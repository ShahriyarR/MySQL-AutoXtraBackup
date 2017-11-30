from prepare_env_test_mode.test_check_env import TestModeConfCheck
from shutil import rmtree
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
        t_obj = TestModeConfCheck(config=self.conf)
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
        ps_branches = self.ps_branches.split()
        for branch in ps_branches:
            if branch != '5.5':
                clone_cmd = "git clone {} -b {} {}/PS-{}-trunk".format(self.gitcmd, branch, self.testpath, branch)
            else:
                clone_cmd = "git clone {} -b {} {}/PS-{}-trunk".format(self.gitcmd.split()[-1], branch, self.testpath, branch)
            if not os.path.exists("{}/PS-{}-trunk".format(self.testpath, branch)):
                logger.debug("Started to clone Percona Server...")
                status, output = subprocess.getstatusoutput(clone_cmd)
                if status == 0:
                    logger.debug("PS-{} cloned ready to build".format(branch))
                else:
                    logger.error("Cloning PS-{} failed".format(branch))
                    logger.error(output)
                    return False

        return True

    def clone_pxb(self):
        # Clone PXB
        pxb_branches = self.pxb_branches.split()
        for branch in pxb_branches:
            clone_cmd = "git clone {} -b {} {}/PXB-{}"
            if not os.path.exists("{}/PXB-{}".format(self.testpath, branch)):
                logger.debug("Started to clone PXB...")
                status, output = subprocess.getstatusoutput(
                    clone_cmd.format(self.pxb_gitcmd, branch, self.testpath, branch))
                if status == 0:
                    logger.debug("PXB-{} cloned ready to build".format(branch))
                else:
                    logger.error("Cloning PXB-{} failed".format(branch))
                    logger.error(output)
                    return False
        return True

    def build_pxb(self):
        # Building pxb from source
        # For this purpose will use build_{}_pxb.sh scripts from this folder
        pxb_branches = self.pxb_branches.split()
        saved_path = os.getcwd()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        for branch in pxb_branches:
            pxb_path = "{}/PXB-{}".format(self.testpath, branch)
            os.chdir(pxb_path)
            build_cmd = "{}/build_{}_pxb.sh {}".format(dir_path, branch, self.testpath)
            status, output = subprocess.getstatusoutput(build_cmd)
            if status == 0:
                logger.debug("PXB build succeeded")
                os.chdir(saved_path)
            else:
                logger.error("PXB build failed")
                logger.error(output)
                os.chdir(saved_path)
                return False

        return True

    def build_server(self):
        # Building server from source
        # For this purpose; I am going to use build_5.x_debug.sh script from percona-qa
        saved_path = os.getcwd()
        # Specify here the cloned PS path; for me it is PS-5.7-trunk(which I have hard coded in method above)
        ps_branches = self.ps_branches.split()
        for branch in ps_branches:
            new_path = "{}/PS-{}-trunk"
            os.chdir(new_path.format(self.testpath, branch))
            if '5.5' in branch:
                # Use same script with 5.5 and 5.6 versions
                build_cmd = "{}/percona-qa/build_5.x_debug_5.6_for_pxb_tests.sh"
            else:
                build_cmd = "{}/percona-qa/build_5.x_debug_{}_for_pxb_tests.sh"
            logger.debug("Started to build Percon Server from source...")
            status, output = subprocess.getstatusoutput(build_cmd.format(self.testpath, branch))
            if status == 0:
                logger.debug("PS build succeeded")
                os.chdir(saved_path)
            else:
                logger.error("PS build failed")
                logger.error(output)
                os.chdir(saved_path)
                return False

        return True

    def rename_basedirs(self):
        logger.debug("Renaming basedir folder name...")
        basedirs = []
        for root, dirs, files in os.walk(self.testpath):
            for dir_name in dirs:
                obj = re.search('PS[0-9]', dir_name)
                if obj:
                    basedir_path = "{}/{}"
                    basedirs.append(basedir_path.format(self.testpath, dir_name))
        if len(basedirs) > 0:
            for i in basedirs:
                os.rename(i, i.replace('-percona-server', ''))
            return True
        else:
            logger.warning("Could not get PS basedir path...")
            logger.debug("It looks like you should build server first...")
            return False

    def get_basedir(self):
        # Method for getting PS basedir path
        logger.debug("Trying to get basedir path...")
        basedirs = []
        for root, dirs, files in os.walk(self.testpath):
            for dir_name in dirs:
                obj = re.search('PS[0-9]', dir_name)
                if obj:
                    basedir_path = "{}/{}"
                    basedirs.append(basedir_path.format(self.testpath, dir_name))
                    # return basedir_path.format(self.testpath, dir_name)
        if len(basedirs) > 0:
            logger.debug("Could get PS basedir path...")
            return basedirs
        else:
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
    def prepare_start_dynamic(basedir_path):
        # Method for calling start_dynamic.sh from basedir.
        # It will generated start_dynamuc executables in basedir.
        saved_path = os.getcwd()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(basedir_path)
        start_dynamic = "{}/start_dynamic.sh".format(dir_path)
        logger.debug("Running start_dynamic.sh here...")
        status, output = subprocess.getstatusoutput(start_dynamic)
        if status == 0:
            logger.debug("Running start_dynamic.sh succeeded")
            os.chdir(saved_path)
            return True
        else:
            logger.error("Running start_dynamic.sh failed")
            logger.error(output)
            os.chdir(saved_path)
            return False

    @staticmethod
    def start_server(basedir_path, options=None):
        # Method for calling start script which is created inside PS basedir
        logger.debug("Using start script here...")
        if options is not None:
            start_cmd = "{}/start {}"
            status, output = subprocess.getstatusoutput(start_cmd.format(basedir_path, options))
        else:
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
    def wipe_server_all(basedir_path, options=None):
        # Method for calling "all" script which is created inside PS basedir
        saved_path = os.getcwd()
        os.chdir(basedir_path)
        logger.debug("Using all_no_cl script here...")
        if options is not None:
            all_cmd = "./all_no_cl {}"
            status, output = subprocess.getstatusoutput(all_cmd.format(options))
        else:
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

    def extract_xb_archive(self, file_name):
        # General method for extracting XB archives
        # It will create target folder inside test path
        extract_cmd = "tar -xf {}/{} -C {}"
        if os.path.isfile("{}/{}".format(self.testpath, file_name)):
            if not os.path.isdir("{}/target/{}".format(self.testpath, file_name[:-7])):
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


