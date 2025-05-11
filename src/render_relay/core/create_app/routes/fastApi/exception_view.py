import os
import traceback
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from starlette.exceptions import HTTPException as StarletteHTTPException

from render_relay.utils import load_settings


settings = load_settings()

class BadRequest(StarletteHTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=HTTP_400_BAD_REQUEST, detail=detail)

class InternalServerError(StarletteHTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class UnicornException(StarletteHTTPException):
    pass 


def exception(app):
    def handle_exception(request,e):
        # return PlainTextResponse(str(e.detail), status_code=e.status_code)
        # handles all the exception except 404
        msg = e.detail
        errorName = str(e.status_code)
        try:
            findString = f"{e.name}:"
            msgStartsOn = str(e).index(findString)
            msg = str(e)[len(findString)+msgStartsOn:]
            errorName = str(e.name)
        except Exception as err:
            pass

        tb_str = ''.join(traceback.format_tb(e.__traceback__))
        response = {
            "error": errorName + ":" + msg,
            "exception_type": errorName,
            "traceback": tb_str
        }
        print(response["error"])
        print(f"Traceback: {response['traceback']}")
        meta = {
            "title": request.url.path+"?"+request.url.query
        }
        if settings.get("DEBUG") or False:
            return app.TemplateResponse(name="exception_template_debug.html",context={"request": request,"error":True,"meta_info":meta,"msg":{response["error"]},"stack":response['traceback'],"name":{response['exception_type']}},status_code=e.status_code)
        else:
            if isinstance(e, BadRequest):
                return app.TemplateResponse(name="bad_request_exception_template.html",context={"request": request,"error":True,"meta_info":meta},status_code=e.status_code)
            if isinstance(e, InternalServerError):
                return app.TemplateResponse(name="internal_server_exception_template.html",context={"request": request,"error":True,"meta_info":meta},status_code=e.status_code)
            return app.TemplateResponse(name="exception_template.html",context={"request": request,"error":True,"msg":msg,"name":errorName,"meta_info":meta})
    return handle_exception