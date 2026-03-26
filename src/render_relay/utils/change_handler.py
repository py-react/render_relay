import os
import subprocess
import sys
import time
import signal
import threading
from watchdog.events import FileSystemEventHandler

from render_relay.utils import load_settings
from render_relay.utils.common import get_current_dir, get_pids
from render_relay.utils.get_logger import get_logger
from render_relay.utils.constant import DEFAULT_LOCKFILE, DEFAULT_SOCK_PATH

settings = load_settings()

def run_uvicorn():
    """Logic to run the app. This will be called in a separate process."""
    # This function is now used as a standalone entry point if needed,
    # but ChangeHandler will mostly use subprocess.Popen now.
    pass

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, my_env):
        self._logger = get_logger("ChangeHandler")
        self.settings = settings
        self.my_env = my_env
        for key, value in self.settings.items():
            self.my_env[key] = str(value)
        
        # Track the active subprocess
        self.current_process = None
        self.start_app()
    
    def on_any_event(self, event):
        # Ignore list (case-insensitive substrings)
        ignore_list = [
            "__pycache__", 
            "render_relay_api_client", 
            "gingerjs_api_client", 
            "_gingerjs", 
            "node_modules", 
            "env",
            "venv",
            ".venv",
            ".git", 
            ".DS_Store",
            "public/static",
            ".tmp",
            ".swp",
            ".pyc",
            "openapi.json"
        ]
        
        path = str(event.src_path)
        if any(ignore.lower() in path.lower() for ignore in ignore_list):
            return
            
        if event.is_directory:
            return
            
        self._logger.info(f"Change detected in: {path}")
        self.debounce_restart()

    def debounce_restart(self):
        """Starts the process with a small delay to debounce multiple events."""
        if hasattr(self, '_timer') and self._timer.is_alive():
            self._timer.cancel()
        
        self._timer = threading.Timer(1.0, self.start_app) # 1 second debounce
        self._timer.start()

    def start_app(self):
        """Restarts the application using subprocess.Popen with a new process group."""
        self._logger.info("Restarting application...")
        
        # 1. Kill existing process group
        self.stop()
        
        # 2. Start the app using 'render_relay runserver'
        self._logger.info("Starting new process...")
        
        cmd = [sys.executable, "-m", "render_relay.cli", "runserver"]
        
        # Use start_new_session=True to create a new process group
        # This makes it easier to kill the whole group (including uvicorn/node spawned by runserver)
        self.current_process = subprocess.Popen(
            cmd,
            env=self.my_env,
            cwd=os.getcwd(),
            start_new_session=True 
        )
        self._logger.info(f"Application started with PID {self.current_process.pid}")

    def stop(self):
        """Explicitly stops the managed application process and its children."""
        if self.current_process:
            try:
                # Kill the entire process group
                pgid = os.getpgid(self.current_process.pid)
                self._logger.debug(f"Terminating process group {pgid}")
                os.killpg(pgid, signal.SIGKILL)
                self.current_process.wait(timeout=2)
            except (ProcessLookupError, subprocess.TimeoutExpired, Exception) as e:
                self._logger.debug(f"Stop error: {e}")
            finally:
                self.current_process = None


# ---------------------------------------------------------------------------
# DevChangeHandler — HMR-aware file watcher for dev mode
# ---------------------------------------------------------------------------

# File extensions that are frontend assets
_CSS_EXTENSIONS = {".css", ".scss", ".less"}
_JS_EXTENSIONS = {".jsx", ".tsx", ".js", ".ts"}
_PYTHON_EXTENSIONS = {".py"}
# Files whose creation/deletion changes the route tree
_ROUTE_FILES = {"index.jsx", "index.tsx", "layout.jsx", "layout.tsx",
                "loading.jsx", "loading.tsx", "page_not_found.jsx", "page_not_found.tsx"}


