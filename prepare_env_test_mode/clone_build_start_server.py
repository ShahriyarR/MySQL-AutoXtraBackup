from prepare_env_test_mode.test_check_env import TestModeConfCheck
from general_conf.generalops import GeneralClass
import subprocess
import os
import logging
logger = logging.getLogger(__name__)


class CloneBuildStartServer:
    """
    Class for cloning from git, building server from source and starting test server
    """
    def __init__(self):
        self.git_cmd = GeneralClass().gitcmd

        # Creating needed path here
        t_obj = TestModeConfCheck()
        if t_obj.check_test_path(t_obj.testpath):
            self.testpath = t_obj.testpath

    def clone_percona_qa(self):
        # Clone percona-qa repo for using existing bash scripts
        clone_cmd = "git clone https://github.com/Percona-QA/percona-qa.git {}/percona-qa"
        if not os.path.exists("{}/percona-qa".format(self.testpath)):
            status, output = subprocess.getstatusoutput(clone_cmd.format(self.testpath))
            if status == 0:
                logger.debug("percona-qa ready to use")
                return True
            else:
                logger.error("Cloning percona-qa repo failed")
                logger.error(output)
                return False
        else:
            return True


    def clone_ps_server_from_conf(self):
        # Clone PS server[the value coming from config file]
        clone_cmd = "git clone {} {}/PS-5.7-trunk"
        if not os.path.exists("{}/PS-5.7-trunk"):
            status, output = subprocess.getstatusoutput(clone_cmd.format(self.git_cmd, self.testpath))
            if status == 0:
                logger.debug("PS cloned ready to build")
                return True
            else:
                logger.error("Cloning PS failed")
                logger.error(output)
                return False
        else:
            return True

    def build_server(self):
        # Building server from source
        # For this purpose; I am going to use build_5.x_debug.sh script from percona-qa
        saved_path = os.getcwd()
        # Specify here the cloned PS path; for me it is PS-5.7-trunk(which I have hard coded in method above)
        new_path = "{}/PS-5.7-trunk"
        os.chdir(new_path.format(self.testpath))
        build_cmd = "{}/percona-qa/build_5.x_debug.sh"
        status, output = subprocess.getstatusoutput(build_cmd.format(self.testpath))
        if status == 0:
            logger.debug("PS build succeeded")
            os.chdir(saved_path)
            return True
        else:
            logger.error("PS build failed")
            logger.error(output)
            os.chdir(saved_path)
            return False

    def get_basedir(self):
        # Method for getting PS basedir path
        for root, dirs, files in os.walk(self.testpath):
            if 'PS' in dirs:
                logger.debug("Could get PS basedir path returning...")
                basedir_path = "{}/{}"
                print(basedir_path)
                return basedir_path.format(self.testpath, dirs)

        logger.warning("Could not get PS basedir path...")
        return False

        # cmd = 'ls -1td {}/PS* | grep -v ".tar" | grep PS[0-9]'
        # status, output = subprocess.getstatusoutput(cmd.format(self.testpath))
        # if status == 0:
        #     logger.debug("Could get PS basedir path returning...")
        #     return output
        # else:
        #     logger.error("Could not get PS basedir path failed...")
        #     logger.error(output)
        #     return False

    def prepare_startup(self, basedir_path):
        # Method for calling startup.sh file from percona-qa folder
        saved_path = os.getcwd()
        os.chdir(basedir_path)

        startup_cmd = "{}/percona-qa/startup.sh"
        status, output = subprocess.getstatusoutput(startup_cmd.format(self.testpath))
        if status == 0:
            logger.debug("Running startup.sh succeeded")
            os.chdir(saved_path)
            return True
        else:
            logger.error("Running startup.sh failed")
            logger.error(output)
            os.chdir(saved_path)
            return False

    @staticmethod
    def start_server(basedir_path):
        # Method for calling start script which is created inside PS basedir
        start_cmd = "{}/start"
        status, output = subprocess.getstatusoutput(start_cmd.format(basedir_path))
        if status == 0:
            logger.debug("Server started!")
            return True
        else:
            logger.error("Server start failed")
            logger.error(output)
            return False

    @staticmethod
    def wipe_server_all(basedir_path):
        # Method for calling "all" script which is created inside PS basedir
        saved_path = os.getcwd()
        os.chdir(basedir_path)
        all_cmd = "./all_no_cl"
        status, output = subprocess.getstatusoutput(all_cmd)
        if status == 0:
            logger.debug("Server wiped for fresh start!")
            os.chdir(saved_path)
            return True
        else:
            logger.error("All script run failed")
            logger.error(output)
            os.chdir(saved_path)
            return False
