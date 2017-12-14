# Backup Prepare and Copy-Back Script
# Originally Developed by
# Shahriyar Rzayev -> http://www.mysql.az
# / rzayev.sehriyar@gmail.com / rzayev.shahriyar@yandex.com


import os
import subprocess
import shutil
import time
from general_conf.generalops import GeneralClass
from os.path import isfile

import logging
logger = logging.getLogger(__name__)


class Prepare(GeneralClass):

    def __init__(self, config="/etc/bck.conf", dry_run=0, tag=None):
        self.conf = config
        self.dry = dry_run
        self.tag = tag
        GeneralClass.__init__(self, self.conf)
        # If prepare_tool option enabled in config, make backup_tool to use this.
        if hasattr(self, 'prepare_tool'):
            self.backup_tool = self.prepare_tool
        if self.tag is not None:
            if not os.path.isfile("{}/backup_tags.txt".format(self.backupdir)):
                raise RuntimeError("Could not find backup_tags.txt inside backup directory. "
                                   "Please run without --tag option")

    def recent_full_backup_file(self):
        # Return last full backup dir name

        if len(os.listdir(self.full_dir)) > 0:
            return max(os.listdir(self.full_dir))
        else:
            raise RuntimeError("The full backup directory is empty, it seems you have not backups")

    def check_inc_backups(self):
        # Check for Incremental backups

        if len(os.listdir(self.inc_dir)) > 0:
            return 1
        return 0

    @staticmethod
    def parse_backup_tags(backup_dir, tag_name):
        '''
        Static Method for returning the backup directory name and backup type
        :param backup_dir: The backup directory path
        :param tag_name: The tag name to search
        :return: Tuple of (backup directory, backup type) (2017-11-09_19-37-16, Full).
        :raises: RuntimeError if there is no such tag inside backup_tags.txt
        '''
        if os.path.isfile("{}/backup_tags.txt".format(backup_dir)):
            with open('{}/backup_tags.txt'.format(backup_dir), 'r') as bcktags:
                f = bcktags.readlines()

            for i in f:
                splitted = i.split('\t')
                if tag_name == splitted[-1].rstrip("'\n\r").lstrip("'"):
                    return splitted[0], splitted[1]
            raise RuntimeError('There is no such tag for backups')

    def prepare_with_tags(self):
        # Method for preparing backups based on passed backup tags
        found_backups = Prepare.parse_backup_tags(backup_dir=self.backupdir, tag_name=self.tag)
        if found_backups[1] == 'Full':
            # Prepare only full backup because specified tag is for full backup
            if self.recent_full_backup_file():
                logger.debug("- - - - Preparing Full Backup - - - -")

                # Extract and decrypt streamed full backup prior to executing incremental backup
                if hasattr(self, 'stream') \
                        and hasattr(self, 'encrypt') \
                        and hasattr(self, 'xbs_decrypt'):
                    logger.debug("Using xbstream to extract and decrypt from full_backup.stream!")
                    xbstream_command = "{} {} --decrypt={} --encrypt-key={} --encrypt-threads={} " \
                                       "< {}/{}/full_backup.stream -C {}/{}".format(
                        self.xbstream,
                        self.xbstream_options,
                        self.decrypt,
                        self.encrypt_key,
                        self.encrypt_threads,
                        self.full_dir,
                        self.recent_full_backup_file(),
                        self.full_dir,
                        self.recent_full_backup_file())

                    logger.debug("The following xbstream command will be executed {}".format(xbstream_command))
                    if self.dry == 0 and isfile("{}/{}/full_backup.stream".format(
                            self.full_dir, self.recent_full_backup_file())):
                        status, output = subprocess.getstatusoutput(xbstream_command)
                        if status == 0:
                            logger.debug("OK: XBSTREAM command succeeded.")
                        else:
                            logger.error("FAILED: XBSTREAM command.")
                            logger.error(output)
                            raise RuntimeError("FAILED: XBSTREAM command.")

                # Extract streamed full backup prior to executing incremental backup
                elif hasattr(self, 'stream'):
                    logger.debug("Using xbstream to extract from full_backup.stream!")
                    xbstream_command = "{} {} < {}/{}/full_backup.stream -C {}/{}".format(
                        self.xbstream,
                        self.xbstream_options,
                        self.full_dir,
                        self.recent_full_backup_file(),
                        self.full_dir,
                        self.recent_full_backup_file())

                    logger.debug("The following xbstream command will be executed {}".format(xbstream_command))

                    if self.dry == 0 and isfile("{}/{}/full_backup.stream".format(
                            self.full_dir, self.recent_full_backup_file())):
                        status, output = subprocess.getstatusoutput(xbstream_command)
                        if status == 0:
                            logger.debug("OK: XBSTREAM command succeeded.")
                        else:
                            logger.error("FAILED: XBSTREAM command.")
                            logger.error(output)
                            raise RuntimeError("FAILED: XBSTREAM command.")

                # Check if decryption enabled
                if hasattr(self, 'decrypt'):
                    if hasattr(self, 'remove_original_enc') and self.remove_original_enc:
                        decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{} --remove-original".format(
                            self.backup_tool,
                            self.decrypt,
                            self.encrypt_key,
                            self.full_dir,
                            self.recent_full_backup_file())
                    else:
                        decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{}".format(
                            self.backup_tool,
                            self.decrypt,
                            self.encrypt_key,
                            self.full_dir,
                            self.recent_full_backup_file())
                    logger.debug("Trying to decrypt backup")
                    logger.debug("Running decrypt command -> {}".format(decr))
                    if self.dry == 0:
                        status, output = subprocess.getstatusoutput(decr)
                        if status == 0:
                            logger.debug(output[-27:])
                            logger.debug("OK: Decrypted!")
                        else:
                            logger.error("FAILED: FULL BACKUP decrypt")
                            logger.error(output)
                            raise RuntimeError("FAILED: FULL BACKUP decrypt")

                # Check if decompression enabled
                if hasattr(self, 'decompress'):
                    if hasattr(self, 'remove_original_comp') and self.remove_original_comp:
                        decmp = "{} --decompress={} --target-dir={}/{} --remove-original".format(
                            self.backup_tool,
                            self.decompress,
                            self.full_dir,
                            self.recent_full_backup_file())
                    else:
                        decmp = "{} --decompress={} --target-dir={}/{} --remove-original".format(
                            self.backup_tool,
                            self.decompress,
                            self.full_dir,
                            self.recent_full_backup_file())
                    logger.debug("Trying to decompress backup")
                    logger.debug("Running decompress command -> {}".format(decmp))
                    if self.dry == 0:
                        status, output = subprocess.getstatusoutput(decmp)
                        if status == 0:
                            logger.debug(output[-27:])
                            logger.debug("OK: Decompressed")
                        else:
                            logger.error("FAILED: FULL BACKUP decompression")
                            logger.error(output)
                            raise RuntimeError("FAILED: FULL BACKUP decompression")

                # Actual prepare command goes here
                args = "{} --prepare --target-dir={}/{}".format(
                    self.backup_tool,
                    self.full_dir,
                    self.recent_full_backup_file())

                # Checking if extra options were passed:
                if hasattr(self, 'xtra_options'):
                    args += " "
                    args += self.xtra_options

                # Checking of extra prepare options were passed:
                if hasattr(self, 'xtra_prepare_options'):
                    args += " "
                    args += self.xtra_prepare_options

                logger.debug("Running prepare command -> {}".format(args))
                if self.dry == 0:
                    status, output = subprocess.getstatusoutput(args)
                    if status == 0:
                        logger.debug(output)
                        # logger.debug(output[-27:])
                    else:
                        logger.error("FAILED: FULL BACKUP prepare.")
                        logger.error(output)
                        raise RuntimeError("FAILED: FULL BACKUP prepare.")
        elif found_backups[1] == 'Inc':
            if self.check_inc_backups() == 0:
                logger.debug("- - - - You have no Incremental backups. So will prepare only latest Full backup - - - -")
                self.prepare_only_full_backup()
            else:
                logger.debug("- - - - You have Incremental backups. - - - -")
                if self.prepare_only_full_backup():
                    logger.debug("Preparing Incs: ")
                    list_of_dir = sorted(os.listdir(self.inc_dir))
                    # Find the index number inside all list for backup(which was found via tag)
                    index_num = list_of_dir.index(found_backups[0])
                    # Limit the iteration until this found backup
                    for i in list_of_dir[:index_num+1]:
                        if i != found_backups[0]:
                            logger.debug("Preparing inc backups in sequence. inc backup dir/name is {}".format(i))
                            # Check if decryption enabled
                            if hasattr(self, 'decrypt'):
                                if hasattr(self, 'remove_original_enc') and self.remove_original_enc:
                                    decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{} --remove-original".format(
                                        self.backup_tool,
                                        self.decrypt,
                                        self.encrypt_key,
                                        self.inc_dir,
                                        i)
                                else:
                                    decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{}".format(
                                        self.backup_tool,
                                        self.decrypt,
                                        self.encrypt_key,
                                        self.inc_dir,
                                        i)
                                logger.debug("Trying to decrypt backup")
                                logger.debug("Running decrypt command -> {}".format(decr))
                                if self.dry == 0:
                                    status, output = subprocess.getstatusoutput(decr)
                                    if status == 0:
                                        logger.debug(output[-27:])
                                        logger.debug("OK: Decrypted!")
                                    else:
                                        logger.error("FAILED: FULL BACKUP decrypt.")
                                        logger.error(output)
                                        raise RuntimeError("FAILED: FULL BACKUP decrypt.")

                            # Check if decompression enabled, if it is, decompress
                            # backup prior prepare
                            if hasattr(self, 'decompress'):
                                if hasattr(self, 'remove_original_comp') and self.remove_original_comp:
                                    decmp = "{} --decompress={} --target-dir={}/{} --remove-original".format(
                                        self.backup_tool,
                                        self.decompress,
                                        self.inc_dir,
                                        i)
                                else:
                                    decmp = "{} --decompress={} --target-dir={}/{}".format(
                                        self.backup_tool,
                                        self.decompress,
                                        self.inc_dir,
                                        i)
                                logger.debug("Trying to decompress backup")
                                logger.debug(
                                    "Running decompress command -> {}".format(decmp))
                                if self.dry == 0:
                                    status, output = subprocess.getstatusoutput(decmp)
                                    if status == 0:
                                        logger.debug(output[-27:])
                                        logger.debug("OK: Decompressed")
                                    else:
                                        logger.error("FAILED: INCREMENTAL BACKUP decompression.")
                                        logger.error(output)
                                        raise RuntimeError("FAILED: INCREMENTAL BACKUP decompression.")

                            # Actual prepare command goes here
                            args = '{} --prepare {} --target-dir={}/{} --incremental-dir={}/{}'.format(
                                self.backup_tool,
                                self.xtrabck_prepare,
                                self.full_dir,
                                self.recent_full_backup_file(),
                                self.inc_dir,
                                i)

                            # Checking if extra options were passed:
                            if hasattr(self, 'xtra_options'):
                                args += " "
                                args += self.xtra_options

                            # Checking of extra prepare options were passed:
                            if hasattr(self, 'xtra_prepare_options'):
                                args += " "
                                args += self.xtra_prepare_options

                            logger.debug("Running prepare command -> {}".format(args))
                            if self.dry == 0:
                                status, output = subprocess.getstatusoutput(args)
                                if status == 0:
                                    logger.debug(output)
                                    # logger.debug(output[-27:])
                                else:
                                    logger.error("FAILED: Incremental BACKUP prepare")
                                    logger.error(output)
                                    raise RuntimeError("FAILED: Incremental BACKUP prepare")

                        else:
                            logger.debug("Preparing last incremental backup, inc backup dir/name is {}".format(i))
                            # Extracting streamed incremental backup prior to preparing

                            if hasattr(self, 'stream'):
                                logger.debug("Using xbstream to extract from inc_backup.stream!")
                                xbstream_command = "{} {} < {}/{}/inc_backup.stream -C {}/{}".format(
                                    self.xbstream,
                                    self.xbstream_options,
                                    self.inc_dir,
                                    i,
                                    self.inc_dir,
                                    i)

                                logger.debug(
                                    "The following xbstream command will be executed {}".format(xbstream_command))
                                if self.dry == 0 and isfile("{}/{}/inc_backup.stream".format(self.inc_dir, i)):
                                    status, output = subprocess.getstatusoutput(xbstream_command)
                                    if status == 0:
                                        logger.debug("OK: XBSTREAM command succeeded.")
                                    else:
                                        logger.error("FAILED: XBSTREAM command.")
                                        logger.error(output)
                                        raise RuntimeError("FAILED: XBSTREAM command.")

                            # Check if decryption enabled
                            if hasattr(self, 'decrypt'):
                                if hasattr(self, 'remove_original_enc') and self.remove_original_enc:
                                    decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{} --remove-original".format(
                                        self.backup_tool,
                                        self.decrypt,
                                        self.encrypt_key,
                                        self.inc_dir,
                                        i)
                                else:
                                    decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{}".format(
                                        self.backup_tool,
                                        self.decrypt,
                                        self.encrypt_key,
                                        self.inc_dir,
                                        i)

                                logger.debug("Trying to decrypt backup")
                                logger.debug("Running decrypt command -> {}".format(decr))
                                if self.dry == 0:
                                    status, output = subprocess.getstatusoutput(decr)
                                    if status == 0:
                                        logger.debug(output[-27:])
                                        logger.debug("OK: Decrypted!")
                                    else:
                                        logger.error("FAILED: FULL BACKUP decrypt.")
                                        logger.error(output)
                                        raise RuntimeError

                            # Check if decompression enabled, if it is, decompress
                            # backup prior prepare
                            if hasattr(self, 'decompress'):
                                if hasattr(self, 'remove_original_comp') and self.remove_original_comp:
                                    decmp = "{} --decompress={} --target-dir={}/{} --remove-original".format(
                                        self.backup_tool,
                                        self.decompress,
                                        self.inc_dir,
                                        i)
                                else:
                                    decmp = "{} --decompress={} --target-dir={}/{}".format(
                                        self.backup_tool,
                                        self.decompress,
                                        self.inc_dir,
                                        i)
                                logger.debug("Trying to decompress backup")
                                logger.debug("Running decompress command -> {}".format(decmp))

                                if self.dry == 0:
                                    status, output = subprocess.getstatusoutput(decmp)
                                    if status == 0:
                                        logger.debug(output[-27:])
                                        logger.debug("OK: Decompressed")
                                    else:
                                        logger.error("FAILED: INCREMENTAL BACKUP decompression")
                                        logger.error(output)
                                        raise RuntimeError("FAILED: INCREMENTAL BACKUP decompression")

                            args2 = '{} --prepare --target-dir={}/{} --incremental-dir={}/{}'.format(
                                self.backup_tool,
                                self.full_dir,
                                self.recent_full_backup_file(),
                                self.inc_dir,
                                i)

                            # Checking if extra options were passed:
                            if hasattr(self, 'xtra_options'):
                                args2 += " "
                                args2 += self.xtra_options

                            # Checking of extra prepare options were passed:
                            if hasattr(self, 'xtra_prepare_options'):
                                args2 += " "
                                args2 += self.xtra_prepare_options

                            logger.debug("Running prepare command -> {}".format(args2))
                            if self.dry == 0:
                                status2, output2 = subprocess.getstatusoutput(args2)
                                if status2 == 0:
                                    logger.debug(output2)
                                    # logger.debug(output2[-27:])
                                else:
                                    logger.error("FAILED: Incremental BACKUP prepare")
                                    logger.error(output2)
                                    raise RuntimeError("FAILED: Incremental BACKUP prepare")

        logger.debug("- - - - The end of the Prepare Stage. - - - -")
    ##########################################################################
    # PREPARE ONLY FULL BACKUP
    ##########################################################################

    def prepare_only_full_backup(self):
        recent_bck = self.recent_full_backup_file()
        if recent_bck:
            if self.check_inc_backups() == 0:
                logger.debug("- - - - Preparing Full Backup - - - -")
                if hasattr(self, 'stream') and self.stream == 'tar':
                    untar_cmd = "tar -xf {}/{}/full_backup.tar -C {}/{}".format(self.full_dir,
                                                                                recent_bck,
                                                                                self.full_dir,
                                                                                recent_bck)
                    logger.debug("The following tar command will be executed -> {}".format(untar_cmd))
                    if self.dry == 0 and isfile("{}/{}/full_backup.tar".format(self.full_dir, recent_bck)):
                        status, output = subprocess.getstatusoutput(untar_cmd)
                        if status == 0:
                            logger.debug("OK: extracting full backup from tar.")
                        else:
                            logger.error("FAILED: extracting full backup from tar")
                            logger.error(output)
                            raise RuntimeError("FAILED: extracting full backup from tar")

                # Extract and decrypt streamed full backup prior to executing incremental backup
                if hasattr(self, 'stream') and self.stream == 'xbstream' \
                        and hasattr(self, 'encrypt') \
                        and hasattr(self, 'xbs_decrypt'):
                    logger.debug("Using xbstream to extract and decrypt from full_backup.stream!")
                    xbstream_command = "{} {} --decrypt={} --encrypt-key={} --encrypt-threads={} " \
                                       "< {}/{}/full_backup.stream -C {}/{}".format(
                                           self.xbstream,
                                           self.xbstream_options,
                                           self.decrypt,
                                           self.encrypt_key,
                                           self.encrypt_threads,
                                           self.full_dir,
                                           recent_bck,
                                           self.full_dir,
                                           recent_bck)

                    logger.debug("The following xbstream command will be executed {}".format(xbstream_command))
                    if self.dry == 0 and isfile("{}/{}/full_backup.stream".format(
                                                self.full_dir, recent_bck)):
                        status, output = subprocess.getstatusoutput(xbstream_command)
                        if status == 0:
                            logger.debug("OK: XBSTREAM command succeeded.")
                        else:
                            logger.error("FAILED: XBSTREAM command.")
                            logger.error(output)
                            raise RuntimeError("FAILED: XBSTREAM command.")

                # Extract streamed full backup prior to executing incremental backup
                elif hasattr(self, 'stream') and self.stream == 'xbstream':
                    logger.debug("Using xbstream to extract from full_backup.stream!")
                    xbstream_command = "{} {} < {}/{}/full_backup.stream -C {}/{}".format(
                                        self.xbstream,
                                        self.xbstream_options,
                                        self.full_dir,
                                        recent_bck,
                                        self.full_dir,
                                        recent_bck)

                    logger.debug("The following xbstream command will be executed {}".format(xbstream_command))

                    if self.dry == 0 and isfile("{}/{}/full_backup.stream".format(
                                                self.full_dir, recent_bck)):
                        status, output = subprocess.getstatusoutput(xbstream_command)
                        if status == 0:
                            logger.debug("OK: XBSTREAM command succeeded.")
                        else:
                            logger.error("FAILED: XBSTREAM command.")
                            logger.error(output)
                            raise RuntimeError("FAILED: XBSTREAM command.")

                # Check if decryption enabled
                if hasattr(self, 'decrypt'):
                    if hasattr(self, 'remove_original_enc') and self.remove_original_enc:
                        decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{} --remove-original".format(
                                self.backup_tool,
                                self.decrypt,
                                self.encrypt_key,
                                self.full_dir,
                                recent_bck)
                    else:
                        decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{}".format(
                                 self.backup_tool,
                                 self.decrypt,
                                 self.encrypt_key,
                                 self.full_dir,
                                 recent_bck)
                    logger.debug("Trying to decrypt backup")
                    logger.debug("Running decrypt command -> {}".format(decr))
                    if self.dry == 0:
                        status, output = subprocess.getstatusoutput(decr)
                        if status == 0:
                            logger.debug(output[-27:])
                            logger.debug("OK: Decrypted!")
                        else:
                            logger.error("FAILED: FULL BACKUP decrypt")
                            logger.error(output)
                            raise RuntimeError("FAILED: FULL BACKUP decrypt")

                # Check if decompression enabled
                if hasattr(self, 'decompress'):
                    if hasattr(self, 'remove_original_comp') and self.remove_original_comp:
                        decmp = "{} --decompress={} --target-dir={}/{} --remove-original".format(
                                 self.backup_tool,
                                 self.decompress,
                                 self.full_dir,
                                 recent_bck)
                    else:
                        decmp = "{} --decompress={} --target-dir={}/{} --remove-original".format(
                                 self.backup_tool,
                                 self.decompress,
                                 self.full_dir,
                                 recent_bck)
                    logger.debug("Trying to decompress backup")
                    logger.debug("Running decompress command -> {}".format(decmp))
                    if self.dry == 0:
                        status, output = subprocess.getstatusoutput(decmp)
                        if status == 0:
                            logger.debug(output[-27:])
                            logger.debug("OK: Decompressed")
                        else:
                            logger.error("FAILED: FULL BACKUP decompression")
                            logger.error(output)
                            raise RuntimeError("FAILED: FULL BACKUP decompression")

                # Actual prepare command goes here
                args = "{} --prepare --target-dir={}/{}".format(
                        self.backup_tool,
                        self.full_dir,
                        recent_bck)

                # Checking if extra options were passed:
                if hasattr(self, 'xtra_options'):
                    args += " "
                    args += self.xtra_options

                # Checking of extra prepare options were passed:
                if hasattr(self, 'xtra_prepare_options'):
                    args += " "
                    args += self.xtra_prepare_options

                logger.debug("Running prepare command -> {}".format(args))
                if self.dry == 0:
                    status, output = subprocess.getstatusoutput(args)
                    if status == 0:
                        logger.debug(output)
                        # logger.debug(output[-27:])
                    else:
                        logger.error("FAILED: FULL BACKUP prepare.")
                        logger.error(output)
                        raise RuntimeError("FAILED: FULL BACKUP prepare.")

            else:
                logger.debug("- - - - Preparing Full backup for incrementals - - - -")
                logger.debug("- - - - Final prepare,will occur after preparing all inc backups - - - -")
                time.sleep(3)

                # Check if decryption enabled
                if hasattr(self, 'decrypt'):
                    if hasattr(self, 'remove_original_enc') and self.remove_original_enc:
                        decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{} --remove-original".format(
                                self.backup_tool,
                                self.decrypt,
                                self.encrypt_key,
                                self.full_dir,
                                self.recent_full_backup_file())
                    else:
                        decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{}".format(
                                 self.backup_tool,
                                 self.decrypt,
                                 self.encrypt_key,
                                 self.full_dir,
                                 self.recent_full_backup_file())
                    logger.debug("Trying to decrypt backup")
                    logger.debug("Running decrypt command -> {}".format(decr))
                    if self.dry == 0:
                        status, output = subprocess.getstatusoutput(decr)
                        if status == 0:
                            logger.debug(output[-27:])
                            logger.debug("OK: Decrypted!")
                        else:
                            logger.error("FAILED: FULL BACKUP decrypt.")
                            logger.error(output)
                            raise RuntimeError("FAILED: FULL BACKUP decrypt.")

                # Check if decompression enabled, if it is, decompress backup prior
                # prepare
                if hasattr(self, 'decompress'):
                    if hasattr(self, 'remove_original_comp') and self.remove_original_comp:
                        decmp = "{} --decompress={} --target-dir={}/{} --remove-original".format(
                                 self.backup_tool,
                                 self.decompress,
                                 self.full_dir,
                                 self.recent_full_backup_file())
                    else:
                        decmp = "{} --decompress={} --target-dir={}/{}".format(
                                 self.backup_tool,
                                 self.decompress,
                                 self.full_dir,
                                 self.recent_full_backup_file())
                    logger.debug("Trying to decompress backup")
                    logger.debug("Running decompress command -> {}".format(decmp))
                    if self.dry == 0:
                        status, output = subprocess.getstatusoutput(decmp)
                        if status == 0:
                            logger.debug(output[-27:])
                            logger.debug("OK: Decompressed")
                        else:
                            logger.error("FAILED: FULL BACKUP decompression.")
                            logger.error(output)
                            raise RuntimeError("FAILED: FULL BACKUP decompression.")

                # Actual prepare command goes here
                args = '{} --prepare {} --target-dir={}/{}'.format(
                        self.backup_tool,
                        self.xtrabck_prepare,
                        self.full_dir,
                        self.recent_full_backup_file())

                # Checking if extra options were passed:
                if hasattr(self, 'xtra_options'):
                    args += " "
                    args += self.xtra_options

                # Checking of extra prepare options were passed:
                if hasattr(self, 'xtra_prepare_options'):
                    args += " "
                    args += self.xtra_prepare_options

                logger.debug("Running prepare command -> {}".format(args))
                if self.dry == 0:
                    status, output = subprocess.getstatusoutput(args)
                    if status == 0:
                        logger.debug(output)
                        # logger.debug(output[-27:])
                        return True
                    else:
                        logger.error("FAILED: One time FULL BACKUP")
                        logger.error(output)
                        raise RuntimeError("FAILED: One time FULL BACKUP")
                else:
                    return True

    ##########################################################################
    # PREPARE INC BACKUPS
    ##########################################################################

    def prepare_inc_full_backups(self):
        if self.check_inc_backups() == 0:
            logger.debug("- - - - You have no Incremental backups. So will prepare only latest Full backup - - - -")
            self.prepare_only_full_backup()
        else:
            logger.debug("- - - - You have Incremental backups. - - - -")
            if self.prepare_only_full_backup():
                logger.debug("Preparing Incs: ")
                list_of_dir = sorted(os.listdir(self.inc_dir))
                for i in list_of_dir:
                    if i != max(os.listdir(self.inc_dir)):
                        logger.debug("Preparing inc backups in sequence. inc backup dir/name is {}".format(i))
                        # Check if decryption enabled
                        if hasattr(self, 'decrypt'):
                            if hasattr(self, 'remove_original_enc') and self.remove_original_enc:
                                decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{} --remove-original".format(
                                        self.backup_tool,
                                        self.decrypt,
                                        self.encrypt_key,
                                        self.inc_dir,
                                        i)
                            else:
                                decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{}".format(
                                         self.backup_tool,
                                         self.decrypt,
                                         self.encrypt_key,
                                         self.inc_dir,
                                         i)                                
                            logger.debug("Trying to decrypt backup")
                            logger.debug("Running decrypt command -> {}".format(decr))
                            if self.dry == 0:
                                status, output = subprocess.getstatusoutput(decr)
                                if status == 0:
                                    logger.debug(output[-27:])
                                    logger.debug("OK: Decrypted!")
                                else:
                                    logger.error("FAILED: FULL BACKUP decrypt.")
                                    logger.error(output)
                                    raise RuntimeError("FAILED: FULL BACKUP decrypt.")

                        # Check if decompression enabled, if it is, decompress
                        # backup prior prepare
                        if hasattr(self, 'decompress'):
                            if hasattr(self, 'remove_original_comp') and self.remove_original_comp:
                                decmp = "{} --decompress={} --target-dir={}/{} --remove-original".format(
                                         self.backup_tool,
                                         self.decompress,
                                         self.inc_dir,
                                         i)
                            else:
                                decmp = "{} --decompress={} --target-dir={}/{}".format(
                                         self.backup_tool,
                                         self.decompress,
                                         self.inc_dir,
                                         i)                                
                            logger.debug("Trying to decompress backup")
                            logger.debug(
                                "Running decompress command -> {}".format(decmp))
                            if self.dry == 0:
                                status, output = subprocess.getstatusoutput(decmp)
                                if status == 0:
                                    logger.debug(output[-27:])
                                    logger.debug("OK: Decompressed")
                                else:
                                    logger.error("FAILED: INCREMENTAL BACKUP decompression.")
                                    logger.error(output)
                                    raise RuntimeError("FAILED: INCREMENTAL BACKUP decompression.")
                                                   
                        # Actual prepare command goes here
                        args = '{} --prepare {} --target-dir={}/{} --incremental-dir={}/{}'.format(
                             self.backup_tool,
                             self.xtrabck_prepare,
                             self.full_dir,
                             self.recent_full_backup_file(),
                             self.inc_dir,
                             i)
                        
                        # Checking if extra options were passed:
                        if hasattr(self, 'xtra_options'):
                            args += " "
                            args += self.xtra_options

                        # Checking of extra prepare options were passed:
                        if hasattr(self, 'xtra_prepare_options'):
                            args += " "
                            args += self.xtra_prepare_options

                        logger.debug("Running prepare command -> {}".format(args))
                        if self.dry == 0:
                            status, output = subprocess.getstatusoutput(args)
                            if status == 0:
                                logger.debug(output)
                                # logger.debug(output[-27:])
                            else:
                                logger.error("FAILED: Incremental BACKUP prepare")
                                logger.error(output)
                                raise RuntimeError("FAILED: Incremental BACKUP prepare")

                    else:
                        logger.debug("Preparing last incremental backup, inc backup dir/name is {}".format(i))
                        # Extracting streamed incremental backup prior to preparing

                        if hasattr(self, 'stream'):
                            logger.debug("Using xbstream to extract from inc_backup.stream!")
                            xbstream_command = "{} {} < {}/{}/inc_backup.stream -C {}/{}".format(
                                                self.xbstream,
                                                self.xbstream_options,
                                                self.inc_dir,
                                                i,
                                                self.inc_dir,
                                                i)

                            logger.debug("The following xbstream command will be executed {}".format(xbstream_command))
                            if self.dry == 0 and isfile("{}/{}/inc_backup.stream".format(self.inc_dir, i)):
                                status, output = subprocess.getstatusoutput(xbstream_command)
                                if status == 0:
                                    logger.debug("OK: XBSTREAM command succeeded.")
                                else:
                                    logger.error("FAILED: XBSTREAM command.")
                                    logger.error(output)
                                    raise RuntimeError("FAILED: XBSTREAM command.")

                        # Check if decryption enabled
                        if hasattr(self, 'decrypt'):
                            if hasattr(self, 'remove_original_enc') and self.remove_original_enc:
                                decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{} --remove-original".format(
                                        self.backup_tool,
                                        self.decrypt,
                                        self.encrypt_key,
                                        self.inc_dir,
                                        i)
                            else:
                                decr = "{} --decrypt={} --encrypt-key={} --target-dir={}/{}".format(
                                                                    self.backup_tool,
                                                                    self.decrypt,
                                                                    self.encrypt_key,
                                                                    self.inc_dir,
                                                                    i)                                

                            logger.debug("Trying to decrypt backup")
                            logger.debug("Running decrypt command -> {}".format(decr))
                            if self.dry == 0:
                                status, output = subprocess.getstatusoutput(decr)
                                if status == 0:
                                    logger.debug(output[-27:])
                                    logger.debug("OK: Decrypted!")
                                else:
                                    logger.error("FAILED: FULL BACKUP decrypt.")
                                    logger.error(output)
                                    raise RuntimeError

                        # Check if decompression enabled, if it is, decompress
                        # backup prior prepare
                        if hasattr(self, 'decompress'):
                            if hasattr(self, 'remove_original_comp') and self.remove_original_comp:
                                decmp = "{} --decompress={} --target-dir={}/{} --remove-original".format(
                                         self.backup_tool,
                                         self.decompress,
                                         self.inc_dir,
                                         i)
                            else:
                                decmp = "{} --decompress={} --target-dir={}/{}".format(
                                         self.backup_tool,
                                         self.decompress,
                                         self.inc_dir,
                                         i)                                
                            logger.debug("Trying to decompress backup")
                            logger.debug("Running decompress command -> {}".format(decmp))

                            if self.dry == 0:
                                status, output = subprocess.getstatusoutput(decmp)
                                if status == 0:
                                    logger.debug(output[-27:])
                                    logger.debug("OK: Decompressed")
                                else:
                                    logger.error("FAILED: INCREMENTAL BACKUP decompression")
                                    logger.error(output)
                                    raise RuntimeError("FAILED: INCREMENTAL BACKUP decompression")

                        args2 = '{} --prepare --target-dir={}/{} --incremental-dir={}/{}'.format(
                                self.backup_tool,
                                self.full_dir,
                                self.recent_full_backup_file(),
                                self.inc_dir,
                                i)
                        
                        # Checking if extra options were passed:
                        if hasattr(self, 'xtra_options'):
                            args2 += " "
                            args2 += self.xtra_options

                        # Checking of extra prepare options were passed:
                        if hasattr(self, 'xtra_prepare_options'):
                            args2 += " "
                            args2 += self.xtra_prepare_options

                        logger.debug("Running prepare command -> {}".format(args2))
                        if self.dry == 0:
                            status2, output2 = subprocess.getstatusoutput(args2)
                            if status2 == 0:
                                logger.debug(output2)
                                # logger.debug(output2[-27:])
                            else:
                                logger.error("FAILED: Incremental BACKUP prepare")
                                logger.error(output2)
                                raise RuntimeError("FAILED: Incremental BACKUP prepare")

            logger.debug("- - - - The end of the Prepare Stage. - - - -")

    ##########################################################################
    # COPY-BACK PREPARED BACKUP
    ##########################################################################

    def shutdown_mysql(self):
        # Shut Down MySQL
        logger.debug("Shutting Down MySQL server:")
        args = self.stop_mysql
        status, output = subprocess.getstatusoutput(args)
        if status == 0:
            logger.debug(output)
            return True
        else:
            logger.error("Could not Shutdown MySQL!. Refer to MySQL error log")
            logger.error(output)
            raise RuntimeError("FAILED: Shutdown MySQL -> {}".format(output))

    def move_datadir(self):
        # Move datadir to new directory
        logger.debug("Moving MySQL datadir to {}".format(self.tmpdir))
        if os.path.isdir(self.tmpdir):
            rmdirc = 'rm -rf {}'.format(self.tmpdir)
            status, output = subprocess.getstatusoutput(rmdirc)
            if status == 0:
                logger.debug("Emptied {} directory ...".format(self.tmpdir))
                try:
                    shutil.move(self.datadir, self.tmpdir)
                    logger.debug("Moved datadir to {} ...".format(self.tmpdir))
                except shutil.Error as err:
                    logger.error("Error occurred while moving datadir")
                    logger.error(err)
                    return False

                logger.debug("Creating an empty data directory ...")
                makedir = "mkdir {}".format(self.datadir)
                status2, output2 = subprocess.getstatusoutput(makedir)
                if status2 == 0:
                    logger.debug("Datadir is Created! ...")
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
                logger.debug("Moved datadir to {} ...".format(self.tmpdir))
            except shutil.Error as err:
                logger.error("Error occurred while moving datadir")
                logger.error(err)
                return False

            logger.debug("Creating an empty data directory ...")
            makedir = "mkdir {}".format(self.datadir)
            status2, output2 = subprocess.getstatusoutput(makedir)
            if status2 == 0:
                logger.debug("Datadir is Created! ...")
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
                    self.recent_full_backup_file(),
                    self.datadir if datadir is None else datadir)

        status, output = subprocess.getstatusoutput(copy_back)

        if status == 0:
            logger.debug("Running -> {}".format(copy_back))
            logger.debug(output)
            logger.debug("Data copied back successfully!")
            return True
        else:
            logger.error("Error occurred while copying back data!")
            logger.error(output)
            raise RuntimeError("Error occurred while copying back data!")

    def giving_chown(self, datadir=None):
        # Changing owner of datadir to given user:group
        give_chown = "{} {}".format(self.chown_command, self.datadir if datadir is None else datadir)
        status, output = subprocess.getstatusoutput(give_chown)
        if status == 0:
            logger.debug("New copied-back data now owned by specified user!")
            return True
        else:
            logger.error("Error occurred while changing owner!")
            logger.error(output)
            raise RuntimeError("Error occurred while changing owner!")

    def start_mysql_func(self, start_tool=None, options=None):
        # Starting MySQL
        logger.debug("Starting MySQL server: ")
        if start_tool is None:
            args = self.start_mysql
        else:
            args = start_tool

        if options is not None:
            start_command = "{} {}".format(args, options)
        else:
            start_command = args
        status, output = subprocess.getstatusoutput(start_command)
        if status == 0:
            logger.debug("Starting MySQL ...")
            logger.debug(output)
            return True
        else:
            logger.error("Error occurred while starting MySQL!")
            logger.error(output)
            raise RuntimeError("Error occurred while starting MySQL!")

    @staticmethod
    def check_if_backup_prepared(full_dir, full_backup_file):
        '''
        This method is for checking if the backup can be copied-back.
        It is going to check xtrabackup_checkpoints file inside backup directory for backup_type column.
        backup_type column must be equal to 'full-prepared'
        :return: True if backup is already prepared; RuntimeError if it is not.
        '''
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
        logger.debug("Copying Back Already Prepared Final Backup:")
        if len(os.listdir(self.datadir if datadir is None else datadir)) > 0:
            logger.debug("MySQL Datadir is not empty!")
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
            self.check_if_backup_prepared(self.full_dir, self.recent_full_backup_file())
            self.shutdown_mysql()
            if self.move_datadir():
                if self.copy(options=options):
                    logger.debug("All data copied back successfully. ")
                    logger.debug("Your MySQL server is UP again")
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
                logger.debug("Backup tag will be used to prepare backups")
                self.prepare_with_tags()
        elif prepare == 2:
            if self.tag is None:
                self.prepare_inc_full_backups()
                if self.dry == 0:
                    self.copy_back_action()
                else:
                    logger.critical("Dry run is not implemented for copy-back/recovery actions!")
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
