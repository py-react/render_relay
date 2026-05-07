import os
import json
import subprocess
import shutil
from pathlib import Path
from kiwijs.utils import load_settings
from kiwijs.utils.get_logger import get_logger
from kiwijs.utils.common import get_current_dir

class BuildManager:
    def __init__(self, app_instance=None):
        self._logger = get_logger("BuildManager")
        self.settings = load_settings()
        self.app_instance = app_instance
        self.working_dir = self.settings.get("CWD", os.getcwd())

    def _ensure_boilerplate(self):
        """Ensures that the _gingerjs boilerplate and public templates exist in the working directory."""
        ginger_path = os.path.join(self.working_dir, "_gingerjs")
        os.makedirs(ginger_path, exist_ok=True)
        
        # Ensure __init__.py exists
        init_file = os.path.join(ginger_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                pass
            self._logger.info(f"Created {init_file}")

        # Ensure main.py exists
        main_py_dest = os.path.join(ginger_path, "main.py")
        if not os.path.exists(main_py_dest):
            main_py_src = os.path.join(get_current_dir(__file__), "app_boiler_plate", "main.py")
            if os.path.exists(main_py_src):
                shutil.copy(main_py_src, main_py_dest)
                self._logger.info(f"Copied boilerplate main.py to {main_py_dest}")
            else:
                self._logger.error(f"Boilerplate source not found at {main_py_src}")
                return False

        # Ensure public/templates exists
        templates_dest = os.path.join(self.working_dir, "public", "templates")
        if not os.path.exists(templates_dest):
            templates_src = os.path.join(get_current_dir(__file__), "app_boiler_plate", "public", "templates")
            if os.path.exists(templates_src):
                shutil.copytree(templates_src, templates_dest)
                self._logger.info(f"Bootstrapped public/templates from framework boilerplate")
            else:
                self._logger.warning(f"Boilerplate templates source not found at {templates_src}")
        
        return True

    def _ensure_app_instance(self):
        """Ensures that self.app_instance is populated by loading it from the default location."""
        if self.app_instance:
            return True

        # First ensure we have the boilerplate
        if not self._ensure_boilerplate():
            return False

        self._logger.info("Attempting to load app instance from _gingerjs.main...")
        try:
            # Add working directory to sys.path to ensure local imports work
            import sys
            if self.working_dir not in sys.path:
                sys.path.insert(0, self.working_dir)

            from kiwijs.utils.common import load_module
            main_path = os.path.join(self.working_dir, "_gingerjs", "main.py")
            
            if not os.path.exists(main_path):
                self._logger.error(f"App entry point not found at {main_path}")
                return False

            os.environ["RENDER_RELAY_SKIP_OPENAPI_GEN"] = "True"
            module = load_module("gingerjs_main", main_path)
            os.environ["RENDER_RELAY_SKIP_OPENAPI_GEN"] = "False"
            if hasattr(module, 'app'):
                self.app_instance = module.app
                self._logger.info("App instance loaded successfully from _gingerjs.main:app")
                return True
            else:
                self._logger.error("No 'app' instance found in _gingerjs.main")
                return False
        except Exception as e:
            self._logger.error(f"Failed to load app instance: {e}")
            return False

    def generate_openapi(self):
        """Generates openapi.json from the app instance."""
        if not self.app_instance:
            if not self._ensure_app_instance():
                self._logger.error("App instance not provided and could not be loaded for OpenAPI generation.")
                return False

        output_file = os.path.join(self.working_dir, "public", "static", "openapi.json")
        try:
            schema = self.app_instance.openapi()
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(schema, indent=2))
            self._logger.info(f"OpenAPI schema saved to {output_file}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to generate OpenAPI schema: {e}")
            return False

    def generate_ts_client(self):
        """Runs the npm command to generate the TS client from the OpenAPI schema."""
        self._logger.info("Generating TypeScript client...")
        try:
            package_manager = self.settings.get("PACKAGE_MANAGER", "npm")
            cmd = ["yarn" if package_manager == "yarn" else "npm", "run", "generate-client"]
            subprocess.run(cmd, cwd=self.working_dir, check=True)
            self._logger.info("TypeScript client generated successfully.")
            return True
        except subprocess.CalledProcessError as e:
            self._logger.error(f"Failed to generate TypeScript client: {e}")
            return False

    def run_vite_build(self, debug=False):
        """Triggers the Vite build process."""
        from kiwijs.core.create_app.cra import create_react_app
        self._logger.info("Starting Vite build...")

        try:
            # Note: create_react_app currently handles its own vite call.
            create_react_app(debug_override=debug)
            
            if debug:
                # Ensure HMR client is in the build directory AFTER vite starts
                # because vite build clears the outDir.
                hmr_src = os.path.join(
                    get_current_dir(__file__), "..", "utils",
                    "react_components", "hmr_client.js"
                )
                hmr_dest_dir = os.path.join(self.working_dir, "_gingerjs", "build", "static", "js")
                hmr_dest = os.path.join(hmr_dest_dir, "hmr_client.js")
                try:
                    os.makedirs(hmr_dest_dir, exist_ok=True)
                    shutil.copy2(hmr_src, hmr_dest)
                    self._logger.info("Copied HMR client to build directory (Post-build).")
                except Exception as e:
                    self._logger.warning(f"Could not copy HMR client: {e}")

            self._logger.info("Vite build completed.")
            return True
        except Exception as e:
            self._logger.error(f"Vite build failed: {e}")
            return False

    def prepare_all(self, debug=False):
        """Coordinates the full preparation sequence."""
        self._logger.info("Starting full build preparation flow...")
        # 1. Generate OpenAPI (this will also load the app instance if needed)
        if not self.generate_openapi():
            self._logger.error("Step failed: generate_openapi")
            return False
        
        # 2. Generate TS Client
        if not self.generate_ts_client():
            self._logger.error("Step failed: generate_ts_client")
            return False
            
        # 3. Run Vite Build
        return self.run_vite_build(debug=debug)

    def pre_flight(self, debug=False):
        """Pre-flight check: Load app to generate schema, then build client and frontend."""
        self._logger.info("Running pre-flight build check...")
        return self.prepare_all(debug=debug)

    def quick_rebuild(self):
        """Fast rebuild: only run vite builds (skip OpenAPI / TS client generation).
        
        Used by DevChangeHandler for incremental rebuilds on CSS/JS changes.
        """
        self._logger.info("Quick rebuild — Vite only...")
        return self.run_vite_build(debug=True)

    def regenerate_routes_and_rebuild(self):
        """Regenerate app.jsx from the route tree, then do a full Vite rebuild.
        
        Used when route-defining files (index.jsx, layout.jsx, etc.) are 
        created or deleted.
        """
        self._logger.info("Regenerating routes and rebuilding...")
        from kiwijs.core.create_app.cra import create_react_app
        try:
            create_react_app()
            self._logger.info("Route regeneration and rebuild complete.")
            return True
        except Exception as e:
            self._logger.error(f"Route regeneration failed: {e}")
            return False
