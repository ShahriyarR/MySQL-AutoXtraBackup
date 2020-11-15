from fastapi import FastAPI
from fastapi.responses import JSONResponse
from backup_backup.backuper import Backup

app = FastAPI()


@app.post("/backup")
async def backup():
    print("Ready to take backup")
    return JSONResponse({"result": "Successfully finished the backup process"})

