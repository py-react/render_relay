import os
from fastapi import FastAPI
from render_relay.core.create_app.routes.fastApi import RouteProcessor
from render_relay.utils.get_logger import get_logger

def add_url_rules(app:FastAPI):
    api_routes = os.path.join(app.root_path,"api")
    ws_routes = os.path.join(app.root_path,"app-sockets")
    view_routes = app.root_path
    api_logger = get_logger("API_ROUTES")
    RouteProcessor(app,api_routes,"api",api_logger)
    view_logger = get_logger("VIEW_ROUTES")
    RouteProcessor(app,view_routes,"view",view_logger)
    ws_logger = get_logger("WS_ROUTES")
    RouteProcessor(app,ws_routes,"ws",ws_logger)
