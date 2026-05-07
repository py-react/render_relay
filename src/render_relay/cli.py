import os
import subprocess
import time
import click

from render_relay.core.create_app.cra import create_react_app
from render_relay.utils import load_settings, excecution_time
from render_relay.utils.change_handler import ChangeHandler
from render_relay.utils.common import copy_file_if_not_exists, create_dir, create_settings_file, create_ts_js_config, get_base, get_current_dir
import logging

from watchdog.observers import Observer

from render_relay.utils.user_input import main
from render_relay.utils.constant import DEFAULT_LOCKFILE,DEFAULT_SOCK_PATH
logger = logging.getLogger(__name__)
observer = Observer()


@click.group()
def cli():
    pass


@cli.command()
@excecution_time
def create_app():
  """Intial project setup"""
  try:
    if not os.path.exists(os.path.join(get_base(), "package.json")):
        config = main()
        create_settings_file(config, get_base())
        create_app_settigns = config["create_app_settings"]
        settings = load_settings()
        cwd = os.path.join(get_base())
        click.echo("Setting up app")
        copy_file_if_not_exists(os.path.join(get_current_dir(
                __file__), "utils", "app_boiler_plate", "package.json"), os.path.join(cwd, "package.json"))
        if "Tailwind CSS" in create_app_settigns['additional_configs']:
            copy_file_if_not_exists(os.path.join(get_current_dir(
                __file__), "utils", "app_boiler_plate", "tailwind.config.js"), os.path.join(cwd, "tailwind.config.js"))
        if create_app_settigns['use_shadcn']:
            copy_file_if_not_exists(os.path.join(get_current_dir(
                __file__), "utils", "app_boiler_plate", "components.json"), os.path.join(cwd, "components.json"))
        create_ts_js_config(config, os.path.join(
            get_current_dir(__file__), "utils", "app_boiler_plate", "jsconfig.json"))
        copy_file_if_not_exists(os.path.join(get_current_dir(__file__), "utils", "app_boiler_plate", "public"), os.path.join(cwd, "public"), {
                                "not_found.html", "bad_request_exception_template.html", "content.html", "exception_template_debug.html", "internal_server_exception_template.html", "layout.html", "exception_template.html", } if settings.get('STATIC_SITE') else {})
        copy_file_if_not_exists(os.path.join(get_current_dir(__file__), "utils", "app_boiler_plate", "src"), os.path.join(cwd, "src"), {"api", "index.py"} if settings.get(
            'STATIC_SITE') else {}, {".jsx": ".tsx", ".js": ".ts"} if config['create_app_settings']['use_typescript'] else {})
        create_dir(os.path.join(cwd, "public", "static"))
        copy_file_if_not_exists(os.path.join(get_current_dir(__file__), "utils", "app_boiler_plate", "public", "static",
                                "gingerjs_logo.png"), os.path.join(cwd, "public", "static", "gingerjs_logo.png"))
        create_dir(os.path.join(cwd, "src", "components"))
        click.echo("App set up completed")
    else:
        logger.info("Found a exsiting ginger app. Skipping intial setup")
        settings = load_settings()
        cwd = os.path.join(get_base())
    click.echo("Installing packages")
    package_manager = settings.get('PACKAGE_MANAGER')
    subprocess.run(["yarn" if package_manager ==
                   "yarn" else "npm", "install"], cwd=cwd)
    click.echo("Packages installed")
    click.echo("Run your app using : render_relay runserver")
  except subprocess.CalledProcessError as e:
      click.echo(f"Error: {e}", err=True)

@cli.command()
@excecution_time
def build():
    from render_relay.utils.build_manager import BuildManager
    settings = load_settings()
    bm = BuildManager()
    bm.pre_flight(debug=settings.get("DEBUG", False))


