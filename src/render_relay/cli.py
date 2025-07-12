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
    settings = load_settings()
    my_env = os.environ.copy()
    my_env["DEBUG"] = str(settings.get("DEBUG", False))
    my_env["TYPESCRIPT"] = str(settings.get("TYPESCRIPT", False))
    my_env["STATIC_SITE"] = str(settings.get("STATIC_SITE", False))
    node_process = None
    try:
        create_react_app()
    except Exception as e:
        if node_process is not None:
            node_process.kill()


@cli.command()
@click.argument('mode',required=False)
def runserver(mode):
    """Runs the webapp"""
    try:
        my_env = os.environ.copy()  # Copy the current environment
        settings = load_settings()

        if mode == "dev":
            settings["DEBUG"] = True
            click.echo("Building app in in watch mode")
            event_handler = ChangeHandler(my_env)
            observer = Observer()
            observer.schedule(event_handler, path=f".{os.path.sep}src", recursive=True)  # Monitor current directory

            try:
                # Start the initial subprocess and begin watching for changes
                observer.start()
                click.echo("Watching for changes...")
                while True:
                    time.sleep(1)  # Keep the program running to watch for events
            except KeyboardInterrupt:
                click.echo("Exiting...")
                observer.stop()
            finally:
                observer.join()
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
            create_react_app()
            subprocess.run([f"uvicorn","_gingerjs.main:app","--port",settings.get("PORT"),"--host",settings.get("HOST"),"--workers",settings.get("UVICORN_WORKERS","1")], check=True, cwd=get_base(),env=my_env)
        except  Exception as e:
            raise e

    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == '__main__':
    cli()