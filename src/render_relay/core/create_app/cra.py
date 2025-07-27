

import os
import shutil
import subprocess
from render_relay.utils import load_settings
from render_relay.utils.common import get_base, get_current_dir
from render_relay.utils.create_app import CreateReactAppUtil
from render_relay.utils.find_files import find_jsx_files


settings = load_settings()
package_manager = settings.get('PACKAGE_MANAGER')
debug = settings.get("DEBUG") or False

def create_react_app():
    my_env = os.environ.copy()
    for key, value in settings.items():
        my_env[key] = str(value)
    my_env["STATIC_SITE"] = str(settings.get("STATIC_SITE",False))
    cwd = os.getcwd()
    app_files = find_jsx_files(
        directory_path= os.path.join(cwd, "src", "app"),
        settings=settings,
    )
    createReactAppUtil = CreateReactAppUtil(paths=app_files,settings=settings,my_env=my_env,debug=debug)
    createReactAppUtil.initial_steps()
    if (not settings.get("STATIC_SITE",False)):
        for dirpath, _, filenames in os.walk(os.path.join(get_base(),"public","templates")):
            for filename in filenames:
                if filename != "layout.html" and filename!="index.html" and filename!="static_site.html":
                    # Construct the source and destination paths
                    source_path = os.path.join(get_base(), 'public', 'templates', filename)
                    destination_path = os.path.join(get_base(),"_gingerjs", 'build', 'templates', filename)

                    # Create the destination directory if it does not exist
                    os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                    # Copy the file
                    shutil.copyfile(source_path, destination_path)
    
    subprocess.run(["yarn" if package_manager == "yarn" else "npx", "vite", "build", "--config",get_current_dir(__file__)+os.sep+"vite.config.js",], cwd=get_base(), check=True, env=my_env)

    os.makedirs(os.path.join(get_base(),"public","static"),exist_ok=True)
    
    if not debug:
        # Use built-in Python functions instead of subprocess
        __build_path = os.path.join(cwd, "_gingerjs", "__build__")
        if os.path.exists(__build_path):
            shutil.rmtree(__build_path)
