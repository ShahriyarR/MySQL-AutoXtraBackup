from fastapi import FastAPI
from fastapi.responses import JSONResponse
from backup_backup.backuper import Backup

app = FastAPI()


@app.post("/backup")
async def backup():
    backup_ = Backup()
    result = backup_.all_backup()
    if result:
        return JSONResponse({"result": "Successfully finished the backup process"})
    return JSONResponse({"result": "[FAILED] to take backup"})

