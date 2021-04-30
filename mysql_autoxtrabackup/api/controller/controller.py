from fastapi import APIRouter
from fastapi import status
from fastapi.responses import JSONResponse

from mysql_autoxtrabackup.backup_backup.backuper import Backup
from mysql_autoxtrabackup.backup_prepare.prepare import Prepare
from mysql_autoxtrabackup.utils.helpers import list_available_backups

router = APIRouter()


@router.post(
    "/backup",
    tags=["MySQL-AutoXtrabackup"],
    response_description="Json response ",
    description="Run all backup process",
)
async def backup() -> JSONResponse:
    backup_ = Backup()
    result = backup_.all_backup()
    if result:
        return JSONResponse(
            content={"result": "Successfully finished the backup process"},
            status_code=status.HTTP_201_CREATED,
        )
    return JSONResponse(
        content={"result": "[FAILED] to take backup"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@router.post(
    "/prepare",
    tags=["MySQL-AutoXtrabackup"],
    response_description="Json response",
    description="Prepare all backups",
)
async def prepare() -> JSONResponse:
    prepare_ = Prepare()
    result = prepare_.prepare_inc_full_backups()
    if result:
        return JSONResponse(
            content={"result": "Successfully prepared all the backups"},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        content={"result": "[FAILED] to prepare backup"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@router.get(
    "/backups",
    tags=["MySQL-AutoXtrabackup"],
    response_description="Json response",
    description="List all available backups",
)
async def backups() -> JSONResponse:
    backup_ = Backup()
    result = list_available_backups(
        str(backup_.builder_obj.backup_options.get("backup_dir"))
    )
    if result:
        return JSONResponse(content={"backups": result}, status_code=status.HTTP_200_OK)
    return JSONResponse(content={"backups": {}}, status_code=status.HTTP_200_OK)


@router.delete(
    "/delete",
    tags=["MySQL-AutoXtrabackup"],
    response_description="Json response",
    description="Remove all available backups",
)
async def delete() -> JSONResponse:
    backup_ = Backup()
    delete_full = backup_.clean_full_backup_dir(remove_all=True)
    delete_inc = backup_.clean_inc_backup_dir()
    if delete_full and delete_inc:
        return JSONResponse(
            content={"result": "There is no backups or backups removed successfully"},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        content={"result": "[FAILED] to remove/delete available backups"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
