import importlib.util
import os
import urllib.request
import urllib.error
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
BACKEND_PATH = BASE_DIR / "ollama_backend.py"

app = Flask(__name__, static_folder="static", template_folder="static")


def load_backend_module(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Backend file not found: {path}")
    spec = importlib.util.spec_from_file_location("ollama_backend", str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load backend module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


try:
    backend = load_backend_module(BACKEND_PATH)
except Exception as exc:
    backend = None
    backend_load_error = str(exc)
else:
    backend_load_error = None


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "portal.html")


@app.route("/api/status")
def api_status():
    if backend is None:
        return jsonify({"success": False, "message": backend_load_error}), 500
    return jsonify({
        "success": True,
        "model": "Ollama/Gemma4",
        "status": "local-only",
    })


@app.route("/api/ask", methods=["POST"])
def api_ask():
    if backend is None:
        return jsonify({"success": False, "message": backend_load_error}), 500
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"success": False, "message": "Prompt is required."}), 400
    if not hasattr(backend, "call_ai_api"):
        return jsonify({"success": False, "message": "Backend has no call_ai_api function."}), 500
    try:
        if hasattr(backend, "global_state"):
            backend.global_state.offline_mode = True
        answer = backend.call_ai_api(prompt)
        return jsonify({"success": True, "answer": answer})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.route("/api/ask-ollama", methods=["POST"])
def api_ask_ollama():
    if backend is None:
        return jsonify({"success": False, "message": backend_load_error}), 500
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"success": False, "message": "Prompt is required."}), 400
    if not hasattr(backend, "call_ollama_api"):
        return jsonify({"success": False, "message": "Backend has no call_ollama_api function."}), 500
    try:
        answer = backend.call_ollama_api(prompt)
        return jsonify({"success": True, "answer": answer})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/api/ollama-health')
def ollama_health():
    """Simple health check for a local Ollama API (Gemma4).

    Attempts to GET the models endpoint and returns reachable status.
    """
    url = 'http://localhost:11434/v1/models'
    try:
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=2) as resp:
            # If we get a 2xx response assume Ollama is up
            code = getattr(resp, 'status', None) or getattr(resp, 'getcode', lambda: None)()
            return jsonify({"success": True, "message": "Ollama reachable", "code": code})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
