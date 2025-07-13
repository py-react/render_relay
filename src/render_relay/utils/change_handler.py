import multiprocessing
import os
import subprocess
from watchdog.events import FileSystemEventHandler

from render_relay.core.create_app.cra import create_react_app
from render_relay.utils import load_settings
from render_relay.utils.app_boiler_plate import settings
from render_relay.utils.common import get_current_dir, get_pids
from render_relay.utils.get_logger import get_logger
from render_relay.utils.constant import DEFAULT_LOCKFILE,DEFAULT_SOCK_PATH
settings = load_settings()

def run_uvicorn():
    # Kill the uvicorn process if running on the same port
    port = int(settings.get("PORT", 5001))
    pid = get_pids(port)
    if len(pid):
        pids = set(get_pids(port))
        command = 'kill -9 {}'.format(' '.join([str(pid) for pid in pids]))
        os.system(command)
    else:
        print(f"No existing uvicorn process found on port {port}")
    
    create_react_app()
    socket_path = DEFAULT_SOCK_PATH
    # Start the Node.js server as a subprocess
    node_process_path = os.path.join(get_current_dir(__file__),"..","core", "bridge", "unix_sock.js")
    LOCKFILE = DEFAULT_LOCKFILE
    try:
        os.remove(LOCKFILE)
        os.remove(socket_path)
    except Exception as e:
        pass
    subprocess.run(["pkill","-f","unix_sock.js"])
    node_process = subprocess.Popen(['node', node_process_path,f"debug={os.environ.get('DEBUG','False')}",f'cwd={os.getcwd()}',f"sock_path={socket_path}"])
    with open(LOCKFILE, "w") as f:
        f.write(str(node_process.pid))
    # Since we don't use subprocess, os.popen gives us a way to capture stdout and stderr.
    subprocess.run([
        "uvicorn", "_gingerjs.main:app",
        "--port", str(port),
        "--host", settings.get("HOST")
    ])

class ChangeHandler(FileSystemEventHandler):
    def __init__(self,my_env):
        self._logger = get_logger("ChangeHandler")
        self.settings = settings
        self.my_env = my_env
        for key, value in self.settings.items():
            self.my_env[key] = str(value)
        # list of all processes, so that they can be killed afterwards 
        self.all_processes = []
        self.start()
    
    def debug_log(self, *args, **kwargs):
        self._logger.debug(*args, **kwargs)

    def on_any_event(self, event):
        # Ignore events in __pycache__ directories
        if any(substring in event.src_path for substring in ["__pycache__","gingerJs_api_client","_gingerjs"])  or event.src_path.endswith(".pyc"):
            return
        if event.is_directory:
            return
        self.debug_log(f"* Detected change in {event.src_path} ,reloading")
        self.start()
        # self.start(event.src_path)

    def start(self):
        """Start the command in a new thread."""
        self.debug_log("Terminating Uvicorn process...")
        for process in self.all_processes:
            process.terminate()

        self._logger.info("Starting new command thread...")
        process = multiprocessing.Process(target=run_uvicorn)
        process.start()
        self.all_processes.append(process)