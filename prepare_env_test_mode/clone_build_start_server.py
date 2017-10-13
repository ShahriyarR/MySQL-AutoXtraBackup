from prepare_env_test_mode.test_check_env import TestModeConfCheck
from general_conf.generalops import GeneralClass
import subprocess
import os
import re
import logging
logger = logging.getLogger(__name__)


class CloneBuildStartServer(TestModeConfCheck):
    """
    Class for cloning from git, building server from source and starting test server etc.
    This class will include all necessary actions for preparing test environment.
    Please see specific methods for clarity.
    """
    def __init__(self, config='/etc/bck.conf'):
        self.conf = config
        super().__init__(config=self.conf)
        #self.git_cmd = GeneralClass().gitcmd
        #self.xb_configs = GeneralClass().xb_configs
        # Creating needed path here
        t_obj = TestModeConfCheck()
        if t_obj.check_test_path(t_obj.testpath):
            self.testpath = t_obj.testpath

    def clone_percona_qa(self):
        # Clone percona-qa repo for using existing bash scripts
        clone_cmd = "git clone https://github.com/Percona-QA/percona-qa.git {}/percona-qa"
        if not os.path.exists("{}/percona-qa".format(self.testpath)):
            logger.debug("Started to clone percona-qa...")
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
        if not os.path.exists("{}/PS-5.7-trunk".format(self.testpath)):
            logger.debug("Started to clone Percona Server...")
            status, output = subprocess.getstatusoutput(clone_cmd.format(self.gitcmd, self.testpath))
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
        logger.debug("Started to build Percon Server from source...")
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
        logger.debug("Trying to get basedir path...")
        for root, dirs, files in os.walk(self.testpath):
            for dir_name in dirs:
                obj = re.search('PS[0-9]', dir_name)
                if obj:
                    logger.debug("Could get PS basedir path returning...")
                    basedir_path = "{}/{}"
                    return basedir_path.format(self.testpath, dir_name)

        logger.warning("Could not get PS basedir path...")
        logger.debug("It looks like you should build server first...")
        return False

    def prepare_startup(self, basedir_path):
        # Method for calling startup.sh file from percona-qa folder
        saved_path = os.getcwd()
        os.chdir(basedir_path)

        startup_cmd = "{}/percona-qa/startup.sh"
        logger.debug("Started to run startup.sh file...")
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
        logger.debug("Using start script here...")
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
        logger.debug("Using all_no_cl script here...")
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

    def get_xb_packages(self, file_name, url):
        # General method for getting XB packages
        wget_cmd = "wget {} -P {}"
        if not os.path.isfile("{}/{}".format(self.testpath, file_name)):
            status, output = subprocess.getstatusoutput(wget_cmd.format(url, self.testpath))
            if status == 0:
                logger.debug("Downloaded {}".format(file_name))
                return True
            else:
                logger.error("Failed to download {}".format(file_name))
                logger.error(output)
                return False
        else:
            logger.debug("The {} is already there".format(file_name))
            return True

    def extract_xb_archive(self, file_name):
        # General method for extracting XB archives
        # It will create target folder inside test path
        extract_cmd = "tar -xf {}/{} -C {}"
        if os.path.isfile("{}/{}".format(self.testpath, file_name)):
            if not os.path.isdir("{}/target".format(self.testpath)):
                status, output = subprocess.getstatusoutput(extract_cmd.format(self.testpath, file_name, self.testpath))
                if status == 0:
                    logger.debug("Extracted from {}".format(file_name))
                    return True
                else:
                    logger.error("Failed to extract from {}".format(file_name))
                    logger.error(output)
                    return False
            else:
                logger.debug("The 'target' folder already there...")
                return True
        else:
            logger.debug("Could not find {}".format(file_name))
            return False