class DevChangeHandler(FileSystemEventHandler):
    """HMR-aware file watcher for dev mode.

    Consolidates both frontend (HMR) and backend (restart) watching.
    This replaces the need for uvicorn's own --reload, preventing 
    conflicting restarts.

    * CSS edit          → quick Vite rebuild → WS ``css_update``
    * JS/JSX/TSX edit   → quick Vite rebuild → WS ``js_update``
    * Route-structure   → regenerate app.jsx + full rebuild → WS ``full_reload``
    * Python edit       → restart uvicorn process
    """

    def __init__(self, my_env, uvicorn_runner=None, node_runner=None):
        self._logger = get_logger("DevChangeHandler")
        self.settings = settings
        self.my_env = my_env
        for key, value in self.settings.items():
            self.my_env[key] = str(value)
        self._timer = None
        self._pending_change_type = None
        self._lock = threading.Lock()
        self._uvicorn_runner = uvicorn_runner # Callback to restart uvicorn
        self._node_runner = node_runner # Callback to restart Node bridge

    # ---- watchdog callbacks ------------------------------------------------


    def on_any_event(self, event):
        ignore_list = [
            "__pycache__", "render_relay_api_client", "gingerjs_api_client",
            "_gingerjs", "node_modules", "env", "venv", ".venv", ".git", ".DS_Store",
            "public/static", ".tmp", ".swp", ".pyc", "openapi.json"
        ]

        path = str(event.src_path)
        if any(ign.lower() in path.lower() for ign in ignore_list):
            return
        if event.is_directory:
            return

        change_type = self._classify(path, event)
        if change_type is None:
            return

        self._logger.info(f"[HMR] {change_type} — {path}")
        self._schedule(change_type)

    # ---- helpers -----------------------------------------------------------

    def _classify(self, path, event):
        """Return one of 'css', 'js', 'route_structure', 'python', or None."""
        _, ext = os.path.splitext(path)
        ext = ext.lower()

        # Route structure: creation or deletion of route-defining files
        basename = os.path.basename(path)
        if basename in _ROUTE_FILES and event.event_type in ("created", "deleted", "moved"):
            return "route_structure"

        if ext == ".py":
            return "python"
        if ext in _CSS_EXTENSIONS:
            return "css"
        if ext in _JS_EXTENSIONS:
            return "js"

        return None

    def _schedule(self, change_type):
        """Debounce: collapse rapid changes into a single action."""
        with self._lock:
            # Escalate change type for the pending batch
            # priority: python > route_structure > js > css
            priority = {"css": 0, "js": 1, "route_structure": 2, "python": 3}
            if self._pending_change_type is None or priority.get(change_type, 0) > priority.get(self._pending_change_type, 0):
                self._pending_change_type = change_type

            if self._timer and self._timer.is_alive():
                self._timer.cancel()

            self._timer = threading.Timer(0.5, self._handle_change)
            self._timer.start()

    def _handle_change(self):
        """Execute the appropriate action for the change type."""
        with self._lock:
            change_type = self._pending_change_type
            self._pending_change_type = None

        if change_type is None:
            return

        try:
            if change_type == "python":
                self._on_python_change()
            elif change_type == "route_structure":
                self._on_route_structure_change()
            elif change_type == "js":
                self._on_js_change()
            elif change_type == "css":
                self._on_css_change()
        except Exception as e:
            self._logger.error(f"[HMR] Error handling {change_type} change: {e}")

    # ---- change handlers ---------------------------------------------------

    def _on_python_change(self):
        """Python file edited — restart the server."""
        self._logger.info("[HMR] Python change — restarting server...")
        if self._uvicorn_runner:
            self._uvicorn_runner()
        if self._node_runner:
            self._node_runner()

    def _on_css_change(self):
        """CSS file edited — quick rebuild then hot-swap."""
        self._logger.info("[HMR] CSS change — rebuilding...")
        self._quick_rebuild()
        if self._node_runner:
            self._node_runner()
        self._notify_browser({"type": "css_update"})

    def _on_js_change(self):
        """JS/JSX/TSX file edited — quick rebuild then fast-reload."""
        self._logger.info("[HMR] JS change — rebuilding...")
        self._quick_rebuild()
        if self._node_runner:
            self._node_runner()
        self._notify_browser({"type": "js_update"})

    def _on_route_structure_change(self):
        """Route files created/deleted — regenerate routes, full rebuild, full reload."""
        self._logger.info("[HMR] Route structure change — regenerating app.jsx and rebuilding...")
        self._regenerate_and_rebuild()
        if self._node_runner:
            self._node_runner()
        self._notify_browser({"type": "full_reload"})


    # ---- build helpers -----------------------------------------------------

    def _quick_rebuild(self):
        """Run only the Vite client + SSR builds (skip OpenAPI / TS client)."""
        from render_relay.utils.build_manager import BuildManager
        bm = BuildManager()
        bm.quick_rebuild()

    def _regenerate_and_rebuild(self):
        """Regenerate app.jsx from route tree, then do a full build."""
        from render_relay.utils.build_manager import BuildManager
        bm = BuildManager()
        bm.regenerate_routes_and_rebuild()

    def _notify_browser(self, message):
        """Send change notification to the FastAPI process via HTTP POST.
        
        The FastAPI process (which owns the WebSocket connections) will then
        broadcast the message to all connected browsers.
        """
        import urllib.request
        import json

        host = self.settings.get("HOST", "127.0.0.1")
        if host == "0.0.0.0":
            host = "127.0.0.1"
        port = self.settings.get("PORT", "8000")
        url = f"http://{host}:{port}/__hmr_notify"

        try:
            data = json.dumps(message).encode("utf-8")
            req = urllib.request.Request(
                url, data=data, headers={'Content-Type': 'application/json'}
            )
            # Use a short timeout to avoid blocking if the server is restarting
            with urllib.request.urlopen(req, timeout=1) as response:
                pass
        except Exception as e:
            # Server might be restarting
            self._logger.debug(f"[HMR] Could not notify server: {e}")