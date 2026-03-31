import re
from collections import defaultdict
import os
import importlib.util
from render_relay.utils import load_settings
from .api import api
from .view import view
from .ws import ws
from .exception_view import exception
from .not_found import not_found
from .middleware import Create_Middleware_Class
from .layout_view import Create_Layout_Middleware_Class
from fastapi.routing import APIRoute, APIWebSocketRoute
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from render_relay.utils.constant import level_map
import logging

class RouteProcessor:
    def __init__(self,app:FastAPI,root_folder:str,route_type:str,logger:logging.Logger):
        self._logger = logger
        self.app = app
        self.root_folder = root_folder
        self.route_type = route_type
        self.settings = load_settings()
        self.app.add_exception_handler(404,not_found(self.app))
        self.app.add_exception_handler(StarletteHTTPException,exception(self.app))
        self.routes_tree = []
        self.debug = self.settings.get("DEBUG",False)
        self.debug_level = self.settings.get("DEBUG_LEVEL","INFO")
        self.define_route()

    def define_route(self,):
        for dirpath, _, filenames in os.walk(self.root_folder):
            # Now your main logic becomes much cleaner:
            if self.route_type == "api":
                # Process all directories for API routes
                if "index.py" in filenames:
                    self.process_route_file(dirpath, "index.py")
            elif self.route_type == "ws":
                if "index.py" in filenames:
                    self.process_route_file(dirpath, "index.py")
            elif self.route_type == "view":
                if "/api/" not in dirpath and "/app-sockets/" not in dirpath:
                    if self.settings.get("STATIC_SITE", False) and "index.py" not in filenames:
                        # Handle static site generation without index.py
                        relative_path = os.path.relpath(os.path.join(dirpath), self.root_folder)
                        url_rule = '/' + os.path.dirname(relative_path).replace(os.sep, '/')
                        url_rule = url_rule.replace('[', '{').replace(']', '}')
                        if url_rule == '/.':
                            url_rule = '/'
                        
                        route = APIRoute(
                            path=url_rule,
                            endpoint=view(None, self.app, True),
                            methods=["GET"],
                            response_class=HTMLResponse,
                        )
                        self.app.router.routes.append(route)
                        self.routes_tree.append(f"Route '{url_rule}' attached it using default in {dirpath}")
                    else:
                        if "index.py" in filenames:
                            self.process_route_file(dirpath, "index.py")
                            
        self.debug_mode()

    def debug_log(self, *a, **kwa):
        msg = " ".join(str(x) for x in a)
        self._logger.debug(f"{msg}", **kwa)

    def process_ws_route(self,module, url_rule, dirpath):
        """Process ws route logic"""

        if hasattr(module, 'index'):
            # Define your dynamic WebSocket route
            route = APIWebSocketRoute(
                path=f"/ws{url_rule}",
                endpoint=ws(module.index),
                name=""
            )
            self.app.router.routes.append(route)
            self.routes_tree.append(f"WS route '/ws{url_rule if url_rule == "/" else f"{url_rule}/"}' attached it using index.py in {dirpath}")

    def process_view_route(self,module, url_rule, dirpath, relative_path):
        """Process view route logic"""
        # Handle layout
        if hasattr(module, 'layout'):
            layout_middleware_class = Create_Layout_Middleware_Class(module.layout, f"{url_rule if url_rule == "/" else f"{url_rule}/"}")
            self.app.add_middleware(layout_middleware_class)
            self.routes_tree.append(f"layout attached on route '{url_rule}' attached it using layout.py in {dirpath}")
        
        # Handle middleware
        if hasattr(module, 'middleware'):
            
            view_middleware_class = Create_Middleware_Class(module.middleware, f"{url_rule if url_rule == "/" else f"{url_rule}/"}", "view")
            self.app.add_middleware(view_middleware_class)
            self.routes_tree.append(f"Middleware attached on route '{url_rule if url_rule == "/" else f"{url_rule}/"}' attached it using middleware.py in {dirpath}")
        
        
        # Handle view function
        if hasattr(module, 'index'):
            self.routes_tree.append(f"Route '{url_rule}' attached it using index.py in {dirpath}")
            route = APIRoute(
                path=url_rule,
                name="",
                endpoint=view(module, self.app),
                methods=["GET"],
                response_class=HTMLResponse,
            )
            self.app.router.routes.append(route)
        else:
            self._logger.warn(f"No 'view_func' found in {relative_path}")

    def process_api_route(self,module, url_rule, dirpath):
        """Process API route logic"""
        dependencies = []
        
        # Handle middleware
        if hasattr(module, 'middleware'):
            self.api_middleware_class = Create_Middleware_Class(module.middleware, f"/api{url_rule if url_rule == "/" else f"{url_rule}/"}", "api")
            self.app.add_middleware(self.api_middleware_class)
            self.routes_tree.append(f"Middleware attached on api '/api{url_rule if url_rule == "/" else f"{url_rule}/"}' attached it using middleware.py in {dirpath}")
        
        # Add HTTP method routes
        methods = ["GET", "POST", "PUT", "DELETE","PATCH","OPTIONS","HEAD"]
        for method in methods:
            if hasattr(module, method):
                route = APIRoute(
                    path=f"/api{url_rule}",
                    name="",
                    endpoint=api(getattr(module, method)),
                    methods=[method],
                    response_class=JSONResponse,
                    dependencies=dependencies
                )
                self.app.router.routes.append(route)
        
        self.routes_tree.append(f"API route '/api{url_rule}' attached it using index.py in {dirpath}")

    def process_route_file(self,dirpath, filename):
        """Process a single route file and add it to the app"""
        # Common logic for both API and view routes
        relative_path = os.path.relpath(os.path.join(dirpath, filename), self.root_folder)
        url_rule = '/' + os.path.dirname(relative_path).replace(os.sep, '/')
        url_rule = url_rule.replace('[', '{').replace(']', '}')
        
        if url_rule == '/.':  # Root index.py
            url_rule = '/'
        
        # Dynamic import of the module
        module_name = relative_path.replace(os.sep, '.')[:-3]  # Convert path to module name
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(dirpath, filename))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if self.route_type == "api":
            self.process_api_route(module, url_rule, dirpath)
        elif self.route_type == "ws":
            self.process_ws_route(module, url_rule, dirpath)
        else:  # route_type == "view"
            self.process_view_route(module, url_rule, dirpath, relative_path)

    def debug_mode(self,):
        if self.debug:
            # Define regex patterns to match routes and actions
            route_pattern = re.compile(r"Route '(.*?)' attached it using (.*?) in")
            no_middleware_pattern = re.compile(r"No 'middleware' found for '(.*?)' attach it by adding middleware.py in")
            middleware_pattern = re.compile(r"Middleware attached on route '(.*?)' attached it using middleware.py")
            layout_pattern = re.compile(r"layout attached on route '(.*?)' attached it using layout.py")

            api_pattern = re.compile(r"API route '(.*?)' attached")
            no_api_middleware_pattern = re.compile(r"No 'middleware' found for api '(.*?)' attach it by adding middleware.py in")
            api_middleware_pattern = re.compile(r"Middleware attached on api '(.*?)' attached it using middleware.py")

            ws_pattern = re.compile(r"WS route '(.*?)' attached it using index.py in")

            # Parse the log entries to extract routes and their actions
            routes = defaultdict(list)

            for line in self.routes_tree:
                route_match = route_pattern.search(line)
                no_middleware_match = no_middleware_pattern.search(line)
                middleware_match = middleware_pattern.search(line)
                layout_match = layout_pattern.search(line)

                api_match = api_pattern.search(line)
                no_api_middleware_match = no_api_middleware_pattern.search(line)
                api_middleware_match = api_middleware_pattern.search(line)

                ws_match = ws_pattern.search(line)
                
                if route_match:
                    route, action = route_match.groups()
                    routes[route].append(f"Page {action}")
                elif no_middleware_match:
                    route = no_middleware_match.group(1)
                    routes[route].append("No 'middleware' found")
                elif middleware_match:
                    route = middleware_match.group(1)
                    routes[route].append("Middleware attached on this route and subroutes")
                elif layout_match:
                    route = layout_match.group(1)
                    routes[route].append("Layout attached using layout.py")
                elif api_match:
                    route = api_match.group(1)
                    routes[route].append("Api Endpoint")
                elif no_api_middleware_match:
                    route = no_api_middleware_match.group(1)
                    routes[route].append("No 'middleware' found")
                elif api_middleware_match:
                    route = api_middleware_match.group(1)
                    routes[route].append("middleware.py")
                elif ws_match:
                    route = ws_match.group(1)
                    routes[route].append("WS Endpoint")
                
            # Function to print the tree structure with color for terminal
            def print_tree(routes, route_type):
                # ANSI colors
                COLOR_RESET = "\033[0m"
                COLOR_ROUTE = "\033[1;36m"
                COLOR_API = "\033[1;34m"
                COLOR_WS = "\033[1;32m"
                COLOR_MIDDLEWARE = "\033[0;33m"
                COLOR_LAYOUT = "\033[0;35m"
                COLOR_PAGE = "\033[0;32m"
                COLOR_OTHER = "\033[0;37m"
                COLOR_NONE = "\033[0;31m"

                def classify(action):
                    if "Api Endpoint" in action:
                        return f"{COLOR_API}API{COLOR_RESET}"
                    elif "WS Endpoint" in action:
                        return f"{COLOR_WS}WebSocket{COLOR_RESET}"
                    elif "Middleware" in action:
                        return f"{COLOR_MIDDLEWARE}Middleware{COLOR_RESET}"
                    elif "Layout" in action:
                        return f"{COLOR_LAYOUT}Layout{COLOR_RESET}"
                    elif "Page" in action:
                        return f"{COLOR_PAGE}Page{COLOR_RESET}"
                    elif "No 'middleware'" in action:
                        return f"{COLOR_NONE}None{COLOR_RESET}"
                    return f"{COLOR_OTHER}Other{COLOR_RESET}"

                # Flatten rows
                rows = []
                for route, actions in sorted(routes.items()):
                    for action in actions:
                        rows.append([
                            f"{COLOR_ROUTE}{route}{COLOR_RESET}",
                            classify(action),
                            action
                        ])

                headers = ["Route", "Type", "Details"]

                # Calculate column widths (strip ANSI for length)
                import re
                ansi_escape = re.compile(r'\x1b\[[0-9;]*m')

                def visible_len(s):
                    return len(ansi_escape.sub('', s))

                col_widths = [
                    max(visible_len(row[i]) for row in rows + [headers])
                    for i in range(len(headers))
                ]

                def format_row(row):
                    return "│ " + " │ ".join(
                        f"{cell}{' ' * (col_widths[i] - visible_len(cell))}"
                        for i, cell in enumerate(row)
                    ) + " │"

                def separator(left, mid, right):
                    return left + mid.join("─" * (w + 2) for w in col_widths) + right

                # Print table
                print(separator("┌", "┬", "┐"))
                print(format_row(headers))
                print(separator("├", "┼", "┤"))

                for row in rows:
                    print(format_row(row))

                print(separator("└", "┴", "┘"))

            # Print the tree structure
            self._logger.debug("")
            self._logger.debug(f"R̲o̲u̲t̲e: {self.route_type}")
            self._logger.debug("")
            print_tree(routes,self.route_type) 



