import os
import sys

from os import path
from contextlib import asynccontextmanager
from fastapi import FastAPI
import subprocess
import psutil

from kiwijs.core.app import App
from kiwijs.utils import load_settings
from kiwijs.utils.common import load_module
from kiwijs.utils.constant import DEFAULT_LOCKFILE
from kiwijs.utils.get_logger import get_logger

LOCKFILE = DEFAULT_LOCKFILE

@asynccontextmanager
async def lifespan(app: FastAPI):
    startLogger = get_logger("AppLifespan: Start")
    settings = load_settings()
    working_dir = settings["CWD"]
    app_name = settings["NAME"]
    
    app_module_path = path.join(working_dir, app_name, f"main.py")
    user_app_module = None
    
    # Load user module once
    try:
        if path.exists(app_module_path):
            user_app_module = load_module("kiwijs_user_app", app_module_path)
    except Exception as e:
        startLogger.error(f"Failed to load user app module: {e}")

    # Startup
    if user_app_module and hasattr(user_app_module, "startup"):
        try:
            await user_app_module.startup(app)
        except Exception as e:
            startLogger.error(f"Error during startup: {e}")
            
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
                    pass
                except Exception as e:
                    stopLogger.error(f"Warning: Error during process cleanup: {e}")
        except (ValueError, FileNotFoundError) as e:
            stopLogger.error(f"Warning: Error reading lockfile: {e}")
        finally:
            if os.path.exists(LOCKFILE):
                os.remove(LOCKFILE)

    # Shutdown
    if user_app_module and hasattr(user_app_module, "shutdown"):
        try:
            await user_app_module.shutdown(app)
        except Exception as e:
            stopLogger.error(f"Error during shutdown: {e}")


app = App(__name__,lifespan=lifespan)