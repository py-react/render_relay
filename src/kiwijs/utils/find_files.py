import os
from typing import Any,Optional

# Function to recursively search for JSX files and create a list of absolute paths
def find_jsx_files(directory_path:str,settings:dict[str, Any], jsx_files_list:Optional[list[str]]=None):
    
    if jsx_files_list is None:
        jsx_files_list = []
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            if settings.get("TYPESCRIPT",False):
                if file.endswith(".tsx"):
                    jsx_files_list.append(os.path.join(root, file))
            else:
                if file.endswith(".jsx"):
                    jsx_files_list.append(os.path.join(root, file))
    
    return jsx_files_list