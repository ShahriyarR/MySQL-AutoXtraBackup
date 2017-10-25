from general_conf.generalops import GeneralClass
import os
import sys

import logging
logger = logging.getLogger(__name__)

class TestModeConfCheck(GeneralClass):
    """
    Class for checking environment for running Test Mode.
    """
    def __init__(self, config='/etc/bck.conf'):
        self.conf = config
        super().__init__(config=self.conf)
        if hasattr(self, 'gitcmd') and hasattr(self, 'testpath'):
            pass
        else:
            logger.critical("Missing needed variables from config file")
            sys.exit(-1)

    def check_test_path(self, path):
        if not os.path.exists(path):
            try:
                logger.debug("Test dir does not exist")
                logger.debug("Creating test mode directory")
                os.makedirs(self.testpath)
                return True
            except Exception as err:
                logger.error(err)
                return False
        else:
            return True
