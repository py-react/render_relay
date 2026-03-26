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

from render_relay.utils import load_settings
from render_relay.utils.add_url import add_url_rules
from render_relay.utils.common import load_module, get_current_dir


def app_context(request):
    return {'app': request.app}

class App(FastAPI):
    def __init__(self,*args, **kwargs):
        super().__init__(**kwargs)
        self._settings = load_settings()
        self.my_env = environ.copy()
        self.template_folder= path.sep.join(["_gingerjs","build","templates"])
        self.root_path= path.join(self._settings.get("CWD", getcwd()),"src","app")
        self.setTemplateEngine()
        self.setStaticPath()
        self.extend_app()
        self.add_url()
        self.generate_openapi_schema()
        # Set up HMR WebSocket in debug mode
        if self._settings.get("DEBUG", False) or environ.get("DEBUG", "False") == "True":
            self.setup_hmr()

    def generate_openapi_schema(self):
        from render_relay.utils.build_manager import BuildManager
        bm = BuildManager(app_instance=self)
        bm.generate_openapi()

    def extend_app(self):
        working_dir = self._settings.get("CWD", getcwd())
        app_name = self._settings.get("NAME", "app")
        try:
            app_module_path = path.join(working_dir,app_name,f"main.py")
            if path.exists(app_module_path):
                app_module_present = load_module("render_relay_user_app", app_module_path)
                if app_module_present and hasattr(app_module_present, "extend_app"):
                    app_module_present.extend_app(self)
        except Exception as e:
            print(f"Error loading extend_app module: {e}")
    
    def add_url(self):
        # Generate Flask routes
        add_url_rules(self)
    
    def setStaticPath(self):
        self.static_url_path='/static'
        self.static_folder=path.sep.join(["_gingerjs","build","static"])
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
        self.templateEngine = Jinja2Templates(directory = self.template_folder,auto_reload=True,autoescape=False, context_processors=[app_context])
        self.TemplateResponse = self.templateEngine.TemplateResponse

    def setup_hmr(self):
        """Set up Hot Module Replacement WebSocket endpoint for dev mode."""
        from render_relay.core.hmr import hmr_manager

        @self.websocket("/__hmr")
        async def hmr_ws(websocket: WebSocket):
            await hmr_manager.connect(websocket)
            try:
                await websocket.send_json({"type": "connected"})
                while True:
                    # Keep connection alive; client doesn't send data
                    await websocket.receive_text()
            except WebSocketDisconnect:
                pass
            finally:
                await hmr_manager.disconnect(websocket)

        @self.post("/__hmr_notify")
        async def hmr_notify(request: Request):
            """Internal endpoint: DevChangeHandler POSTs here to trigger browser notifications."""
            try:
                data = await request.json()
                await hmr_manager.broadcast(data)
                return JSONResponse({"ok": True, "clients": hmr_manager.client_count})
            except Exception as e:
                return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

        # Copy hmr_client.js to the build static output so it can be served
        hmr_src = path.join(
            get_current_dir(__file__), "..", "..", "utils",
            "react_components", "hmr_client.js"
        )
        hmr_dest_dir = path.join(getcwd(), "_gingerjs", "build", "static", "js")
        hmr_dest = path.join(hmr_dest_dir, "hmr_client.js")
        try:
            Path(hmr_dest_dir).mkdir(parents=True, exist_ok=True)
            shutil.copy2(hmr_src, hmr_dest)
        except Exception as e:
            print(f"Warning: Could not copy HMR client: {e}")