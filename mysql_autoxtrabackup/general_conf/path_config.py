# This file is simply place holder for default config file path, which is used in many places.
# If you decide to change the default config path then please edit this file and reinstall tool.
from os.path import expanduser
from os.path import join

home: str = expanduser("~")
config_path: str = join(home, ".autoxtrabackup")
config_path_file: str = join(config_path, "autoxtrabackup.cnf")
log_file_path: str = join(config_path, "autoxtrabackup.log")
