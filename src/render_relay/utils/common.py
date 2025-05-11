
import os
import importlib.util
import signal
import psutil
import subprocess
import logging
import re
import shutil
import json

logger = logging.getLogger(__name__)

def load_module(module_name,module_path):
    try:
        module_name = module_name
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        raise e

def kill_process(process):
    try:
        process.send_signal(signal.SIGTERM)
    except psutil.NoSuchProcess:
        pass

def get_pids(port):
    returnItems = []
    command = "lsof -i :%s | awk '{print $2}'" % port
    pids = subprocess.check_output(command, shell=True)
    pids = pids.strip()
    if pids:
        pids = re.sub(' +', ' ', pids.decode("utf-8"))
        for pid in pids.split('\n'):
            try:
                returnItems.append(int(pid)) 
            except:
                pass
    return returnItems

def run_command(cmd, env=None, cwd=None):
    logger.debug(f"Running command: {cmd}")
    process = subprocess.Popen(cmd, shell=True, env=env, cwd=cwd)
    process.wait()

def task_wrapper(func, name, *args, **kwargs):
    logger.debug(f"Starting task: {name}")
    return func(*args, **kwargs)


def get_base():
    return os.path.join(os.getcwd())

def get_current_dir(file):
    return os.path.dirname(os.path.abspath(file))

def create_dir(directory):
    # Ensure the directory exists
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except Exception as e:
        # show error
        logger.error(e)

def create_and_write_file(directory, filename, content):
    # Ensure the directory exists
    try:
        create_dir(directory)
        # Full file path
        file_path = os.path.join(directory, filename)
        # Create and write to the file
        with open(file_path, 'w') as file:
            file.write(content)
    except Exception as e:
        # show error
        logger.error(e)

def copy_with_exceptions(src, dst, exclude=None,file_extension_mapping={}):
    if not os.path.exists(os.path.dirname(dst)):
        os.makedirs(os.path.dirname(dst))
    
    # Get the list of items in the source directory
    if not os.path.isdir(src):
        # Change the extension if the file extension is in the mapping
        src_ext = os.path.splitext(src)[1]
        if src_ext in file_extension_mapping:
            dst = os.path.splitext(dst)[0] + file_extension_mapping[src_ext]
        shutil.copy(src, dst)
        return
    
    items = os.listdir(src)
    
    # Precompute the set of items to ignore
    ignore_items = {name for name in items if name in exclude} if exclude else set()
    
    for item in items:
        if item in ignore_items:
            continue
        
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        
        if os.path.isdir(s):
            copy_with_exceptions(s, d,exclude,file_extension_mapping)
        else:
            item_ext = os.path.splitext(item)[1]
            if item_ext in file_extension_mapping:
                d = os.path.splitext(d)[0] + file_extension_mapping[item_ext]
            if not os.path.exists(os.path.dirname(d)):
                os.makedirs(os.path.dirname(d))
            shutil.copy(s, d)

def copy_file_if_not_exists(src, dst,exclude=None,file_extension_mapping={}):
    if os.path.exists(dst):
        logger.debug(f"The file {src} already exists. Operation skipped.")
    else:
        if os.path.exists(src):
            copy_with_exceptions(src, dst,exclude,file_extension_mapping)
            logger.debug(f"Copied {src} to {dst}.")
        else:
            logger.debug(f"The file {src} doesn't exists. Operation skipped.")
            raise f"The file {src} doesn't exists"
        
# Function to copy files and directories only if they don't exist at the destination
def copy_if_not_exists(src, dest):
    if not os.path.exists(dest):
        if os.path.isdir(src):
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)


def create_settings_file(config,base):
    config_content = f"""import os

NAME="{config["project_settings"]['project_name']}"
VERSION="{config["project_settings"]['version']}"
PACKAGE_MANAGER="{config["project_settings"]['package_manager']}"
DEBUG={config["project_settings"]['debug']}
PORT="{config["project_settings"]['port']}"
HOST="{config["project_settings"]['host']}"
PYTHONDONTWRITEBYTECODE="{config["project_settings"]['PYTHONDONTWRITEBYTECODE']}"
CWD={config["project_settings"]['CWD']}
STATIC_SITE={config["project_settings"]['static_site']}
TYPESCRIPT={config["project_settings"]["use_typescript"]}
TAILWIND={True if "Tailwind CSS" in config["create_app_settings"]['additional_configs']else False}
"""

    with open(os.path.join(get_base(),"settings.py"), "w") as file:
        file.write(config_content)
    logger.info("\nConfiguration file 'config.py' created successfully.")


def create_ts_js_config(config,config_json_path):
    with open(config_json_path, "r") as file:
        config_json = json.load(file)
    tsconfig = False
    include = config_json.get("include",["**/*.jsx", "**/*.js"])
    if config["create_app_settings"]["use_typescript"]:
        tsconfig = True
        include = ["**/*.tsx", "**/*.ts"]
    config_json["include"] = include

    with open(os.path.join(get_base(),f'{"tsconfig" if tsconfig else "jsconfig"}.json'), "w") as file:
        json.dump(config_json, file, indent=2)
    logger.info("\nCreated",f'{"tsconfig" if tsconfig else "jsconfig"}.json')