import os
import re
import shutil
import subprocess
from typing import Any

from render_relay.utils.delete_pycache import delete_pycache
from render_relay.utils.common import copy_file_if_not_exists, copy_if_not_exists, get_base, get_current_dir
import logging

logger = logging.getLogger(__name__)

class CreateReactAppUtil:
    def __init__(self, paths:list[str],settings:dict[str,Any],my_env:dict[str,Any],debug:bool=False):
        self.paths = paths
        self.debug = debug
        self.settings = settings
        self.cwd = os.getcwd()
        self.env = my_env
        self.file_ext = "tsx"
        self.app_file = f"app.{self.file_ext}"
        self.DEFAULT_LAYOUT = "DefaultLayout_"
        self.PAGE_NOT_FOUND = "GenericNotFound"
        self.DEFAULT_LOADER = "DefaultLoader_"

    def create_nodes(self,components_paths:list[str],nodes:dict[str,str]=None):

        if nodes is None:
            nodes = {}
        
        for component_path in components_paths:
            relative_path = component_path.split("src")[1]
            paths = list(filter(None, relative_path.split(os.path.sep)))  # Remove empty strings from split
            current = nodes
            for i in range(len(paths) - 1):
                key = paths[i]
                current = current.setdefault(key, {})
            current[paths[-1]] = component_path
        return nodes   
    
    def get_error_component_statement(self):
        component_defination_start = f"""
            <{"Error {...props}" if self.debug else ""} >
        """
        component_defination_end = f"""
            </{"Error" if self.debug else ""}>
        """

        return {
            "component_defination_start":component_defination_start,
            "component_defination_end":component_defination_end
        }
    
    def get_src_part_replacer(self):
        if self.settings.get("STATIC_SITE",False):
            return os.path.sep.join(["","src",""])
        return os.path.sep.join(["","_gingerjs","build",""])
    
    def replace_wildcards_in_component_name(self,path):
        # Define the regex pattern to match any text within square brackets
        pattern = re.compile(r"\[([^\]]+)\]")
        # Replace the matching segments with : followed by the captured text
        return pattern.sub(r"_\1_", path)
    
    def replace_wildcards(self,path):
        if path == "/":
            return "*"
        # Define the regex pattern to match any text within square brackets
        pattern = re.compile(r"\[([^\]]+)\]")
        # Replace the matching segments with : followed by the captured text
        return pattern.sub(r":\1", path)
    
    def generate_component_name(self,component_path:str):
        return self.replace_wildcards_in_component_name(
            "_".join(
                part.capitalize() for part in component_path.split("/")[3:]
            ).replace("-", "_").replace(f".{self.file_ext}","")
        )
    
    def get_imports(self,obj:dict):
        imports = []
        src_part_replacer = self.get_src_part_replacer()
        def traverse(node, path):
            nonlocal imports
            if isinstance(node, str):
                component_name = self.generate_component_name(node)
                if f"{os.path.sep}{self.app_file}" not in node:
                    imports.append(f"""
                            //import {component_name} from '{node.replace(os.path.sep.join(["","src",""]), src_part_replacer).replace(f".{self.file_ext}",".js")}'
                            const {component_name} = React.lazy(() => import('{node}'));
                        """)

            else:
                for key in node:
                    traverse(node[key], f'{path}/{key}')

        traverse(obj, "")
        return "\n".join(imports)
    
    def get_react_components(self,compoennt_name:str):
        try:
            with open(os.path.join(get_current_dir(__file__),"react_components",compoennt_name), 'r') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            print(f"Error: File '{compoennt_name}' not found.")
            return None
        except PermissionError:
            print(f"Error: Permission denied when trying to read '{compoennt_name}'.")
            return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def create_routes(self, data, parent_path="/", last_path="", parentLoader="", debug=False):
        routes = []
        parent = parent_path
        loader = self.DEFAULT_LOADER if  parentLoader=="" else parentLoader
        full_parent_path = last_path + "/" + self.replace_wildcards(parent).replace('*','') if self.replace_wildcards(parent) != "*" else last_path  + self.replace_wildcards(parent).replace('*','')
        layout_comp = self.DEFAULT_LAYOUT
        page_not_found = self.PAGE_NOT_FOUND

        layout_file = f"layout.{self.file_ext}"
        page_not_found_file = f"page_not_found.{self.file_ext}"
        loading_file = f"loading.{self.file_ext}"
        index_file = f"index.{self.file_ext}"
        app_file = f"app.{self.file_ext}"

        if layout_file in data:
            layout_comp = self.generate_component_name(data[layout_file])
        elif layout_file not in data and parent_path == "/":
            layout_comp = self.DEFAULT_LAYOUT

        if page_not_found_file in data:
            page_not_found = self.generate_component_name(data[page_not_found_file])

        if loading_file in data:
            loader = self.generate_component_name(data[loading_file])

        if index_file in data:
            routes.append(f"""
                    <Route path="{self.replace_wildcards(parent)}" 
                        element = {{
                            <LayoutPropsProvider key={{"{full_parent_path+"/"}"}} Fallback={{{loader}}} forUrl={{"{full_parent_path+"/"}"}} Element={{{layout_comp}}} {{...props}}/>
                        }}
                    >
            """)
            for key in data:
                route_path = data[index_file].split("app")[1].replace(f"{os.path.sep}{index_file}", "")
                if key not in {index_file, layout_file, app_file, loading_file,page_not_found_file}:
                    routes.extend(self.create_routes(data[key], key, full_parent_path,loader, debug))
                elif key not in {layout_file, app_file, loading_file,page_not_found_file}:
                    component_name = self.generate_component_name(data[index_file])
                    add_path = f'path="{self.replace_wildcards(route_path).replace(f"/{parent}", "")}"'
                    sub_paths = route_path.split("/")
                    routes.append(f'''
                        <Route {"index" if sub_paths[-1] == parent_path or route_path in ["", "/src/"] else add_path}
                            element={{
                                <PropsProvider Element={{{component_name}}} Fallback={{{loader}}} {{...props}} />
                            }}
                        />
                    ''')
            routes.append('</Route>')
            routes.append(f'<Route path="*" element={{<{page_not_found} />}}/>') 
        return routes
    
    def get_app_content(self,):
        node_data= self.create_nodes(self.paths)
        to_return  = [
            "import React, { useState, useEffect,createContext, startTransition, useMemo, Suspense } from 'react';",
            "import { BrowserRouter as Router, Route, Routes, Outlet, useLocation } from 'react-router-dom';",
            "import { Redirect, matchPath } from 'react-router';",
            self.get_imports(node_data),
            self.get_react_components("DefaultLoader.jsx"),
            self.get_react_components("PropsProvider.jsx"),
            self.get_react_components("LayoutPropsProvider.jsx"),
            self.get_react_components("GenericNotFound.jsx"),
            self.get_react_components("Error.jsx"),
            "const DefaultLayout_ = ()=><Outlet/>",
            "const App = (props) => (",
            self.get_error_component_statement().get("component_defination_start"),
            "<Routes>",
            "\n".join(self.create_routes(data=node_data["app"], debug=self.debug)),
            "</Routes>",
            self.get_error_component_statement().get("component_defination_end"),
            ")",
            "export default App",
        ]

        return "\n".join(to_return)

    def get_main_client(self,):
        return self.get_react_components("Main_client.jsx")
    
    def copy_public_static(self,):
        # Construct the source and destination paths
        source_path = os.path.join(get_base(), 'public', 'static')
        destination_path = os.path.join(get_base(), '_gingerjs', 'build', 'static', "assets")

        # Iterate through the source directory
        for root, dirs, files in os.walk(source_path):
            for name in dirs:
                src_dir = os.path.join(root, name)
                dest_dir = os.path.join(destination_path, os.path.relpath(src_dir, source_path))
                copy_if_not_exists(src_dir, dest_dir)
            for name in files:
                src_file = os.path.join(root, name)
                dest_file = os.path.join(destination_path, os.path.relpath(src_file, source_path))
                copy_if_not_exists(src_file, dest_file)

    def initial_steps(self,):
        if self.cwd is None:
            raise ValueError("Current working directory not provided")
        try:
            # Remove the './build' directory
            build_path = os.path.join(self.cwd,"_gingerjs")
            if os.path.exists(build_path):
                shutil.rmtree(build_path)

            # Remove the './public/static/js/app.js' file
            app_js_path = os.path.join(self.cwd, 'public', 'static', 'js', 'app.js')
            if os.path.exists(app_js_path):
                os.remove(app_js_path)
        except subprocess.CalledProcessError:
            pass

        react_components_path = os.path.join(get_current_dir(__file__),"react_components")
        build_path = os.path.join(self.cwd, "_gingerjs", "__build__")

        os.makedirs(os.path.join(self.cwd,"_gingerjs"), exist_ok=True)
        copy_file_if_not_exists(os.path.join(get_current_dir(__file__),"app_boiler_plate","main.py"),os.path.join(get_base(),"_gingerjs","main.py"),shutil.copy) # fastApi app
        with open(os.path.join(self.cwd,"_gingerjs","__init__.py"), 'w') as file:
            pass  # 'pass' is used here to do nothing, effectively creating an empty file

        os.makedirs(build_path, exist_ok=True)

        copy_file_if_not_exists(os.path.join(react_components_path, "BrowserRouterWrapper.jsx"), os.path.join(
            build_path, "BrowserRouterWrapper.jsx"))
        copy_file_if_not_exists(os.path.join(react_components_path, "StaticRouterWrapper.jsx"), os.path.join(
            build_path, "StaticRouterWrapper.jsx"))
        copy_file_if_not_exists(os.path.join(react_components_path, "LayoutPropsProvider.jsx"), os.path.join(
            build_path, "LayoutPropsProvider.jsx"))
        copy_file_if_not_exists(os.path.join(react_components_path, "PropsProvider.jsx"), os.path.join(
            build_path, "PropsProvider.jsx"))
        copy_file_if_not_exists(os.path.join(react_components_path, "GenericNotFound.jsx"), os.path.join(
            build_path, "GenericNotFound.jsx"))
        copy_file_if_not_exists(os.path.join(react_components_path, "DefaultLoader.jsx"), os.path.join(
            build_path, "DefaultLoader.jsx"))

        with open(os.path.join(self.cwd,"_gingerjs", "__build__", "app.jsx"), "w") as file:
            file.write(self.get_app_content())

        with open(os.path.join(self.cwd,"_gingerjs", "__build__", "main.jsx"), "w") as file:
            file.write(self.get_main_client())

        if self.debug:
            copy_file_if_not_exists(os.path.join(react_components_path,"Error.jsx"),os.path.join(build_path, "Error.jsx"))
        
        delete_pycache(self.cwd,[])
        subprocess.run(["yarn" if self.settings.get("PACKAGE_MANAGER") == "yarn" else "npx", "vite","build", "--config",os.path.join(get_current_dir(__file__),"..","core","create_app","vite.node.config.js")], cwd=get_base(), check=True, env=self.env)