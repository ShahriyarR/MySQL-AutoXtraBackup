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
        '''
        Method for checking if MySQL server is up or not.
        :param options: Passed options to connect to MySQL server if None, then going to get it from conf file
        :return: True on success, raise RuntimeError on error.
        '''
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
                raise RuntimeError("Neither mysql_socket nor mysql_host and mysql_port are defined in config!")
        else:
            statusargs = "{} {} status".format(self.mysqladmin, options)
        
        logger.debug("Running mysqladmin command -> {}".format(statusargs))
        #statusargs = shlex.split(statusargs)
        status, output = subprocess.getstatusoutput(statusargs)
        #myadmin = subprocess.Popen(statusargs, stdout=subprocess.PIPE)

        if status == 0:
            logger.debug('OK: Server is Up and running')
            return True
        else:
            logger.error('FAILED: Server is NOT Up')
            raise RuntimeError('FAILED: Server is NOT Up')

        # if not ('Uptime' in str(myadmin.stdout.read())):
        #     logger.error('FAILED: Server is NOT Up')
        #     raise RuntimeError('FAILED: Server is NOT Up')
        # else:
        #     logger.debug('OK: Server is Up and running')
        #     return True

    def check_mysql_conf(self):
        '''
        Method for checking passed MySQL my.cnf defaults file. If it is not passed then skip this check
        :return: True on success, raise RuntimeError on error.
        '''
        if self.mycnf is None or self.mycnf == '':
            logger.debug("Skipping my.cnf check, because it is not specified")
            return True
        elif not os.path.exists(self.mycnf) and (self.mycnf is not None):
            logger.error('FAILED: MySQL configuration file path does NOT exist')
            raise RuntimeError('FAILED: MySQL configuration file path does NOT exist')
        else:
            logger.debug('OK: MySQL configuration file exists')
            return True

    def check_mysql_mysql(self):
        '''
        Method for checking mysql client path
        :return: True on success, raise RuntimeError on error.
        '''
        if not os.path.exists(self.mysql):
            logger.error('FAILED: {} doest NOT exist'.format(self.mysql))
            raise RuntimeError('FAILED: {} doest NOT exist'.format(self.mysql))
        else:
            logger.debug('OK: {} exists'.format(self.mysql))
            return True

    def check_mysql_mysqladmin(self):
        '''
        Method for checking mysqladmin path
        :return: True on success, raise RuntimeError on error.
        '''
        if not os.path.exists(self.mysqladmin):
            logger.error('FAILED: {} does NOT exist'.format(self.mysqladmin))
            raise RuntimeError('FAILED: {} does NOT exist'.format(self.mysqladmin))
        else:
            logger.debug('OK: {} exists'.format(self.mysqladmin))
            return True

    def check_mysql_backuptool(self):
        if not os.path.exists(self.backup_tool):
            logger.error('FAILED: XtraBackup does NOT exist')
            raise RuntimeError('FAILED: XtraBackup does NOT exist')
        else:
            logger.debug('OK: XtraBackup exists')
            return True

    def check_mysql_backupdir(self):
        '''
        Check for MySQL backup directory.
        If directory exists already then, return True. If not, try to create it.
        :return: True on success.
        '''
        if not (os.path.exists(self.backupdir)):
            logger.debug('Main backup directory does not exist')
            logger.debug('Creating Main Backup folder...')
            os.makedirs(self.backupdir)
            logger.debug('OK: Created')
            return True
        else:
            logger.debug('OK: Main backup directory exists')
            return True

    def check_mysql_archive_dir(self):
        '''
        Check for archive directory.
        If archive_dir is given in config file and if it is does not exist, try to create.
        :return: True on success.
        '''
        if hasattr(self, 'archive_dir'):
            if not (os.path.exists(self.archive_dir)):
                logger.debug('Archive backup directory does not exist')
                logger.debug('Creating archive folder...')
                os.makedirs(self.archive_dir)
                logger.debug('OK: Created')
                return True
            else:
                logger.debug('OK: Archive folder directory exists')
                return True
        else:
            return True

    def check_mysql_fullbackupdir(self):
        '''
        Check full backup directory path.
        If this path exists return True if not try to create.
        :return: True on success.
        '''
        if not (os.path.exists(self.full_dir)):
            logger.debug('Full Backup directory does not exist')
            logger.debug('Creating full backup directory...')
            os.makedirs(self.full_dir)
            logger.debug('OK: Created')
            return True
        else:
            logger.debug("OK: Full Backup directory exists")
            return True

    def check_mysql_incbackupdir(self):
        '''
        Check incremental backup directory path.
        If this path exists return True if not try to create.
        :return: True on success.
        '''
        if not (os.path.exists(self.inc_dir)):
            logger.debug('Increment directory does not exist')
            logger.debug('Creating increment backup directory...')
            os.makedirs(self.inc_dir)
            logger.debug('OK: Created')
            return True
        else:
            logger.debug('OK: Increment directory exists')
            return True

    def check_all_env(self):
        '''
        Method for running all checks
        :return: True on success, raise RuntimeError on error.
        '''
        try:
            self.check_mysql_uptime()
            self.check_mysql_mysql()
            self.check_mysql_mysqladmin()
            self.check_mysql_conf()
            self.check_mysql_backuptool()
            self.check_mysql_backupdir()
            self.check_mysql_fullbackupdir()
            self.check_mysql_incbackupdir()
            self.check_mysql_archive_dir()
        except Exception as err:
            logger.critical("FAILED: Check status")
            logger.error(err)
            raise RuntimeError("FAILED: Check status")
        else:
            logger.debug("OK: Check status")
            return True