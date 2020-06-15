# Backup Prepare and Copy-Back Script
# Originally Developed by
# Shahriyar Rzayev -> http://www.mysql.az
# / rzayev.sehriyar@gmail.com / rzayev.shahriyar@yandex.com


import os
import subprocess
import shutil
import time
import logging

from os.path import isfile
from general_conf import path_config
from process_runner.process_runner import ProcessRunner
from utils import helpers
from backup_backup.backuper import Backup

logger = logging.getLogger(__name__)


class Prepare(Backup):

    def __init__(self, config=path_config.config_path_file, dry_run=0, tag=None):
        self.conf = config
        self.dry = dry_run
        self.tag = tag
        Backup.__init__(self, self.conf)
        # If prepare_tool option enabled in config, make backup_tool to use this.
        try:
            self.backup_tool = self.prepare_tool
        except AttributeError:
            pass

        if self.tag and not os.path.isfile("{}/backup_tags.txt".format(self.backupdir)):
            raise RuntimeError("Could not find backup_tags.txt inside backup directory. "
                               "Please run without --tag option")

    def check_inc_backups(self):
        # Check for Incremental backups
        return os.listdir(self.inc_dir)

    @staticmethod
    def parse_backup_tags(backup_dir, tag_name):
        """
        Static Method for returning the backup directory name and backup type
        :param backup_dir: The backup directory path
        :param tag_name: The tag name to search
        :return: Tuple of (backup directory, backup type) (2017-11-09_19-37-16, Full).
        :raises: RuntimeError if there is no such tag inside backup_tags.txt
        """
        if os.path.isfile("{}/backup_tags.txt".format(backup_dir)):
            with open('{}/backup_tags.txt'.format(backup_dir), 'r') as bcktags:
                f = bcktags.readlines()

            for i in f:
                splitted = i.split('\t')
                if tag_name == splitted[-1].rstrip("'\n\r").lstrip("'"):
                    return splitted[0], splitted[1]
            raise RuntimeError('There is no such tag for backups')

    def decompress_backup(self, path, dir_name):
        """
        Method for backup decompression.
        Check if decompression enabled, if it is, decompress
        backup prior prepare.
        :param path: the basedir path i.e full backup dir or incremental dir.
        :param dir_name: the exact name backup folder(likely timestamped folder name).
        :return: None or RuntimeError
        """
        if hasattr(self, 'decompress'):
            # The base decompression command
            decmp = "{} --decompress={} --target-dir={}/{}".format(
                self.backup_tool,
                self.decompress,
                path,
                dir_name)
            if hasattr(self, 'remove_original_comp') and self.remove_original_comp:
                decmp += " --remove-original"

            logger.info("Trying to decompress backup")
            logger.info("Running decompress command -> {}".format(decmp))
            if self.dry:
                return
            ProcessRunner.run_command(decmp)

    def decrypt_backup(self, path, dir_name):
        """
        Method for decrypting backups.
        If you use crypted backups it should be decrypted prior preparing.
        :param path: the basedir path i.e full backup dir or incremental dir.
        :param dir_name: the exact name backup folder(likely timestamped folder name).
        :return: None or RuntimeError
        """
        if hasattr(self, 'decrypt'):
            # The base decryption command
            decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{}".format(
                self.backup_tool,
                self.decrypt,
                self.encrypt_key,
                path,
                dir_name)
            if hasattr(self, 'remove_original_enc') and self.remove_original_enc:
                decr += " --remove-original"
            logger.info("Trying to decrypt backup")
            logger.info("Running decrypt command -> {}".format(decr))
            if self.dry:
                return
            ProcessRunner.run_command(decr)

    def prepare_command_builder(self, full_backup, incremental=None, apply_log_only=None):
        """
        Method for building prepare command as it is repeated several times.
        :param full_backup: The full backup directory name
        :param incremental: The incremental backup directory name
        :param apply_log_only: The flag to add --apply-log-only
        :return: The prepare command string
        """
        # Base prepare command
        xtrabackup_prepare_cmd = "{} --prepare --target-dir={}/{}".format(
            self.backup_tool,
            self.full_dir,
            full_backup)

        if incremental:
            xtrabackup_prepare_cmd += " --incremental-dir={}/{}".format(self.inc_dir, incremental)
        if apply_log_only:
            xtrabackup_prepare_cmd += " --apply-log-only"

        # Checking if extra options were passed:
        if hasattr(self, 'xtra_options'):
            xtrabackup_prepare_cmd += "  {}".format(self.xtra_options)

        # Checking of extra prepare options were passed:
        if hasattr(self, 'xtra_prepare_options'):
            xtrabackup_prepare_cmd += "  {}".format(self.xtra_prepare_options)

        return xtrabackup_prepare_cmd

    def prepare_with_tags(self):
        # Method for preparing backups based on passed backup tags
        found_backups = Prepare.parse_backup_tags(backup_dir=self.backupdir, tag_name=self.tag)
        recent_bck = helpers.get_latest_dir_name(self.full_dir)

        if found_backups[1] == 'Full':
            if recent_bck:
                logger.info("- - - - Preparing Full Backup - - - -")

                # Extracting/decrypting from streamed backup and extra checks goes here
                self.extract_decrypt_from_stream_backup(recent_full_bck=recent_bck)

                # Decrypt backup
                self.decrypt_backup(self.full_dir, recent_bck)

                # Decompress backup
                self.decompress_backup(self.full_dir, recent_bck)

                # Prepare command
                xtrabackup_prepare_cmd = self.prepare_command_builder(full_backup=recent_bck)
                if self.dry:
                    return
                ProcessRunner.run_command(xtrabackup_prepare_cmd)

        elif found_backups[1] == 'Inc':
            if not self.check_inc_backups():
                logger.info("- - - - You have no Incremental backups. So will prepare only latest Full backup - - - -")
                self.prepare_only_full_backup()
            else:
                logger.info("- - - - You have Incremental backups. - - - -")
                if self.prepare_only_full_backup():
                    logger.info("Preparing Incs: ")
                    list_of_dir = helpers.sorted_ls(self.inc_dir)
                    # Find the index number inside all list for backup(which was found via tag)
                    index_num = list_of_dir.index(found_backups[0])
                    # Limit the iteration until this found backup
                    for i in list_of_dir[:index_num + 1]:
                        if i != found_backups[0]:
                            logger.info("Preparing inc backups in sequence. inc backup dir/name is {}".format(i))
                            # Prepare command
                            xtrabackup_prepare_cmd = self.prepare_command_builder(full_backup=recent_bck,
                                                                                  incremental=i,
                                                                                  apply_log_only=True)
                        else:
                            logger.info("Preparing last incremental backup, inc backup dir/name is {}".format(i))

                            # Extracting/decrypting from streamed backup and extra checks goes here
                            self.extract_decrypt_from_stream_backup(recent_inc_bck=i, flag=True)

                            # Prepare command
                            xtrabackup_prepare_cmd = self.prepare_command_builder(full_backup=recent_bck,
                                                                                  incremental=i)
                        # Decrypt backup
                        self.decrypt_backup(self.inc_dir, i)

                        # Decompress backup
                        self.decompress_backup(self.inc_dir, i)

                        logger.info("Running prepare command -> {}".format(xtrabackup_prepare_cmd))
                        if self.dry:
                            return
                        ProcessRunner.run_command(xtrabackup_prepare_cmd)

        logger.info("- - - - The end of the Prepare Stage. - - - -")

    ##########################################################################
    # PREPARE ONLY FULL BACKUP
    ##########################################################################

    def untar_backup(self, recent_bck):
        if hasattr(self, 'stream') and self.stream == 'tar':
            untar_cmd = "tar -xf {}/{}/full_backup.tar -C {}/{}".format(self.full_dir,
                                                                        recent_bck,
                                                                        self.full_dir,
                                                                        recent_bck)
            logger.info("The following tar command will be executed -> {}".format(untar_cmd))
            if self.dry == 0 and isfile("{}/{}/full_backup.tar".format(self.full_dir, recent_bck)):
                ProcessRunner.run_command(untar_cmd)

    def prepare_only_full_backup(self):
        recent_bck = helpers.get_latest_dir_name(self.full_dir)
        if recent_bck:
            if not self.check_inc_backups():
                logger.info("- - - - Preparing Full Backup - - - -")
                self.untar_backup(recent_bck=recent_bck)
                # Extracting/decrypting from streamed backup and extra checks goes here
                self.extract_decrypt_from_stream_backup(recent_full_bck=recent_bck)

                # Prepare command
                xtrabackup_prepare_cmd = self.prepare_command_builder(full_backup=recent_bck)

            else:
                logger.info("- - - - Preparing Full backup for incrementals - - - -")
                logger.info("- - - - Final prepare,will occur after preparing all inc backups - - - -")
                time.sleep(3)

                # Prepare command
                xtrabackup_prepare_cmd = self.prepare_command_builder(full_backup=recent_bck, apply_log_only=True)

            # Decrypt backup
            self.decrypt_backup(self.full_dir, recent_bck)

            # Decompress backup
            self.decompress_backup(self.full_dir, recent_bck)

            logger.info("Running prepare command -> {}".format(xtrabackup_prepare_cmd))
            if self.dry:
                return
            ProcessRunner.run_command(xtrabackup_prepare_cmd)
        return True

    ##########################################################################
    # PREPARE INC BACKUPS
    ##########################################################################

    def prepare_inc_full_backups(self):
        if not self.check_inc_backups():
            logger.info("- - - - You have no Incremental backups. So will prepare only latest Full backup - - - -")
            return self.prepare_only_full_backup()
        else:
            logger.info("- - - - You have Incremental backups. - - - -")
            recent_bck = helpers.get_latest_dir_name(self.full_dir)

            if self.prepare_only_full_backup():
                logger.info("Preparing Incs: ")
                list_of_dir = sorted(os.listdir(self.inc_dir))
                for inc_backup_dir in list_of_dir:
                    if inc_backup_dir != max(os.listdir(self.inc_dir)):
                        logger.info(
                            "Preparing Incremental backups in sequence. Incremental backup dir/name is {}".format(
                                inc_backup_dir))

                        # Prepare command
                        xtrabackup_prepare_cmd = self.prepare_command_builder(full_backup=recent_bck,
                                                                              incremental=inc_backup_dir,
                                                                              apply_log_only=True)
                    else:
                        logger.info(
                            "Preparing last Incremental backup, inc backup dir/name is {}".format(inc_backup_dir))

                        # Extracting/decrypting from streamed backup and extra checks goes here
                        self.extract_decrypt_from_stream_backup(recent_inc_bck=inc_backup_dir, flag=True)

                        # Prepare command
                        xtrabackup_prepare_cmd = self.prepare_command_builder(full_backup=recent_bck,
                                                                              incremental=inc_backup_dir)
                    # Decrypt backup
                    self.decrypt_backup(self.inc_dir, inc_backup_dir)

                    # Decompress backup
                    self.decompress_backup(self.inc_dir, inc_backup_dir)

                    logger.info("Running prepare command -> {}".format(xtrabackup_prepare_cmd))
                    if self.dry:
                        return
                    ProcessRunner.run_command(xtrabackup_prepare_cmd)

            logger.info("- - - - The end of the Prepare Stage. - - - -")
            return True

    ##########################################################################
    # COPY-BACK PREPARED BACKUP
    ##########################################################################

    def shutdown_mysql(self):
        # Shut Down MySQL
        logger.info("Shutting Down MySQL server:")
        args = self.stop_mysql
        ProcessRunner.run_command(args)

    def move_to_tmp_dir(self):
        try:
            shutil.move(self.data_dir, self.tmpdir)
            logger.info("Moved data_dir to {} ...".format(self.tmpdir))
        except shutil.Error as err:
            logger.error("Error occurred while moving data_dir")
            logger.error(err)
            raise RuntimeError(err)

    def create_empty_data_dir(self):
        logger.info("Creating an empty data directory ...")
        makedir = "mkdir {}".format(self.data_dir)
        status, output = subprocess.getstatusoutput(makedir)
        if status == 0:
            logger.info("data_dir is Created! ...")
        else:
            logger.error("Error while creating data_dir")
            logger.error(output)
            raise RuntimeError(output)

    def move_data_dir(self):
        # Move data_dir to new directory
        logger.info("Moving MySQL data_dir to {}".format(self.tmpdir))
        if os.path.isdir(self.tmpdir):
            rmdirc = 'rm -rf {}'.format(self.tmpdir)
            status, output = subprocess.getstatusoutput(rmdirc)
            if status == 0:
                logger.info("Emptied {} directory ...".format(self.tmpdir))
            else:
                logger.error("Could not delete {} directory".format(self.tmpdir))
                logger.error(output)
                raise RuntimeError(output)
        self.move_to_tmp_dir()
        self.create_empty_data_dir()
        return True

    def run_xtra_copyback(self, data_dir=None):
        # Running Xtrabackup with --copy-back option
        copy_back = '{} --copy-back {} --target-dir={}/{} --data_dir={}'.format(
            self.backup_tool,
            self.xtra_options,
            self.full_dir,
            helpers.get_latest_dir_name(self.full_dir),
            self.data_dir if data_dir is None else data_dir)
        ProcessRunner.run_command(copy_back)
        
    def giving_chown(self, data_dir=None):
        # Changing owner of data_dir to given user:group
        give_chown = "{} {}".format(self.chown_command, self.data_dir if data_dir is None else data_dir)
        ProcessRunner.run_command(give_chown)
        
    def start_mysql_func(self, start_tool=None, options=None):
        # Starting MySQL
        logger.info("Starting MySQL server: ")
        args = self.start_mysql if start_tool is None else start_tool
        start_command = '{} {}'.format(args, options) if options is not None else args
        ProcessRunner.run_command(start_command)
        
    @staticmethod
    def check_if_backup_prepared(full_dir, full_backup_file):
        """
        This method is for checking if the backup can be copied-back.
        It is going to check xtrabackup_checkpoints file inside backup directory for backup_type column.
        backup_type column must be equal to 'full-prepared'
        :return: True if backup is already prepared; RuntimeError if it is not.
        """
        with open("{}/{}/xtrabackup_checkpoints".format(full_dir, full_backup_file), 'r') as xchk_file:
            # This thing seems to be complicated bu it is not:
            # Trying to get 'full-prepared' from ['backup_type ', ' full-prepared\n']
            if xchk_file.readline().split("=")[1].strip("\n").lstrip() == 'full-prepared':
                return True
            else:
                raise RuntimeError("This full backup is not fully prepared, not doing copy-back!")

    def copy(self, options=None, data_dir=None):
        """
        Function for running:
          xtrabackup --copy-back
          giving chown to data_dir
          starting mysql
        :return: True if succeeded. Error if failed
        """
        logger.info("Copying Back Already Prepared Final Backup:")
        if len(os.listdir(self.data_dir if data_dir is None else data_dir)) > 0:
            logger.info("MySQL data_dir is not empty!")
        else:
            self.run_xtra_copyback(data_dir=data_dir)
            self.giving_chown(data_dir=data_dir)
            self.start_mysql_func(options=options)
            return True

    def copy_back_action(self, options=None):
        """
        Function for complete recover/copy-back actions
        :return: True if succeeded. Error if failed.
        """
        try:
            self.check_if_backup_prepared(self.full_dir, helpers.get_latest_dir_name(self.full_dir))
            self.shutdown_mysql()
            if self.move_data_dir() and self.copy(options=options):
                logger.info("All data copied back successfully. ")
                logger.info("Your MySQL server is UP again")
        except Exception as err:
            logger.error("{}: {}".format(type(err).__name__, err))

    ##########################################################################
    # FINAL FUNCTION FOR CALL: prepare_backup_and_copy_back()
    ##########################################################################

    def prepare_backup_and_copy_back(self):
        # Recovering/Copying Back Prepared Backup

        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        print("")
        print("Preparing full/inc backups!")
        print("What do you want to do?")
        print("1. Prepare Backups and keep for future usage. NOTE('Once Prepared Backups Can not be prepared Again')")
        print("2. Prepare Backups and restore/recover/copy-back immediately")
        print("3. Just copy-back previously prepared backups")

        prepare = int(input("Please Choose one of options and type 1 or 2 or 3: "))
        print("")
        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        time.sleep(3)
        if prepare == 1:
            if self.tag is None:
                self.prepare_inc_full_backups()
            else:
                logger.info("Backup tag will be used to prepare backups")
                self.prepare_with_tags()
        elif prepare == 2:
            if self.tag is None:
                self.prepare_inc_full_backups()
            else:
                self.prepare_with_tags()
            if self.dry == 0:
                self.copy_back_action()
            else:
                logger.critical("Dry run is not implemented for copy-back/recovery actions!")
        elif prepare == 3:
            if self.dry == 0:
                self.copy_back_action()
            else:
                logger.critical("Dry run is not implemented for copy-back/recovery actions!")
        else:
            print("Please type 1 or 2 or 3 and nothing more!")
