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
            if self.dry == 0:
                status = ProcessRunner.run_command(decmp)
                if status:
                    logger.info("OK: Decompressed")
                else:
                    logger.error("FAILED: Decompression.")
                    raise RuntimeError("FAILED: Decompression.")

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
            if self.dry == 0:
                status = ProcessRunner.run_command(decr)
                if status:
                    logger.info("OK: Decrypted!")
                else:
                    logger.error("FAILED: FULL BACKUP decrypt")
                    raise RuntimeError("FAILED: FULL BACKUP decrypt")

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

                if self.dry == 0:
                    status = ProcessRunner.run_command(xtrabackup_prepare_cmd)
                    if not status:
                        logger.error("FAILED: FULL BACKUP prepare.")
                        raise RuntimeError("FAILED: FULL BACKUP prepare.")

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

                            # Decrypt backup
                            self.decrypt_backup(self.inc_dir, i)

                            # Decompress backup
                            self.decompress_backup(self.inc_dir, i)

                            # Prepare command
                            xtrabackup_prepare_cmd = self.prepare_command_builder(full_backup=recent_bck,
                                                                                  incremental=i,
                                                                                  apply_log_only=True)

                            logger.info("Running prepare command -> {}".format(xtrabackup_prepare_cmd))
                            if self.dry == 0:
                                status = ProcessRunner.run_command(xtrabackup_prepare_cmd)
                                if not status:
                                    logger.error("FAILED: Incremental BACKUP prepare")
                                    raise RuntimeError("FAILED: Incremental BACKUP prepare")

                        else:
                            logger.info("Preparing last incremental backup, inc backup dir/name is {}".format(i))
                            # Extracting streamed incremental backup prior to preparing

                            if hasattr(self, 'stream'):
                                logger.info("Using xbstream to extract from inc_backup.stream!")
                                xbstream_command = "{} {} < {}/{}/inc_backup.stream -C {}/{}".format(
                                    self.xbstream,
                                    self.xbstream_options,
                                    self.inc_dir,
                                    i,
                                    self.inc_dir,
                                    i)

                                logger.info(
                                    "The following xbstream command will be executed {}".format(xbstream_command))
                                if self.dry == 0 and isfile("{}/{}/inc_backup.stream".format(self.inc_dir, i)):
                                    status, output = subprocess.getstatusoutput(xbstream_command)
                                    if status == 0:
                                        logger.info("OK: XBSTREAM command succeeded.")
                                    else:
                                        logger.error("FAILED: XBSTREAM command.")
                                        logger.error(output)
                                        raise RuntimeError("FAILED: XBSTREAM command.")
                            # Decrypt backup
                            self.decrypt_backup(self.inc_dir, i)

                            # Decompress backup
                            self.decompress_backup(self.inc_dir, i)

                            # Prepare command
                            xtrabackup_prepare_cmd = self.prepare_command_builder(full_backup=recent_bck,
                                                                                  incremental=i)

                            logger.info("Running prepare command -> {}".format(xtrabackup_prepare_cmd))
                            if self.dry == 0:
                                status2 = ProcessRunner.run_command(xtrabackup_prepare_cmd)
                                if not status2:
                                    logger.error("FAILED: Incremental BACKUP prepare")
                                    raise RuntimeError("FAILED: Incremental BACKUP prepare")

        logger.info("- - - - The end of the Prepare Stage. - - - -")

    ##########################################################################
    # PREPARE ONLY FULL BACKUP
    ##########################################################################

    def prepare_only_full_backup(self):
        recent_bck = helpers.get_latest_dir_name(self.full_dir)
        if recent_bck:
            if not self.check_inc_backups():
                logger.info("- - - - Preparing Full Backup - - - -")
                if hasattr(self, 'stream') and self.stream == 'tar':
                    untar_cmd = "tar -xf {}/{}/full_backup.tar -C {}/{}".format(self.full_dir,
                                                                                recent_bck,
                                                                                self.full_dir,
                                                                                recent_bck)
                    logger.info("The following tar command will be executed -> {}".format(untar_cmd))
                    if self.dry == 0 and isfile("{}/{}/full_backup.tar".format(self.full_dir, recent_bck)):
                        status, output = subprocess.getstatusoutput(untar_cmd)
                        if status == 0:
                            logger.info("OK: extracting full backup from tar.")
                        else:
                            logger.error("FAILED: extracting full backup from tar")
                            logger.error(output)
                            raise RuntimeError("FAILED: extracting full backup from tar")

                # Extracting/decrypting from streamed backup and extra checks goes here
                self.extract_decrypt_from_stream_backup(recent_full_bck=recent_bck)

                # Decrypt backup
                self.decrypt_backup(self.full_dir, recent_bck)

                # Decompress backup
                self.decompress_backup(self.full_dir, recent_bck)

                # Prepare command
                xtrabackup_prepare_cmd = self.prepare_command_builder(full_backup=recent_bck)

                logger.debug("Running prepare command -> {}".format(xtrabackup_prepare_cmd))
                if self.dry == 0:
                    status = ProcessRunner.run_command(xtrabackup_prepare_cmd)
                    if status:
                        logger.info("Prepare command ran successfully.")
                    else:
                        logger.error("FAILED: FULL BACKUP prepare.")
                        raise RuntimeError("FAILED: FULL BACKUP prepare.")

            else:
                logger.info("- - - - Preparing Full backup for incrementals - - - -")
                logger.info("- - - - Final prepare,will occur after preparing all inc backups - - - -")
                time.sleep(3)

                # Decrypt backup
                self.decrypt_backup(self.full_dir, recent_bck)

                # Decompress backup
                self.decompress_backup(self.full_dir, recent_bck)

                # Prepare command
                xtrabackup_prepare_cmd = self.prepare_command_builder(full_backup=recent_bck, apply_log_only=True)

                logger.info("Running prepare command -> {}".format(xtrabackup_prepare_cmd))
                if self.dry == 0:
                    status = ProcessRunner.run_command(xtrabackup_prepare_cmd)
                    if status:
                        logger.info("Prepare command ran successfully")
                    else:
                        logger.error("FAILED: One time FULL BACKUP")
                        raise RuntimeError("FAILED: One time FULL BACKUP")
                else:
                    return True
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

                        # Decrypt backup
                        self.decrypt_backup(self.inc_dir, inc_backup_dir)

                        # Decompress backup
                        self.decompress_backup(self.inc_dir, inc_backup_dir)

                        # Prepare command
                        xtrabackup_prepare_cmd = self.prepare_command_builder(full_backup=recent_bck,
                                                                              incremental=inc_backup_dir,
                                                                              apply_log_only=True)
                    else:
                        logger.info(
                            "Preparing last Incremental backup, inc backup dir/name is {}".format(inc_backup_dir))
                        # TODO: figure out the way of calling only this
                        if hasattr(self, 'stream'):
                            logger.info("Using xbstream to extract from inc_backup.stream!")
                            xbstream_command = "{} {} < {}/{}/inc_backup.stream -C {}/{}".format(
                                self.xbstream,
                                self.xbstream_options,
                                self.inc_dir,
                                inc_backup_dir,
                                self.inc_dir,
                                inc_backup_dir)

                            logger.info("The following xbstream command will be executed {}".format(xbstream_command))
                            if self.dry == 0 and isfile("{}/{}/inc_backup.stream".format(self.inc_dir, inc_backup_dir)):
                                status, output = subprocess.getstatusoutput(xbstream_command)
                                if status == 0:
                                    logger.info("OK: XBSTREAM command succeeded.")
                                else:
                                    logger.error("FAILED: XBSTREAM command.")
                                    logger.error(output)
                                    raise RuntimeError("FAILED: XBSTREAM command.")

                        # Decrypt backup
                        self.decrypt_backup(self.inc_dir, inc_backup_dir)

                        # Decompress backup
                        self.decompress_backup(self.inc_dir, inc_backup_dir)

                        # Prepare command
                        xtrabackup_prepare_cmd = self.prepare_command_builder(full_backup=recent_bck,
                                                                              incremental=inc_backup_dir)

                    logger.info("Running prepare command -> {}".format(xtrabackup_prepare_cmd))
                    if self.dry == 0:
                        status = ProcessRunner.run_command(xtrabackup_prepare_cmd)
                        if not status:
                            logger.error("FAILED: Incremental BACKUP prepare")
                            raise RuntimeError("FAILED: Incremental BACKUP prepare")

            logger.info("- - - - The end of the Prepare Stage. - - - -")
            return True

    ##########################################################################
    # COPY-BACK PREPARED BACKUP
    ##########################################################################

    def shutdown_mysql(self):
        # Shut Down MySQL
        logger.info("Shutting Down MySQL server:")
        args = self.stop_mysql
        status, output = subprocess.getstatusoutput(args)
        if status == 0:
            logger.info(output)
            return True
        else:
            logger.error("Could not Shutdown MySQL!. Refer to MySQL error log")
            logger.error(output)
            raise RuntimeError("FAILED: Shutdown MySQL -> {}".format(output))

    def move_datadir(self):
        # Move datadir to new directory
        logger.info("Moving MySQL datadir to {}".format(self.tmpdir))
        if os.path.isdir(self.tmpdir):
            rmdirc = 'rm -rf {}'.format(self.tmpdir)
            status, output = subprocess.getstatusoutput(rmdirc)
            if status == 0:
                logger.info("Emptied {} directory ...".format(self.tmpdir))
                try:
                    shutil.move(self.datadir, self.tmpdir)
                    logger.info("Moved datadir to {} ...".format(self.tmpdir))
                except shutil.Error as err:
                    logger.error("Error occurred while moving datadir")
                    logger.error(err)
                    return False

                logger.info("Creating an empty data directory ...")
                makedir = "mkdir {}".format(self.datadir)
                status2, output2 = subprocess.getstatusoutput(makedir)
                if status2 == 0:
                    logger.info("Datadir is Created! ...")
                else:
                    logger.error("Error while creating datadir")
                    logger.error(output2)
                    return False

                return True

            else:
                logger.error("Could not delete {} directory".format(self.tmpdir))
                logger.error(output)
                return False

        else:
            try:
                shutil.move(self.datadir, self.tmpdir)
                logger.info("Moved datadir to {} ...".format(self.tmpdir))
            except shutil.Error as err:
                logger.error("Error occurred while moving datadir")
                logger.error(err)
                return False

            logger.info("Creating an empty data directory ...")
            makedir = "mkdir {}".format(self.datadir)
            status2, output2 = subprocess.getstatusoutput(makedir)
            if status2 == 0:
                logger.info("Datadir is Created! ...")
                return True
            else:
                logger.error("Error while creating datadir")
                logger.error(output2)
                return False

    def run_xtra_copyback(self, datadir=None):
        # Running Xtrabackup with --copy-back option
        copy_back = '{} --copy-back {} --target-dir={}/{} --datadir={}'.format(
            self.backup_tool,
            self.xtra_options,
            self.full_dir,
            helpers.get_latest_dir_name(self.full_dir)
,
            self.datadir if datadir is None else datadir)
        status = ProcessRunner.run_command(copy_back)
        if status:
            logger.info("Data copied back successfully!")
            return True
        else:
            logger.error("Error occurred while copying back data!")
            raise RuntimeError("Error occurred while copying back data!")

    def giving_chown(self, datadir=None):
        # Changing owner of datadir to given user:group
        give_chown = "{} {}".format(self.chown_command, self.datadir if datadir is None else datadir)
        status, output = subprocess.getstatusoutput(give_chown)
        if status == 0:
            logger.info("New copied-back data now owned by specified user!")
            return True
        else:
            logger.error("Error occurred while changing owner!")
            logger.error(output)
            raise RuntimeError("Error occurred while changing owner!")

    def start_mysql_func(self, start_tool=None, options=None):
        # Starting MySQL
        logger.info("Starting MySQL server: ")
        args = self.start_mysql if start_tool is None else start_tool
        start_command = '{} {}'.format(args, options) if options is not None else args
        status, output = subprocess.getstatusoutput(start_command)
        if status == 0:
            logger.info("Starting MySQL ...")
            logger.info(output)
            return True
        else:
            logger.error("Error occurred while starting MySQL!")
            logger.error(output)
            raise RuntimeError("Error occurred while starting MySQL!")

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

    def copy(self, options=None, datadir=None):
        """
        Function for running:
          xtrabackup --copy-back
          giving chown to datadir
          starting mysql
        :return: True if succeeded. Error if failed
        """
        logger.info("Copying Back Already Prepared Final Backup:")
        if len(os.listdir(self.datadir if datadir is None else datadir)) > 0:
            logger.info("MySQL Datadir is not empty!")
            return False
        else:
            self.run_xtra_copyback(datadir=datadir)
            self.giving_chown(datadir=datadir)
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
            if self.move_datadir() and self.copy(options=options):
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
