from fastapi.responses import Response

from render_relay.core.ssr import SSROperation

def not_found(app):
    def view_func(request,*args,**kwargs):
        if request.url.path.endswith(".ico") or request.url.path.endswith(".js.map") or request.url.path.endswith(".js") or request.url.path.endswith(".css"):
            return Response(status_code=404)
        props = {}
        props["location"] = {}
        props['location']["path"] = request.url.path
        props['location']['query'] = request.url.query
        ssr_ops = SSROperation()
        toRender = ssr_ops.render(props)
        meta = {
            "title": request.url.path+"?"+request.url.query
        }
        return app.TemplateResponse(name="content.html",request=request,context={"react_context":toRender,"react_props":props,"meta_info":meta,"not_found":True},status_code=404)

    return view_func