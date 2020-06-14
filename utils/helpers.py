# General helpers file for adding all sort of simple helper functions.
# Trying to use here type hints as well.

import subprocess
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


def get_folder_size(path: str) -> str:
    """
    Function to calculate given folder size. Using 'du' command here.
    :param path: The full path to be calculated
    :return: String with human readable size info, for eg, 5.3M
    """
    du_cmd = 'du -hs {}'.format(path)
    status, output = subprocess.getstatusoutput(du_cmd)
    if status == 0:
        return output.split()[0]
    else:
        logger.error("Failed to get the folder size")


def sorted_ls(path: str) -> list:
    """
    Function for sorting given path
    :param path: Directory path
    :return: The list of sorted directories
    """
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
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
    new_dir = os.path.join(directory, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    try:
        # Creating directory
        os.makedirs(new_dir)
        return new_dir
    except Exception as err:
        logger.error("Something went wrong in create_backup_directory(): {}".format(err))
        raise RuntimeError("Something went wrong in create_backup_directory(): {}".format(err))


def get_latest_dir_name(path: str) -> str:
    # Return last backup dir name either incremental or full backup dir
    if len(os.listdir(path)) > 0:
        return max(os.listdir(path))

