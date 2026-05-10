from os import environ,path,getcwd
import sys
import shutil

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.routing import APIRoute
from fastapi.responses import FileResponse, JSONResponse
import importlib.util
from pathlib import Path
import json

from kiwijs.utils import load_settings
from kiwijs.utils.add_url import add_url_rules
from kiwijs.utils.common import load_module, get_current_dir


def app_context(request):
    return {'app': request.app}

class App(FastAPI):
    def __init__(self,*args, **kwargs):
        super().__init__(**kwargs)
        self._settings = load_settings()
        self.my_env = environ.copy()
        self.template_folder= path.sep.join(["_kiwijs","build","templates"])
        self.root_path= path.join(self._settings.get("CWD", getcwd()),"src","app")
        self.setTemplateEngine()
        self.setStaticPath()
        self.extend_app()
        self.add_url()
        self.generate_openapi_schema()
        # Set up Live Reload WebSocket in debug mode
        if self._settings.get("DEBUG", False) or environ.get("DEBUG", "False") == "True":
            self.setup_livereload()

    def generate_openapi_schema(self):
        if environ.get("KIWIJS_SKIP_OPENAPI_GEN", "False") == "True":
            return
        from kiwijs.utils.build_manager import BuildManager
        bm = BuildManager(app_instance=self)
        bm.generate_openapi()

    def extend_app(self):
        working_dir = self._settings.get("CWD", getcwd())
        app_name = self._settings.get("NAME", "app")
        try:
            app_module_path = path.join(working_dir,app_name,f"main.py")
            if path.exists(app_module_path):
                app_module_present = load_module("kiwijs_user_app", app_module_path)
                if app_module_present and hasattr(app_module_present, "extend_app"):
                    app_module_present.extend_app(self)
        except Exception as e:
            print(f"Error loading extend_app module: {e}")
    
    def add_url(self):
        # Generate Flask routes
        add_url_rules(self)
    
    def setStaticPath(self):
        self.static_url_path='/static'
        self.static_folder=path.sep.join(["_kiwijs","build","static"])
        static_app = FastAPI()

        async def serve_static_file(file_path: str)->FileResponse:
            file_path_full = path.join(getcwd(),self.static_folder, file_path)
            # Check if the file exists
            if not path.isfile(file_path_full):
                raise HTTPException(status_code=404, detail="File not found")
            # Serve the file
            return FileResponse(file_path_full)
        
        route =APIRoute(
            path="/static/{file_path:path}",
            endpoint=serve_static_file,
            methods=["GET"],
            response_class=FileResponse,
            name="static"
        )
        static_app.router.routes.append(route)
        self.mount(self.static_url_path,app=static_app, name="static")
    
    def setTemplateEngine(self):
        self.templateEngine = Jinja2Templates(directory = self.template_folder, context_processors=[app_context])
        self.templateEngine.env.auto_reload = True
        self.templateEngine.env.autoescape = False
        self.TemplateResponse = self.templateEngine.TemplateResponse

    def setup_livereload(self):
        """Set up Live Reload WebSocket endpoint for dev mode."""
        from kiwijs.core.livereload import live_reload_manager

        @self.websocket("/__live_reload")
        async def livereload_ws(websocket: WebSocket):
            await live_reload_manager.connect(websocket)
            try:
                await websocket.send_json({"type": "connected"})
                while True:
                    # Keep connection alive; client doesn't send data
                    await websocket.receive_text()
            except WebSocketDisconnect:
                pass
            finally:
                await live_reload_manager.disconnect(websocket)

        @self.post("/__live_reload_notify")
        async def livereload_notify(request: Request):
            """Internal endpoint: DevChangeHandler POSTs here to trigger browser notifications."""
            try:
                data = await request.json()
                await live_reload_manager.broadcast(data)
                return JSONResponse({"ok": True, "clients": live_reload_manager.client_count})
            except Exception as e:
                return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

        # Copy livereload_client.js to the build static output so it can be served
        livereload_src = path.join(
            get_current_dir(__file__), "..", "..", "utils",
            "react_components", "livereload_client.js"
        )
        livereload_dest_dir = path.join(getcwd(), "_kiwijs", "build", "static", "js")
        livereload_dest = path.join(livereload_dest_dir, "livereload_client.js")
        try:
            Path(livereload_dest_dir).mkdir(parents=True, exist_ok=True)
            shutil.copy2(livereload_src, livereload_dest)
        except Exception as e:
            print(f"Warning: Could not copy Live Reload client: {e}")