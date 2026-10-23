// Venice AI · Image / Image Edit / Video:
// - narrows duration / resolution / aspect ratio / quality to what the selected
//   model offers (constraints from /venice_ai/catalog)
// - maps a saved model label with an outdated price to the current label (same model ID)
// - shows a fact sheet of the selected model (capabilities, inputs, price, removal date)
//   and, after a run, the run info (price, settings, notes) above it

const { app } = window.comfyAPI.app;
const { api } = window.comfyAPI.api;

const NODES = { VeniceAI_Image: "image", VeniceAI_ImageEdit: "edit", VeniceAI_Video: "video" };
const SEP = " · ";
const INFO_MIN_HEIGHT = 170; // px, room for the model fact sheet (~9 lines)

let catalogPromise = null;
function loadCatalog() {
  if (!catalogPromise) {
    catalogPromise = api
      .fetchApi("/venice_ai/catalog")
      .then((r) => r.json())
      .catch((e) => {
        console.warn("[Venice AI] catalog not available:", e);
        catalogPromise = null;
        return { image: {}, video: {} };
      });
  }
  return catalogPromise;
}

const modelId = (label) => String(label ?? "").split(SEP).pop().replace("★", "").trim();
const seconds = (d) => (/^\d+s$/.test(d) ? parseInt(d, 10) : 0);
const height = (r) => {
  const s = String(r).toLowerCase();
  if (s === "2k") return 1440;
  if (s === "4k") return 2160;
  const m = s.match(/(\d+)p/);
  return m ? parseInt(m[1], 10) : 0;
};

function widget(node, name) {
  return node.widgets?.find((w) => w.name === name);
}

// Restrict a combo to `values` (null = all original values) and keep the
// current value if allowed, else the nearest one.
function restrict(node, name, values, measure) {
  const w = widget(node, name);
  if (!w) return;
  w._veniceAll ??= [...w.options.values];
  const list = values && values.length ? values : w._veniceAll;
  w.options.values = list;
  if (!list.includes(w.value)) {
    const caseMatch = list.find((v) => String(v).toLowerCase() === String(w.value).toLowerCase());
    let next = caseMatch ?? list[0];
    if (!caseMatch && measure && measure(w.value)) {
      const numeric = list.filter((v) => measure(v));
      if (numeric.length) {
        next = numeric.reduce((a, b) =>
          Math.abs(measure(b) - measure(w.value)) < Math.abs(measure(a) - measure(w.value)) ? b : a);
      }
    }
    w.value = next;
  }
}

function fixModelLabel(node) {
  const w = widget(node, "model");
  if (!w || w.options.values.includes(w.value)) return;
  const id = modelId(w.value);
  const match = w.options.values.find((v) => modelId(v) === id);
  if (match) w.value = match;
}

async function applyConstraints(node, kind) {
  const cat = await loadCatalog();
  const id = modelId(widget(node, "model")?.value);
  const c = cat[kind]?.[id];
  if (!c) return;
  if (kind === "video") {
    restrict(node, "duration", c.durations, seconds);
    restrict(node, "resolution", c.resolutions, height);
    const ars = (c.aspect_ratios || []).filter((a) => a !== "auto");
    restrict(node, "aspect_ratio", ["auto", ...ars]);
  } else {
    const ratios = (c.aspectRatios || []).filter((a) => a !== "auto");
    // image models without fixed ratios take width/height: all ratios + custom stay available
    restrict(node, "aspect_ratio", ratios.length ? ["auto", ...ratios] : kind === "edit" ? ["auto"] : null);
    restrict(node, "resolution", ["auto", ...(c.resolutions || [])]);
    restrict(node, "quality", ["auto", ...(c.qualities || [])]);
  }
  showModelInfo(node, kind, cat, id);
}

// Fact sheet of the selected model; after a run the run info comes first.
function showModelInfo(node, kind, cat, id) {
  if (node._veniceRunModel && node._veniceRunModel !== id) node._veniceRunText = null;
  const profile = cat.profiles?.[kind]?.[id] || "";
  const run = node._veniceRunText;
  showInfo(node, run ? `${run}\n\n— Model —\n${profile}` : profile);
}

function showInfo(node, text) {
  let w = widget(node, "venice_info");
  if (!w) {
    const { ComfyWidgets } = window.comfyAPI.widgets;
    w = ComfyWidgets.STRING(node, "venice_info", ["STRING", { multiline: true }], app).widget;
    // Neither saved in the workflow nor sent with the prompt: a changed input
    // would make ComfyUI re-run (and re-bill) the node instead of using its cache.
    w.serialize = false;
    w.options = { ...(w.options || {}), serialize: false, getMinHeight: () => INFO_MIN_HEIGHT };
    if (w.inputEl) {
      w.inputEl.readOnly = true;
      w.inputEl.style.opacity = 0.8;
    }
    // grow the node to the box's minimum (max, not add: no growth on every reload)
    const min = node.computeSize();
    node.setSize([Math.max(node.size[0], min[0], 380), Math.max(node.size[1], min[1])]);
  }
  w.value = text;
  node.setDirtyCanvas?.(true, true);
}

app.registerExtension({
  name: "VeniceAI.ModelConstraints",

  async beforeRegisterNodeDef(nodeType, nodeData) {
    const kind = NODES[nodeData?.name];
    if (!kind) return;

    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = onNodeCreated?.apply(this, arguments);
      const node = this;
      const w = widget(node, "model");
      if (w) {
        const cb = w.callback;
        w.callback = function () {
          const res = cb?.apply(this, arguments);
          applyConstraints(node, kind);
          return res;
        };
      }
      applyConstraints(node, kind);
      return r;
    };

    const onConfigure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const r = onConfigure?.apply(this, arguments);
      fixModelLabel(this);
      applyConstraints(this, kind);
      return r;
    };

    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (message) {
      const r = onExecuted?.apply(this, arguments);
      const text = message?.text;
      if (text) {
        this._veniceRunText = Array.isArray(text) ? text.join("\n") : String(text);
        this._veniceRunModel = modelId(widget(this, "model")?.value);
        loadCatalog().then((cat) => showModelInfo(this, kind, cat, this._veniceRunModel));
      }
      return r;
    };
  },
});
