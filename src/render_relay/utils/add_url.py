import os

# from render_relay.core.create_app.routes.fastApi import define_routes
from render_relay.core.create_app.routes.fastApi import RouteProcessor


def add_url_rules(app,**kwargs):
    
    api_routes = os.path.join(app.root_path,"api")
    view_routes = app.root_path
    RouteProcessor(app,api_routes,"api")
    RouteProcessor(app,view_routes,"view")

    # define_routes(app,api_routes,"api",debug=kwargs.get("debug",False))

    # define_routes(app,view_routes,"view",debug=kwargs.get("debug",False))
