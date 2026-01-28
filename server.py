from flask import Flask, redirect, request, send_from_directory, Response, stream_with_context
import subprocess
import sys
from pathlib import Path
import json
import re
import time
import os
import tempfile
APP_DIR = Path(__file__).resolve().parent
GM_DIR = APP_DIR / "gm"
STATE_DIR = GM_DIR / "_state"
LAYOUT_FILE = STATE_DIR / "dashboard_layout.json"
app = Flask(__name__)
OK_RE = re.compile(r"OK:\s*Wrote\s+(?P<path>.+?)\s+with\s+(?P<count>\d+)\s+", re.IGNORECASE)
def run_generator_blocking():
    cmd = [sys.executable, "-u", "-m", "gm.generate_models_html"]
    print("RUN:", " ".join(cmd), "CWD:", str(APP_DIR))
    subprocess.run(cmd, cwd=str(APP_DIR), check=True)
def _step_from_written_path(path_str: str):
    p = path_str.lower().replace("\\", "/")
    if p.endswith("/films.html") or p.endswith("films.html"):
        return "films"
    if p.endswith("/models.html") or p.endswith("models.html"):
        return "models"
    if p.endswith("/studios.html") or p.endswith("studios.html"):
        return "studios"
    if p.endswith("/genres.html") or p.endswith("genres.html"):
        return "genres"
    return None
def _atomic_write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_name = tempfile.mkstemp(prefix="dash_", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp_name, str(path))
    finally:
        try:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
        except Exception:
            pass
def _is_valid_layout(payload) -> bool:
    if payload is None:
        return False
    if isinstance(payload, list):
        if not payload:
            return True
        if all(isinstance(x, str) for x in payload):
            return True
        if all(isinstance(x, dict) for x in payload):
            for r in payload:
                if "cards" not in r:
                    return False
                if not isinstance(r.get("cards"), list):
                    return False
                if not all(isinstance(c, str) for c in r.get("cards", [])):
                    return False
                shape = r.get("shape", "square")
                if shape not in ("square", "rect", "vert"):
                    return False
            return True
    return False
@app.get("/")
def root():
    return redirect("/gm/dashboard.html")
@app.get("/dash/layout")
def dash_get_layout():
    try:
        if not LAYOUT_FILE.exists():
            return Response("", status=204)
        raw = LAYOUT_FILE.read_text(encoding="utf-8").strip()
        if not raw:
            return Response("", status=204)
        return Response(raw, status=200, mimetype="application/json", headers={"Cache-Control": "no-store"})
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype="application/json")
@app.post("/dash/layout")
def dash_save_layout():
    try:
        payload = request.get_json(silent=True)
        if not _is_valid_layout(payload):
            return Response(json.dumps({"ok": False, "error": "Invalid layout payload"}), status=400, mimetype="application/json")
        _atomic_write_json(LAYOUT_FILE, payload)
        return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"ok": False, "error": str(e)}), status=500, mimetype="application/json")
@app.delete("/dash/layout")
def dash_delete_layout():
    try:
        if LAYOUT_FILE.exists():
            LAYOUT_FILE.unlink()
        return Response(json.dumps({"ok": True}), status=200, mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"ok": False, "error": str(e)}), status=500, mimetype="application/json")
@app.post("/refresh")
def refresh():
    try:
        run_generator_blocking()
    except subprocess.CalledProcessError as e:
        return Response(
            "Refresh failed.\n\n"
            f"cmd: {e.cmd}\n"
            f"returncode: {e.returncode}\n"
            f"python: {sys.executable}\n"
            f"cwd: {APP_DIR}\n",
            status=500,
            mimetype="text/plain",
        )
    ref = request.headers.get("Referer") or "/gm/models.html"
    return redirect(ref)
@app.get("/refresh/stream")
def refresh_stream():
    ref = request.args.get("ref") or "/gm/models.html"
    @stream_with_context
    def generate():
        def sse(event, payload):
            return f"event: {event}\n" f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        cmd = [sys.executable, "-u", "-m", "gm.generate_models_html"]
        print("RUN (SSE):", " ".join(cmd), "CWD:", str(APP_DIR))
        yield sse("start", {"ok": True})
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(APP_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            done_steps = set()
            last_ping = time.time()
            def maybe_emit_step_from_line(line_lower: str):
                mapping = [
                    ("films.html", "films"),
                    ("models.html", "models"),
                    ("studios.html", "studios"),
                    ("genres.html", "genres"),
                ]
                for needle, step in mapping:
                    if needle in line_lower and step not in done_steps:
                        done_steps.add(step)
                        return step
                return None
            for line in iter(proc.stdout.readline, ""):
                if not line:
                    break
                line_stripped = line.rstrip("\n")
                line_lower = line_stripped.lower()
                if "ok:" in line_lower and "wrote" in line_lower:
                    step = maybe_emit_step_from_line(line_lower)
                    if step:
                        yield sse("step", {"step": step, "status": "done"})
                now = time.time()
                if now - last_ping > 0.6:
                    last_ping = now
                    yield ": ping\n\n"
            rc = proc.wait()
            if rc != 0:
                yield sse("error", {"message": f"Generator failed (exit code {rc})."})
                return
            for step in ["films", "models", "studios", "genres"]:
                if step not in done_steps:
                    done_steps.add(step)
                    yield sse("step", {"step": step, "status": "done"})
            yield sse("done", {"ok": True, "ref": ref})
        except Exception as e:
            yield sse("error", {"message": str(e)})
    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
@app.get("/gm/<path:filename>")
def gm_files(filename: str):
    return send_from_directory(GM_DIR, filename)
if __name__ == "__main__":
    host = os.environ.get("MODEL_LIST_HOST", "127.0.0.1")
    try:
        port = int(os.environ.get("MODEL_LIST_PORT", "8787"))
    except Exception:
        port = 8787
    app.run(host=host, port=port, debug=False, threaded=True)
