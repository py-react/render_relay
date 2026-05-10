from fastapi import Request
async def meta_data():
    return {
        "title": "KiwiJs",
    }


async def index(request:Request):
    isDev = "true"
    return {"isdev":isDev}