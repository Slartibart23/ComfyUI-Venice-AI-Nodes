"""
Minimal Venice AI API client (standard library only).

The API key is looked up in this order:
  1. the node's api_key widget (not recommended, it is saved inside workflows)
  2. the VENICE_API_KEY environment variable
  3. Venice_AI_API.txt in the ComfyUI folder (or the portable root above it)
"""

import json
import os
import urllib.error
import urllib.request

BASE_URL = "https://api.venice.ai/api/v1"
KEY_FILE = "Venice_AI_API.txt"
ENV_KEY = "VENICE_API_KEY"
LOG = "[Venice AI]"
USER_AGENT = "ComfyUI-Venice-AI-Nodes"


class VeniceError(RuntimeError):
    pass


# --------------------------------------------------------------------------- #
# API key
# --------------------------------------------------------------------------- #
def comfy_root() -> str:
    try:
        import folder_paths
        return folder_paths.base_path
    except Exception:
        # outside ComfyUI (tools, tests): <ComfyUI>/custom_nodes/<pack>/venice_ai
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def key_file_candidates() -> list:
    root = comfy_root()
    return [os.path.join(root, KEY_FILE), os.path.join(os.path.dirname(root), KEY_FILE)]


def _read_key_file(path: str) -> str:
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # also accept "VENICE_API_KEY=..." (.env style)
            if "=" in line and line.split("=", 1)[0].strip().upper() == ENV_KEY:
                line = line.split("=", 1)[1].strip().strip('"').strip("'")
            return line
    return ""


def resolve_api_key(widget_value: str = "") -> str:
    if widget_value and widget_value.strip():
        return widget_value.strip()
    env = os.environ.get(ENV_KEY, "").strip()
    if env:
        return env
    for path in key_file_candidates():
        if os.path.isfile(path):
            key = _read_key_file(path)
            if key:
                return key
    raise VeniceError(
        f"{LOG} No Venice API key found. Put your key into {key_file_candidates()[0]} "
        f"(only the key, one line), or set the {ENV_KEY} environment variable.")


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
class Response:
    def __init__(self, status: int, headers, body: bytes):
        self.status = status
        self.headers = {k.lower(): v for k, v in headers.items()}
        self.body = body

    @property
    def content_type(self) -> str:
        return self.headers.get("content-type", "").split(";")[0].strip().lower()

    def json(self):
        return json.loads(self.body.decode("utf-8"))


def _error_message(status: int, body: bytes) -> str:
    try:
        data = json.loads(body.decode("utf-8"))
    except Exception:
        data = {}
    err = data.get("error")
    if isinstance(err, dict):
        code, text = err.get("code", ""), err.get("message", "")
    else:
        code, text = "", err or body[:300].decode("utf-8", "replace")
    issues = data.get("issues") or []
    if issues:
        text += " | " + "; ".join(
            f"{'.'.join(str(p) for p in i.get('path', []))}: {i.get('message', '')}" for i in issues)

    hints = {
        401: "API key invalid, or this model needs a Venice Pro account.",
        402: "Not enough Venice balance. Top up at venice.ai.",
        403: "Model not available in your region, or the key is IP-restricted.",
        409: "This model needs consent first (Seedance: switch seedance_consent on).",
        413: "Request too large. Use smaller input images/videos.",
        422: "Prompt or media rejected by the content policy of Venice or the model provider.",
        429: "Rate limit reached. Wait a moment and try again.",
    }
    hint = hints.get(status, "")
    if code == "needs_consent":
        hint = hints[409]
    return f"{LOG} HTTP {status}: {text}" + (f"\n{hint}" if hint else "")


def request(method: str, path: str, payload=None, api_key: str = "", timeout: float = 120,
            accept: str = "application/json") -> Response:
    url = path if path.startswith("http") else BASE_URL + path
    data = None
    headers = {"User-Agent": USER_AGENT, "Accept": accept}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return Response(r.status, r.headers, r.read())
    except urllib.error.HTTPError as e:
        raise VeniceError(_error_message(e.code, e.read())) from None
    except urllib.error.URLError as e:
        raise VeniceError(f"{LOG} Venice API not reachable: {e.reason}") from None


def post_json(path: str, payload: dict, api_key: str = "", timeout: float = 120):
    return request("POST", path, payload, api_key, timeout).json()


def get_json(path: str, timeout: float = 60):
    return request("GET", path, timeout=timeout).json()


def download(url: str, target: str, timeout: float = 600) -> None:
    """Download a pre-signed URL (no auth header) to target."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r, open(target, "wb") as f:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
    except urllib.error.HTTPError as e:
        raise VeniceError(f"{LOG} Download failed: HTTP {e.code}") from None
