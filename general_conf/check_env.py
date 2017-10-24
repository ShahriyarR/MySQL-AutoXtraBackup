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

    def check_mysql_uptime(self):

        statusargs = '%s --defaults-file=%s --user=%s --password=%s status' % (
            self.mysqladmin, self.mycnf, self.mysql_user, self.mysql_password)

        if hasattr(self, 'mysql_socket'):
            statusargs += " --socket=%s" % (self.mysql_socket)
        elif hasattr(self, 'mysql_host') and hasattr(self, 'mysql_port'):
            statusargs += " --host=%s" % self.mysql_host
            statusargs += " --port=%s" % self.mysql_port
        else:
            logger.critical(
                "Neither mysql_socket nor mysql_host and mysql_port are defined in config!")
            return False
        
        logger.debug(
            "Running mysqladmin command -> %s", statusargs)
        statusargs = shlex.split(statusargs)
        myadmin = subprocess.Popen(statusargs, stdout=subprocess.PIPE)

        if not ('Uptime' in str(myadmin.stdout.read())):
            logger.error(
                'Server is NOT Up+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+')
            return False
        else:
            logger.debug(
                'Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK')
            return True

    def check_mysql_conf(self):
        if self.mycnf is None or self.mycnf == '':
            logger.debug("Skipping my.cnf check, because it is not specified")
            return True
        elif not os.path.exists(self.mycnf) and (self.mycnf is not None):
            # Testing with MariaDB Galera Cluster
            # if not os.path.exists(self.maria_cluster_cnf):
            logger.error(
                'MySQL configuration file path does NOT exist+-+-+-+-+-+-+-+-+-+')
            return False
        else:
            logger.debug(
                'MySQL configuration file exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+OK')
            return True

    def check_mysql_mysql(self):
        if not os.path.exists(self.mysql):
            logger.error(
                '%s doest NOT exist+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+' % self.mysql)
            return False
        else:
            logger.debug(
                '%s exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-OK' % self.mysql)
            return True

    def check_mysql_mysqladmin(self):
        if not os.path.exists(self.mysqladmin):
            logger.error(
                '%s does NOT exist+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-' % self.mysqladmin)
            return False
        else:
            logger.debug(
                '%s exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK' % self.mysqladmin)
            return True

    def check_mysql_backuptool(self):
        if not os.path.exists(self.backup_tool):
            logger.error(
                'Xtrabackup does NOT exist+-+-+-+-+-+-+-+-+-++-+-+-+-+-')
            return False
        else:
            logger.debug(
                'Xtrabackup exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-OK')
            return True

    def check_mysql_backupdir(self):

        if not (os.path.exists(self.backupdir)):
            try:
                logger.debug(
                    'Main backup directory does not exist+-+-+-+-+-+-+-+-+-++-+-+-+-')
                logger.debug(
                    'Creating Main Backup folder+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+')
                os.makedirs(self.backupdir)
                logger.debug(
                    'Created+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK')
                return True
            except Exception as err:
                logger.error(err)
                return False
        else:
            logger.debug(
                'Main backup directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK')
            return True

    def check_mysql_archive_dir(self):

        if not (os.path.exists(self.archive_dir)):
            try:
                logger.debug(
                    'Archive backup directory does not exist+-+-+-+-+-+-+-+-+-++-+-+-+-')
                logger.debug(
                    'Creating archive folder+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+')
                os.makedirs(self.archive_dir)
                logger.debug(
                    'Created+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK')
                return True
            except Exception as err:
                logger.error(err)
                return False
        else:
            logger.debug(
                'Archive folder directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK')
            return True

    def check_mysql_fullbackupdir(self):

        if not (os.path.exists(self.full_dir)):
            try:
                logger.debug(
                    'Full Backup directory does not exist.+-+-+-+-+-+-+-+-+-+-+-+-OK')
                logger.debug(
                    'Creating full backup directory...+-+-+-+-+-+-+-+-+-++-+-+-+-+OK')
                #os.makedirs(self.backupdir + '/full')
                os.makedirs(self.full_dir)
                logger.debug(
                    'Created+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK')
                return True
            except Exception as err:
                logger.error(err)
                return False
        else:
            logger.debug(
                "Full Backup directory exists.+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+OK")
            return True

    def check_mysql_incbackupdir(self):

        if not (os.path.exists(self.inc_dir)):
            try:
                logger.debug(
                    'Increment directory does not exist.+-+-+-+-+-+-+-+-+-++-+-+-+OK')
                logger.debug(
                    'Creating increment backup directory.+-+-+-+-+-+-+-+-+-++-+-+-OK')
                #os.makedirs(self.backupdir + '/inc')
                os.makedirs(self.inc_dir)
                logger.debug('Created')
                return True
            except Exception as err:
                logger.error(err)
                return False
        else:
            logger.debug(
                'Increment directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK')
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
                                        if hasattr(
                                                self, 'archive_dir') and self.check_mysql_archive_dir():
                                            # if
                                            # self.check_mysql_flush_log_user():
                                            env_result = True
                                        else:
                                            env_result = True

            if env_result:
                logger.debug(
                    "Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-OK")
                return env_result
            else:
                logger.critical(
                    "Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-FAILED")
                return env_result
