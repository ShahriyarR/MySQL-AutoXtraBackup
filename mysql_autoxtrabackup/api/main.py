from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from api.controller.controller import router


app = FastAPI()


@app.on_event("startup")
async def startup():
    """startup."""
    print("app started")


@app.on_event("shutdown")
async def shutdown():
    """shutdown."""
    print("SHUTDOWN")


def modify_openapi():
    """modify_openapi."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="MySQL-AutoXtrabackup",
        version="2.0",
        description="Rest API doc for MySQL-AutoXtrabackup",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = modify_openapi

app.include_router(router)

