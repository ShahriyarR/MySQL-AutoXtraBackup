#!/opt/Python-3.3.2/bin/python3
import re
import subprocess
import os
from general_conf.generalops import GeneralClass
from general_conf import path_config

import logging
logger = logging.getLogger(__name__)


class CheckEnv(GeneralClass):

    def __init__(self, config=path_config.config_path_file, full_dir=None, inc_dir=None):
        self.conf = config
        GeneralClass.__init__(self, self.conf)
        if full_dir:
            self.full_dir = full_dir
        if inc_dir:
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

        # filter out password from argument list
        filteredargs = re.sub("--password='?\w+'?", "--password='*'", statusargs)

        logger.debug("Running mysqladmin command -> {}".format(filteredargs))

        status, output = subprocess.getstatusoutput(statusargs)

        if status == 0:
            logger.debug('OK: Server is Up and running')
            return True
        else:
            logger.error('FAILED: Server is NOT Up')
            raise RuntimeError('FAILED: Server is NOT Up')

    def check_mysql_conf(self):
        '''
        Method for checking passed MySQL my.cnf defaults file. If it is not passed then skip this check
        :return: True on success, raise RuntimeError on error.
        '''
        if self.mycnf is None or self.mycnf == '':
            logger.debug("Skipping my.cnf check, because it is not specified")
            return True
        elif not os.path.exists(self.mycnf) and self.mycnf:
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
        if os.path.exists(self.mysql):
            logger.debug('OK: {} exists'.format(self.mysql))
            return True
        else:
            logger.error('FAILED: {} doest NOT exist'.format(self.mysql))
            raise RuntimeError('FAILED: {} doest NOT exist'.format(self.mysql))

    def check_mysql_mysqladmin(self):
        '''
        Method for checking mysqladmin path
        :return: True on success, raise RuntimeError on error.
        '''
        if os.path.exists(self.mysqladmin):
            logger.debug('OK: {} exists'.format(self.mysqladmin))
            return True
        else:
            logger.error('FAILED: {} does NOT exist'.format(self.mysqladmin))
            raise RuntimeError('FAILED: {} does NOT exist'.format(self.mysqladmin))

    def check_mysql_backuptool(self):
        """
        Method for checking if given backup tool path is there or not.
        :return: RuntimeError on failure, True on success
        """
        if os.path.exists(self.backup_tool):
            logger.debug('OK: XtraBackup exists')
            return True
        else:
            logger.error('FAILED: XtraBackup does NOT exist')
            raise RuntimeError('FAILED: XtraBackup does NOT exist')

    def check_mysql_backupdir(self):
        """
        Check for MySQL backup directory.
        If directory exists already then, return True. If not, try to create it.
        :return: True on success. RuntimeError on failure.
        """
        if os.path.exists(self.backupdir):
            logger.debug('OK: Main backup directory exists')
            return True
        else:
            logger.debug('Main backup directory does not exist')
            logger.debug('Creating Main Backup folder...')
            try:
                os.makedirs(self.backupdir)
                logger.debug('OK: Created')
                return True
            except Exception as err:
                logger.error("FAILED: Could not create directory, ", err)
                raise RuntimeError("FAILED: Could not create directory")


    def check_mysql_archive_dir(self):
        '''
        Check for archive directory.
        If archive_dir is given in config file and if it does not exist, try to create.
        :return: True on success. RuntimeError on failure.
        '''
        if hasattr(self, 'archive_dir'):
            if os.path.exists(self.archive_dir):
                logger.debug('OK: Archive folder directory exists')
                return True
            else:
                logger.debug('Archive backup directory does not exist')
                logger.debug('Creating archive folder...')
                try:
                    os.makedirs(self.archive_dir)
                    logger.debug('OK: Created')
                    return True
                except Exception as err:
                    logger.error("FAILED: Could not create directory, ", err)
                    raise RuntimeError("FAILED: Could not create directory")
        else:
            return True

    def check_mysql_fullbackupdir(self):
        '''
        Check full backup directory path.
        If this path exists return True if not try to create.
        :return: True on success.
        '''
        if os.path.exists(self.full_dir):
            logger.debug("OK: Full Backup directory exists")
            return True
        else:
            logger.debug('Full Backup directory does not exist')
            logger.debug('Creating full backup directory...')
            try:
                os.makedirs(self.full_dir)
                logger.debug('OK: Created')
                return True
            except Exception as err:
                logger.error("FAILED: Could not create directory, ", err)
                raise RuntimeError("FAILED: Could not create directory")

    def check_mysql_incbackupdir(self):
        '''
        Check incremental backup directory path.
        If this path exists return True if not try to create.
        :return: True on success.
        '''
        if os.path.exists(self.inc_dir):
            logger.debug('OK: Increment directory exists')
            return True
        else:
            logger.debug('Increment directory does not exist')
            logger.debug('Creating increment backup directory...')
            try:
                os.makedirs(self.inc_dir)
                logger.debug('OK: Created')
                return True
            except Exception as err:
                logger.error("FAILED: Could not create directory, ", err)
                raise RuntimeError("FAILED: Could not create directory")

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