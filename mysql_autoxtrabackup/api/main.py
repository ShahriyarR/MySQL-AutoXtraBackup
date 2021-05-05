from typing import Any, Dict, Optional

import uvicorn  # type: ignore
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from mysql_autoxtrabackup.api.controller.controller import router
from mysql_autoxtrabackup.utils.version import VERSION

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
        version=f"{VERSION}",
        description="Rest API doc for MySQL-AutoXtrabackup",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = modify_openapi  # type: ignore

app.include_router(router)


def run_server(host: Optional[str] = None, port: Optional[int] = None) -> None:
    host = host or "127.0.0.1"
    port = port or 5555
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
