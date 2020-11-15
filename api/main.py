from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from backup_backup.backuper import Backup

app = FastAPI()


@app.post("/backup", status_code=201)
async def backup(response: Response):
    backup_ = Backup()
    result = backup_.all_backup()
    if result:
        return JSONResponse({"result": "Successfully finished the backup process"})
    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return JSONResponse({"result": "[FAILED] to take backup"})