@cli.command()
@click.argument('mode',required=False)
def runserver(mode):
    """Runs the webapp"""
    try:
        my_env = os.environ.copy()  # Copy the current environment
        settings = load_settings()

        if mode == "dev":
            settings["DEBUG"] = True
            my_env["DEBUG"] = "True"
            for key, value in settings.items():
                my_env[key] = str(value)

            click.echo("🔥 Starting dev mode with HMR...")

            # 1. Initial build (generate __build__ files + vite build)
            click.echo("Building app...")
            from render_relay.utils.build_manager import BuildManager
            bm = BuildManager()
            bm.pre_flight(debug=True)
            click.echo("Initial build complete.")

            # 2. Process Manager for safe restarts
            import threading

            class DevProcessManager:
                def __init__(self, uvicorn_cmd, node_cmd_args, env, cwd):
                    self.uvicorn_cmd = uvicorn_cmd
                    self.node_cmd_args = node_cmd_args
                    self.env = env
                    self.cwd = cwd
                    self.uvicorn_process = None
                    self.node_process = None
                    self.is_restarting_uvicorn = False
                    self.is_restarting_node = False
                    self.lock = threading.Lock()
                    self.should_exit = False

                def start_node(self):
                    with self.lock:
                        self.is_restarting_node = True
                        if self.node_process:
                            try:
                                self.node_process.terminate()
                                self.node_process.wait(timeout=3)
                            except Exception:
                                self.node_process.kill()
                        
                        socket_path = DEFAULT_SOCK_PATH
                        LOCKFILE = DEFAULT_LOCKFILE
                        try:
                            if os.path.exists(socket_path): os.remove(socket_path)
                            if os.path.exists(LOCKFILE): os.remove(LOCKFILE)
                        except Exception: pass

                        self.node_process = subprocess.Popen(
                            ['node'] + self.node_cmd_args,
                            cwd=self.cwd
                        )
                        with open(LOCKFILE, "w") as f:
                            f.write(str(self.node_process.pid))
                        self.is_restarting_node = False
                        return self.node_process

                def start_uvicorn(self):
                    with self.lock:
                        self.is_restarting_uvicorn = True
                        if self.uvicorn_process:
                            try:
                                self.uvicorn_process.terminate()
                                self.uvicorn_process.wait(timeout=3)
                            except Exception:
                                self.uvicorn_process.kill()

                        self.uvicorn_process = subprocess.Popen(
                            self.uvicorn_cmd, 
                            cwd=self.cwd, 
                            env=self.env
                        )
                        self.is_restarting_uvicorn = False
                        return self.uvicorn_process

                def restart_uvicorn(self):
                    click.echo("🔄 Restarting uvicorn...")
                    self.start_uvicorn()
                    click.echo(f"🔄 Uvicorn restarted (PID {self.uvicorn_process.pid})")

                def restart_node(self):
                    click.echo("🔄 Restarting Node bridge...")
                    self.start_node()
                    click.echo(f"🔄 Node bridge restarted (PID {self.node_process.pid})")

                def restart_all(self):
                    """Restarts both uvicorn and node atomically from the health check perspective."""
                    with self.lock:
                        self.is_restarting_uvicorn = True
                        self.is_restarting_node = True
                    
                    # We call the start methods which handle their own locking and flag clearing
                    self.restart_uvicorn()
                    self.restart_node()

                def is_healthy(self):
                    with self.lock:
                        if self.is_restarting_uvicorn or self.is_restarting_node:
                            return True # If we're in the middle of a restart, it's "healthy" for now
                        
                        uv_dead = self.uvicorn_process and self.uvicorn_process.poll() is not None
                        node_dead = self.node_process and self.node_process.poll() is not None
                        
                        if uv_dead or node_dead:
                            if uv_dead: click.echo("❌ Uvicorn exited unexpectedly.")
                            if node_dead: click.echo("❌ Node bridge exited unexpectedly.")
                            return False
                        return True

                def stop_all(self):
                    self.should_exit = True
                    for proc, name in [(self.uvicorn_process, "uvicorn"), (self.node_process, "node bridge")]:
                        if proc:
                            try:
                                proc.terminate()
                                proc.wait(timeout=3)
                                click.echo(f"  {name} stopped")
                            except Exception:
                                try: proc.kill()
                                except Exception: pass

            node_process_path = os.path.join(get_current_dir(__file__), "core", "bridge", "unix_sock.js")
            node_args = [node_process_path, f"debug=True", f'cwd={os.getcwd()}', f"sock_path={DEFAULT_SOCK_PATH}"]
            uvicorn_cmd = [
                "uvicorn", "_gingerjs.main:app",
                "--port", settings.get("PORT", "8000"),
                "--host", settings.get("HOST", "0.0.0.0"),
            ]

            manager = DevProcessManager(uvicorn_cmd, node_args, my_env, get_base())
            manager.start_node()
            click.echo(f"Node bridge started (PID {manager.node_process.pid})")
            manager.start_uvicorn()
            click.echo(f"Uvicorn started (PID {manager.uvicorn_process.pid})")

            # 4. Start DevChangeHandler for unified watching
            from render_relay.utils.change_handler import DevChangeHandler
            # Use manager.restart_all for Python changes to avoid race conditions
            event_handler = DevChangeHandler(
                my_env, 
                uvicorn_runner=manager.restart_uvicorn, 
                node_runner=manager.restart_node,
                server_runner=manager.restart_all
            )
            observer = Observer()
            observer.schedule(event_handler, path=".", recursive=True)

            try:
                observer.start()
                click.echo("✅ Dev server ready — watching for changes (HMR enabled)")
                click.echo(f"   Open http://{settings.get('HOST', 'localhost')}:{settings.get('PORT', '8000')}")

                while not manager.should_exit:
                    time.sleep(1)
                    if not manager.is_healthy():
                        break
            except KeyboardInterrupt:
                click.echo("\nShutting down dev server...")
            finally:
                observer.stop()
                observer.join()
                manager.stop_all()
                # Clean up lock/socket files
                for f in [DEFAULT_LOCKFILE, DEFAULT_SOCK_PATH]:
                    try: os.remove(f)
                    except Exception: pass
                click.echo("Dev server stopped.")
            return

        
        settings["DEBUG"] = False
        # Define the socket path
        socket_path = DEFAULT_SOCK_PATH
        # Start the Node.js server as a subprocess
        node_process_path = os.path.join(get_current_dir(__file__),"core", "bridge", "unix_sock.js")
        LOCKFILE = DEFAULT_LOCKFILE
        try:
            os.remove(LOCKFILE)
            os.remove(socket_path)
        except Exception as e:
            pass
        node_process = subprocess.Popen(['node', node_process_path,f"debug={os.environ.get('DEBUG','False')}",f'cwd={os.getcwd()}',f"sock_path={socket_path}"])
        with open(LOCKFILE, "w") as f:
            f.write(str(node_process.pid))

        try:
            from render_relay.utils.build_manager import BuildManager
            bm = BuildManager()
            # In runserver, we want to ensure everything is preped before uvicorn starts
            # But generate_openapi needs a running app instance.
            # So we rely on the App() initialization within uvicorn to trigger it.
            # However, Vite Build needs the TS Client. 
            # Proposed: Run a minimal bootstrap to generate schema -> client -> build.
            bm.pre_flight(debug=settings.get("DEBUG", False))
            
            subprocess.run([f"uvicorn","_gingerjs.main:app","--port",settings.get("PORT"),"--host",settings.get("HOST"),"--workers",settings.get("UVICORN_WORKERS","1")], check=True, cwd=get_base(),env=my_env)
        except  Exception as e:
            raise e

    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == '__main__':
    cli()