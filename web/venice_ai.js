// Venice AI · Image / Image Edit / Video:
// - narrows duration / resolution / aspect ratio / quality to what the selected
//   model offers (constraints from /venice_ai/catalog)
// - maps a saved model label with an outdated price to the current label (same model ID)
// - shows a fact sheet of the selected model (capabilities, inputs, price, removal date)
//   and, after a run, the run info (price, settings, notes) above it
// - filters for the model list (type, audio input, combining images, uncensored)

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
  const all = w?._veniceAllModels ?? w?.options.values;
  if (!w || all.includes(w.value)) return;
  const id = modelId(w.value);
  const match = all.find((v) => modelId(v) === id);
  if (match) w.value = match;
}

// ------------------------------------------------------------------ filters
// Narrow the model list. Browser only: stored in node.properties (saved with the
// workflow), never sent with the prompt, so changing a filter never re-runs a node.
const ALL_TYPES = "all types";
const TYPES = { "text → video": "T2V", "image → video": "I2V", "reference → video": "R2V", "video → video": "V2V" };
const FILTERS = {
  video: [
    { key: "type", label: "filter: type", combo: [ALL_TYPES, ...Object.keys(TYPES)], def: ALL_TYPES },
    { key: "audioInput", label: "filter: takes audio input", def: false },
    { key: "uncensored", label: "filter: uncensored only", def: false },
  ],
  edit: [
    { key: "combine", label: "filter: combines several images", def: false },
    { key: "uncensored", label: "filter: uncensored only", def: false },
  ],
  image: [{ key: "uncensored", label: "filter: uncensored only", def: false }],
};

function passes(kind, cat, label, f) {
  const c = cat[kind]?.[modelId(label)];
  if (!c) return true;
  if (f.uncensored && !label.includes("UNCENSORED")) return false;
  if (kind === "video") {
    if (f.type && f.type !== ALL_TYPES && c.kind !== TYPES[f.type]) return false;
    if (f.audioInput && !c.audio_input) return false;
  }
  if (kind === "edit" && f.combine && !c.combineImages) return false;
  return true;
}

async function applyFilter(node, kind, userChange) {
  const cat = await loadCatalog();
  const w = widget(node, "model");
  if (!w) return;
  w._veniceAllModels ??= [...w.options.values];
  const f = node.properties?.veniceFilter || {};
  let list = w._veniceAllModels.filter((label) => passes(kind, cat, label, f));
  if (!list.length) list = [...w._veniceAllModels]; // nothing matches: show everything
  if (!list.includes(w.value)) {
    if (userChange) w.value = list[0];
    else list = [w.value, ...list]; // a loaded workflow keeps its model visible
  }
  w.options.values = list;
  if (userChange) await applyConstraints(node, kind);
  node.setDirtyCanvas?.(true, true);
}

function addFilterWidgets(node, kind) {
  node.properties ??= {};
  node.properties.veniceFilter ??= {};
  const created = FILTERS[kind].map((spec) => {
    const value = node.properties.veniceFilter[spec.key] ?? spec.def;
    const cb = (v) => {
      node.properties.veniceFilter[spec.key] = v;
      applyFilter(node, kind, true);
    };
    const w = spec.combo
      ? node.addWidget("combo", spec.label, value, cb, { values: spec.combo, serialize: false })
      : node.addWidget("toggle", spec.label, value, cb, { on: "yes", off: "no", serialize: false });
    w.serialize = false;
    w.options.serialize = false;
    w._veniceFilterKey = spec.key;
    return w;
  });
  // show the filters right above the model list
  for (const w of created) node.widgets.splice(node.widgets.indexOf(w), 1);
  node.widgets.splice(node.widgets.indexOf(widget(node, "model")), 0, ...created);
}

function syncFilterWidgets(node) {
  const f = node.properties?.veniceFilter || {};
  for (const w of node.widgets || []) {
    if (w._veniceFilterKey && f[w._veniceFilterKey] !== undefined) w.value = f[w._veniceFilterKey];
  }
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
        w._veniceAllModels = [...w.options.values];
        const cb = w.callback;
        w.callback = function () {
          const res = cb?.apply(this, arguments);
          applyConstraints(node, kind);
          return res;
        };
        addFilterWidgets(node, kind);
      }
      applyFilter(node, kind, false).then(() => applyConstraints(node, kind));
      return r;
    };

    const onConfigure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const r = onConfigure?.apply(this, arguments);
      syncFilterWidgets(this);
      fixModelLabel(this);
      applyFilter(this, kind, false).then(() => applyConstraints(this, kind));
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
