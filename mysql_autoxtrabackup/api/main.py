from typing import Any
from typing import Dict

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from mysql_autoxtrabackup.api.controller.controller import router

app = FastAPI()


@app.on_event("startup")
async def startup() -> None:
    """startup."""
    print("app started")


@app.on_event("shutdown")
async def shutdown() -> None:
    """shutdown."""
    print("SHUTDOWN")


def modify_openapi() -> Dict[str, Any]:
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


app.openapi = modify_openapi  # type: ignore

app.include_router(router)
