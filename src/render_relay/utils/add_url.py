import os

from render_relay.core.create_app.routes.fastApi import define_routes

def add_url_rules(app,**kwargs):
    api_routes = os.path.join(app.root_path,"api")
    define_routes(app,api_routes,"api",debug=kwargs.get("debug",False))

    view_routes = app.root_path
    define_routes(app,view_routes,"view",debug=kwargs.get("debug",False))
