#!/opt/Python-3.3.2/bin/python3

import shlex
import subprocess
import os
import time
from general_conf.generalops import GeneralClass

import logging
logger = logging.getLogger(__name__)


class CheckEnv(GeneralClass):

    def __init__(self, config='/etc/bck.conf', full_dir=None, inc_dir=None):
        self.conf = config
        GeneralClass.__init__(self, self.conf)
        if full_dir is not None:
            self.full_dir = full_dir
        if inc_dir is not None:
            self.inc_dir = inc_dir

    def check_mysql_uptime(self, options=None):

        if options is None:

            statusargs = '{} --defaults-file={} --user={} --password={} status'.format(self.mysqladmin,
                                                                                   self.mycnf,
                                                                                   self.mysql_user,
                                                                                   self.mysql_password)

            if hasattr(self, 'mysql_socket'):
                statusargs += " --socket={}".format(self.mysql_socket)
            elif hasattr(self, 'mysql_host') and hasattr(self, 'mysql_port'):
                statusargs += " --host={}".format(self.mysql_host)
                statusargs += " --port={}".format(self.mysql_port)
            else:
                logger.critical("Neither mysql_socket nor mysql_host and mysql_port are defined in config!")
                return False
        else:
            statusargs = "{} {} status".format(self.mysqladmin, options)
        
        logger.debug("Running mysqladmin command -> {}".format(statusargs))
        statusargs = shlex.split(statusargs)
        myadmin = subprocess.Popen(statusargs, stdout=subprocess.PIPE)

        if not ('Uptime' in str(myadmin.stdout.read())):
            logger.error('FAILED: Server is NOT Up')
            return False
        else:
            logger.debug('OK: Server is Up and running')
            return True

    def check_mysql_conf(self):
        if self.mycnf is None or self.mycnf == '':
            logger.debug("Skipping my.cnf check, because it is not specified")
            return True
        elif not os.path.exists(self.mycnf) and (self.mycnf is not None):
            logger.error('FAILED: MySQL configuration file path does NOT exist')
            return False
        else:
            logger.debug('OK: MySQL configuration file exists')
            return True

    def check_mysql_mysql(self):
        if not os.path.exists(self.mysql):
            logger.error('FAILED: {} doest NOT exist'.format(self.mysql))
            return False
        else:
            logger.debug('OK: {} exists'.format(self.mysql))
            return True

    def check_mysql_mysqladmin(self):
        if not os.path.exists(self.mysqladmin):
            logger.error('FAILED: {} does NOT exist'.format(self.mysqladmin))
            return False
        else:
            logger.debug('OK: {} exists'.format(self.mysqladmin))
            return True

    def check_mysql_backuptool(self):
        if not os.path.exists(self.backup_tool):
            logger.error('FAILED: XtraBackup does NOT exist')
            return False
        else:
            logger.debug('OK: XtraBackup exists')
            return True

    def check_mysql_backupdir(self):

        if not (os.path.exists(self.backupdir)):
            try:
                logger.debug('Main backup directory does not exist')
                logger.debug('Creating Main Backup folder...')
                os.makedirs(self.backupdir)
                logger.debug('OK: Created')
                return True
            except Exception as err:
                logger.error('FAILED: Could not create backup folder')
                logger.error(err)
                return False
        else:
            logger.debug('OK: Main backup directory exists')
            return True

    def check_mysql_archive_dir(self):

        if not (os.path.exists(self.archive_dir)):
            try:
                logger.debug('Archive backup directory does not exist')
                logger.debug('Creating archive folder...')
                os.makedirs(self.archive_dir)
                logger.debug('OK: Created')
                return True
            except Exception as err:
                logger.error("FAILED: Could not create archive folder")
                logger.error(err)
                return False
        else:
            logger.debug('OK: Archive folder directory exists')
            return True

    def check_mysql_fullbackupdir(self):

        if not (os.path.exists(self.full_dir)):
            try:
                logger.debug('Full Backup directory does not exist')
                logger.debug('Creating full backup directory...')
                os.makedirs(self.full_dir)
                logger.debug('OK: Created')
                return True
            except Exception as err:
                logger.error("FAILED: Could not create full backup directory")
                logger.error(err)
                return False
        else:
            logger.debug("OK: Full Backup directory exists")
            return True

    def check_mysql_incbackupdir(self):

        if not (os.path.exists(self.inc_dir)):
            try:
                logger.debug('Increment directory does not exist')
                logger.debug('Creating increment backup directory...')
                os.makedirs(self.inc_dir)
                logger.debug('OK: Created')
                return True
            except Exception as err:
                logger.error("FAILED: Could not create increment backup directory")
                logger.error(err)
                return False
        else:
            logger.debug('OK: Increment directory exists')
            return True

    def check_all_env(self):

        env_result = False

        if self.check_mysql_uptime():
            if self.check_mysql_mysql():
                if self.check_mysql_mysqladmin():
                    if self.check_mysql_conf():
                        if self.check_mysql_backuptool():
                            if self.check_mysql_backupdir():
                                if self.check_mysql_fullbackupdir():
                                    if self.check_mysql_incbackupdir():
                                        if hasattr(self, 'archive_dir') and self.check_mysql_archive_dir():
                                            env_result = True
                                        else:
                                            env_result = True

            if env_result:
                logger.debug("OK: Check status")
                return env_result
            else:
                logger.critical("FAILED: Check status")
                return env_result