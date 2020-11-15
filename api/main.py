from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from backup_backup.backuper import Backup
from backup_prepare.prepare import Prepare


app = FastAPI()


@app.post("/backup")
async def backup() -> JSONResponse:
    backup_ = Backup()
    result = backup_.all_backup()
    if result:
        return JSONResponse(content={"result": "Successfully finished the backup process"},
                            status_code=status.HTTP_201_CREATED)
    return JSONResponse(content={"result": "[FAILED] to take backup"},
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/prepare")
async def prepare() -> JSONResponse:
    prepare_ = Prepare()
    result = prepare_.prepare_inc_full_backups()
    if result:
        return JSONResponse(content={"result": "Successfully prepared all the backups"},
                            status_code=status.HTTP_200_OK)
    return JSONResponse(content={"result": "[FAILED] to prepare backup"},
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
