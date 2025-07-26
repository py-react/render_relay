import os
from os import path
from contextlib import asynccontextmanager
from fastapi import FastAPI
import subprocess
import psutil

from render_relay.core.app import App
from render_relay.utils import load_settings
from render_relay.utils.constant import DEFAULT_LOCKFILE
from render_relay.utils.get_logger import get_logger

import importlib.util


def load_module(module_name,module_path):
    try:
        module_name = module_name
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        raise e

LOCKFILE = DEFAULT_LOCKFILE

@asynccontextmanager
async def lifespan(app: FastAPI):
    startLogger = get_logger("AppLifespan: Start")
    settings = load_settings()
    subprocess.run(["yarn" if settings.get("package_manager","npm") == "yarn" else "npm","run","generate-client"])
    working_dir = settings["CWD"]
    app_name = settings["NAME"]
    try:
        startup_module = load_module("startup",path.join(working_dir,app_name,f"main.py"))
        if startup_module:
            await startup_module.startup(app)
    except Exception as e:
        startLogger.error(f"Attaching startup module failed: {e}")
        pass
    startLogger.info("Client Generated")
    yield
    stopLogger = get_logger("AppLifespan: Cleanup")
    if os.path.exists(LOCKFILE):
        try:
            with open(LOCKFILE) as f:
                pid = int(f.read())
                try:
                    process = psutil.Process(pid)
                    if process.is_running():
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            process.kill()
                except psutil.NoSuchProcess:
                    # Process has already terminated, which is fine
                    pass
                except Exception as e:
                    # Log any other process-related errors but don't fail shutdown
                    stopLogger.error(f"Warning: Error during process cleanup: {e}")
        except (ValueError, FileNotFoundError) as e:
            # Handle invalid PID in lockfile or file read errors
            stopLogger.error(f"Warning: Error reading lockfile: {e}")
        finally:
            # Always clean up the lockfile
            if os.path.exists(LOCKFILE):
                os.remove(LOCKFILE)
    try:
        shutdown_module = load_module("shutdown",path.join(working_dir,app_name,f"main.py"))
        if shutdown_module:
            await shutdown_module.shutdown(app)
    except Exception as e:
        stopLogger.error(f"Attaching shutdown module failed: {e}")
        pass
    # Clean up and release the resources
    pass

app = App(__name__,lifespan=lifespan)