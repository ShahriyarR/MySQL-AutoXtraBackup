# General helpers file for adding all sort of simple helper functions.
# Trying to use here type hints as well.

import logging
import os
import subprocess
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

logger = logging.getLogger(__name__)


def get_folder_size(path: str) -> Union[str, None]:
    """
    Function to calculate given folder size. Using 'du' command here.
    :param path: The full path to be calculated
    :return: String with human readable size info, for eg, 5.3M
    """
    du_cmd = "du -hs {}".format(path)
    status, output = subprocess.getstatusoutput(du_cmd)
    if status == 0:
        return output.split()[0]
    else:
        logger.error("Failed to get the folder size")
    return None


def sorted_ls(path: Optional[str]) -> List[str]:
    """
    Function for sorting given path
    :param path: Directory path
    :return: The list of sorted directories
    """
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime  # type: ignore
    return list(sorted(os.listdir(path), key=mtime))


def get_directory_size(path: str) -> int:
    """
    Calculate total size of given directory path
    :param path: Directory path
    :return: Total size of directory
    """
    # I am not sure why we have 2 separate functions for same thing but,
    # I assume it is there on purpose
    total_size = 0
    for dir_path, dir_names, file_names in os.walk(path):
        for f in file_names:
            fp = os.path.join(dir_path, f)
            total_size += os.path.getsize(fp)
    return total_size


def create_backup_directory(directory: str) -> str:
    """
    Function for creating timestamped directory on given path
    :param directory: Directory path
    :return: Created new directory path
    """
    new_dir = os.path.join(directory, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    try:
        # Creating directory
        os.makedirs(new_dir)
        return new_dir
    except Exception as err:
        logger.error(
            "Something went wrong in create_backup_directory(): {}".format(err)
        )
        raise RuntimeError(
            "Something went wrong in create_backup_directory(): {}".format(err)
        )


def get_latest_dir_name(path: Optional[str]) -> Optional[str]:
    # Return last backup dir name either incremental or full backup dir
    if len(os.listdir(path)) > 0:
        return max(os.listdir(path))
    return None


def create_directory(path: str) -> Optional[bool]:
    logger.info("Creating given directory...")
    try:
        os.makedirs(path)
        logger.info("OK: Created")
        return True
    except Exception as err:
        logger.error("FAILED: Could not create directory, ", err)
        raise RuntimeError("FAILED: Could not create directory")


def check_if_backup_prepared(type_: str, path: str) -> str:
    """
    Helper function for checking if given backup already prepared or not.
    :param type_: Type of backup full or inc
    :param path: path string of the backup folder
    :return: True if given backup is prepared, False otherwise
    """
    if type_ == "full" and os.path.isfile(path + "/xtrabackup_checkpoints"):
        with open(path + "/xtrabackup_checkpoints", "r") as f:
            if f.readline().split()[-1] == "full-prepared":
                return "Full-Prepared"
    # TODO: add the possible way of checking for incremental backups as well.
    return "Not-Prepared"


def list_available_backups(path: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Helper function for returning
    Dict of backups;
    and the statuses - if they are already prepared or not
    :param path: General backup directory path
    :return: dictionary of backups full and incremental
    """
    backups = {}
    full_backup_dir = path + "/full"
    inc_backup_dir = path + "/inc"
    if os.path.isdir(full_backup_dir):
        backups = {
            "full": [
                {dir_: check_if_backup_prepared("full", full_backup_dir + f"/{dir_}")}
            ]
            for dir_ in os.listdir(full_backup_dir)
        }
    if os.path.isdir(inc_backup_dir):
        backups["inc"] = sorted_ls(inc_backup_dir)  # type: ignore
    logger.info(
        "Listing all available backups from full and incremental backup directories..."
    )
    return backups
