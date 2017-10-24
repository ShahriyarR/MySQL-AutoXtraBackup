# Backup Prepare and Copy-Back Script
# Originally Developed by
# Shahriyar Rzayev -> http://www.mysql.az
# / rzayev.sehriyar@gmail.com / rzayev.shahriyar@yandex.com


import os
import subprocess
import shutil
import time
from general_conf.generalops import GeneralClass
from general_conf.check_env import CheckEnv
from os.path import isfile

import logging
logger = logging.getLogger(__name__)


class Prepare(GeneralClass):

    def __init__(self, config="/etc/bck.conf", dry_run=0):
        self.conf = config
        self.dry = dry_run
        GeneralClass.__init__(self, self.conf)
        #self.check_env_obj = CheckEnv(self.conf)
        # If prepare_tool option enabled in config, make backup_tool to use this.
        if hasattr(self, 'prepare_tool'):
            self.backup_tool = self.prepare_tool

    def recent_full_backup_file(self):
        # Return last full backup dir name

        if len(os.listdir(self.full_dir)) > 0:
            return max(os.listdir(self.full_dir))
        return 0

    def check_inc_backups(self):
        # Check for Incremental backups

        if len(os.listdir(self.inc_dir)) > 0:
            return 1
        return 0

    ##########################################################################
    # PREPARE ONLY FULL BACKUP
    ##########################################################################

    def prepare_only_full_backup(self):
        if self.recent_full_backup_file() == 0:
            logger.debug(
                "####################################################################################################")
            logger.debug(
                "You have no FULL backups. First please take FULL backup for preparing - - - - - - - - - - - - - -  #")
            logger.debug(
                "####################################################################################################")
            exit(0)

        elif self.check_inc_backups() == 0:
            logger.debug(
                "################################################################################################")
            logger.debug(
                "Preparing Full Backup - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #")
            logger.debug(
                "################################################################################################")

            # Extract and decrypt streamed full backup prior to executing incremental backup
            if hasattr(self, 'stream')  \
                    and hasattr(self, 'encrypt') \
                    and hasattr(self, 'xbs_decrypt'):
                logger.debug("Using xbstream to extract and decrypt from full_backup.stream!")
                xbstream_command = "%s %s --decrypt=%s --encrypt-key=%s --encrypt-threads=%s " \
                                   "< %s/%s/full_backup.stream -C %s/%s" % (
                                       self.xbstream,
                                       self.xbstream_options,
                                       self.decrypt,
                                       self.encrypt_key,
                                       self.encrypt_threads,
                                       self.full_dir,
                                       self.recent_full_backup_file(),
                                       self.full_dir,
                                       self.recent_full_backup_file()
                                   )

                logger.debug(
                    "The following xbstream command will be executed %s",
                    xbstream_command)
                if self.dry == 0 and isfile(("%s/%s/full_backup.stream") %
                                                          (self.full_dir, self.recent_full_backup_file())):
                    status, output = subprocess.getstatusoutput(xbstream_command)
                    if status == 0:
                        logger.debug("XBSTREAM command succeeded.")
                    else:
                        logger.error("XBSTREAM COMMAND FAILED!")
                        time.sleep(5)
                        logger.error(output)
                        return False

            # Extract streamed full backup prior to executing incremental backup
            elif hasattr(self, 'stream'):
                logger.debug("Using xbstream to extract from full_backup.stream!")
                xbstream_command = "%s %s < %s/%s/full_backup.stream -C %s/%s" % (
                    self.xbstream,
                    self.xbstream_options,
                    self.full_dir,
                    self.recent_full_backup_file(),
                    self.full_dir,
                    self.recent_full_backup_file()
                )

                logger.debug(
                    "The following xbstream command will be executed %s",
                    xbstream_command)

                if self.dry == 0 and isfile(("%s/%s/full_backup.stream") %
                                                            (self.full_dir, self.recent_full_backup_file())):
                    status, output = subprocess.getstatusoutput(xbstream_command)
                    if status == 0:
                        logger.debug("XBSTREAM command succeeded.")
                    else:
                        logger.error("XBSTREAM COMMAND FAILED!")
                        time.sleep(5)
                        logger.error(output)
                        return False


            # Check if decryption enabled
            if hasattr(self, 'decrypt'):
                if hasattr(self, 'remove_original_enc') and (self.remove_original_enc):
                    decr = "%s --decrypt=%s --encrypt-key=%s --target-dir=%s/%s --remove-original" % \
                           (self.backup_tool,
                            self.decrypt,
                            self.encrypt_key,
                            self.full_dir,
                            self.recent_full_backup_file())
                else:
                    decr = "%s --decrypt=%s --encrypt-key=%s --target-dir=%s/%s" % \
                            (self.backup_tool,
                             self.decrypt,
                             self.encrypt_key,
                             self.full_dir,
                             self.recent_full_backup_file())                    
                logger.debug("Trying to decrypt backup")
                logger.debug("Running decrypt command -> %s", decr)
                if self.dry == 0:
                    status, output = subprocess.getstatusoutput(decr)
                    if status == 0:
                        logger.debug(output[-27:])
                        logger.debug("Decrypted!")
                    else:
                        logger.error("FULL BACKUP DECRYPT FAILED!")
                        time.sleep(5)
                        logger.error(output)

            # Check if decompression enabled
            if hasattr(self, 'decompress'):
                if hasattr(self, 'remove_original_comp') and (self.remove_original_comp):
                    decmp = "%s --decompress=%s --target-dir=%s/%s --remove-original" % \
                            (self.backup_tool,
                             self.decompress,
                             self.full_dir,
                             self.recent_full_backup_file())
                else:
                    decmp = "%s --decompress=%s --target-dir=%s/%s --remove-original" % \
                            (self.backup_tool,
                             self.decompress,
                             self.full_dir,
                             self.recent_full_backup_file())    
                logger.debug("Trying to decompress backup")
                logger.debug("Running decompress command -> %s", decmp)
                if self.dry == 0:
                    status, output = subprocess.getstatusoutput(decmp)
                    if status == 0:
                        logger.debug(output[-27:])
                        logger.debug("Decompressed")
                    else:
                        logger.error("FULL BACKUP DECOMPRESSION FAILED!")
                        time.sleep(5)
                        logger.error(output)
                    
            # Actual prepare command goes here
            args = "%s --prepare --target-dir=%s/%s" % \
                   (self.backup_tool,
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

            logger.debug("Running prepare command -> %s", args)
            if self.dry == 0:
                status, output = subprocess.getstatusoutput(args)

                if status == 0:
                    logger.debug(output)
                    #logger.debug(output[-27:])
                else:
                    logger.error("FULL BACKUP PREPARE FAILED!")
                    time.sleep(5)
                    logger.error(output)
                    return False

        else:
            logger.debug(
                "Preparing Full backup 1 time. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#\n"
                "Final prepare,will occur after preparing all inc backups - - - - - - - - - - - - - - - - -  - - - -#")
            logger.debug(
                "####################################################################################################")
            time.sleep(3)

            # Check if decryption enabled
            if hasattr(self, 'decrypt'):
                if hasattr(self, 'remove_original_enc') and (self.remove_original_enc):
                    decr = "%s --decrypt=%s --encrypt-key=%s --target-dir=%s/%s --remove-original" % \
                           (self.backup_tool,
                            self.decrypt,
                            self.encrypt_key,
                            self.full_dir,
                            self.recent_full_backup_file())
                else:
                    decr = "%s --decrypt=%s --encrypt-key=%s --target-dir=%s/%s" % \
                            (self.backup_tool,
                             self.decrypt,
                             self.encrypt_key,
                             self.full_dir,
                             self.recent_full_backup_file())                    
                logger.debug("Trying to decrypt backup")
                logger.debug("Running decrypt command -> %s", decr)
                if self.dry == 0:
                    status, output = subprocess.getstatusoutput(decr)
                    if status == 0:
                        logger.debug(output[-27:])
                        logger.debug("Decrypted!")
                    else:
                        logger.error("FULL BACKUP DECRYPT FAILED!")
                        time.sleep(5)
                        logger.error(output)

            # Check if decompression enabled, if it is, decompress backup prior
            # prepare
            if hasattr(self, 'decompress'):
                if hasattr(self, 'remove_original_comp') and (self.remove_original_comp):
                    decmp = "%s --decompress=%s --target-dir=%s/%s --remove-original" % \
                            (self.backup_tool,
                             self.decompress,
                             self.full_dir,
                             self.recent_full_backup_file())
                else:
                    decmp = "%s --decompress=%s --target-dir=%s/%s" % \
                            (self.backup_tool,
                             self.decompress,
                             self.full_dir,
                             self.recent_full_backup_file())
                logger.debug("Trying to decompress backup")
                logger.debug("Running decompress command -> %s", decmp)
                if self.dry == 0:
                    status, output = subprocess.getstatusoutput(decmp)
                    if status == 0:
                        logger.debug(output[-27:])
                        logger.debug("Decompressed")
                    else:
                        logger.error("FULL BACKUP DECOMPRESSION FAILED!")
                        time.sleep(5)
                        logger.error(output)
            
                         
            # Actual prepare command goes here
            args = '%s --prepare %s --target-dir=%s/%s' % \
                (self.backup_tool,
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
            
            logger.debug("Running prepare command -> %s", args)
            if self.dry == 0:
                status, output = subprocess.getstatusoutput(args)
                if status == 0:
                    logger.debug(output)
                    #logger.debug(output[-27:])
                    return True
                else:
                    logger.error("One time FULL BACKUP PREPARE FAILED!")
                    time.sleep(5)
                    logger.error(output)
                    return False
            else:
                return True

    ##########################################################################
    # PREPARE INC BACKUPS
    ##########################################################################

    def prepare_inc_full_backups(self):
        if self.check_inc_backups() == 0:
            logger.debug(
                "################################################################################################")
            logger.debug(
                "You have no Incremental backups. So will prepare only latest Full backup - - - - - - - - - - - #")
            logger.debug(
                "################################################################################################")
            time.sleep(3)
            self.prepare_only_full_backup()
        else:
            logger.debug(
                "####################################################################################################")
            logger.debug(
                "You have Incremental backups. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#")
            time.sleep(3)
            if self.prepare_only_full_backup():
                logger.debug(
                    "####################################################################################################")
                logger.debug("Preparing Incs: ")
                time.sleep(3)
                list_of_dir = sorted(os.listdir(self.inc_dir))

                for i in list_of_dir:
                    if i != max(os.listdir(self.inc_dir)):
                        logger.debug(
                            "Preparing inc backups in sequence. inc backup dir/name is %s" %
                            i)
                        logger.debug(
                            "####################################################################################################")
                        time.sleep(3)

                        # Check if decryption enabled
                        if hasattr(self, 'decrypt'):
                            if hasattr(self, 'remove_original_enc') and (self.remove_original_enc):
                                decr = "%s --decrypt=%s --encrypt-key=%s --target-dir=%s/%s --remove-original" % \
                                       (self.backup_tool,
                                        self.decrypt,
                                        self.encrypt_key,
                                        self.inc_dir,
                                        i)
                            else:
                                decr = "%s --decrypt=%s --encrypt-key=%s --target-dir=%s/%s" % \
                                        (self.backup_tool,
                                         self.decrypt,
                                         self.encrypt_key,
                                         self.inc_dir,
                                         i)                                
                            logger.debug("Trying to decrypt backup")
                            logger.debug("Running decrypt command -> %s", decr)
                            if self.dry == 0:
                                status, output = subprocess.getstatusoutput(decr)
                                if status == 0:
                                    logger.debug(output[-27:])
                                    logger.debug("Decrypted!")
                                else:
                                    logger.error("FULL BACKUP DECRYPT FAILED!")
                                    time.sleep(5)
                                    logger.error(output)

                        # Check if decompression enabled, if it is, decompress
                        # backup prior prepare
                        if hasattr(self, 'decompress'):
                            if hasattr(self, 'remove_original_comp') and (self.remove_original_comp):
                                decmp = "%s --decompress=%s --target-dir=%s/%s --remove-original" % \
                                        (self.backup_tool,
                                         self.decompress,
                                         self.inc_dir,
                                         i)
                            else:
                                decmp = "%s --decompress=%s --target-dir=%s/%s" % \
                                        (self.backup_tool,
                                         self.decompress,
                                         self.inc_dir,
                                         i)                                
                            logger.debug("Trying to decompress backup")
                            logger.debug(
                                "Running decompress command -> %s", decmp)
                            if self.dry == 0:
                                status, output = subprocess.getstatusoutput(decmp)
                                if status == 0:
                                    logger.debug(output[-27:])
                                    logger.debug("Decompressed")
                                else:
                                    logger.error(
                                        "INCREMENTAL BACKUP DECOMPRESSION FAILED!")
                                    time.sleep(5)
                                    logger.error(output)
                        
                                                   
                        # Actual prepare command goes here
                        args = '%s --prepare %s --target-dir=%s/%s --incremental-dir=%s/%s' % \
                            (self.backup_tool,
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

                        logger.debug("Running prepare command -> %s", args)
                        if self.dry == 0:
                            status, output = subprocess.getstatusoutput(args)
                            if status == 0:
                                logger.debug(output)
                                #logger.debug(output[-27:])
                            else:
                                logger.error("Incremental BACKUP PREPARE FAILED!")
                                time.sleep(5)
                                logger.error(output)
                                return False

                    else:
                        logger.debug(
                            "####################################################################################################")
                        logger.debug(
                            "Preparing last incremental backup, inc backup dir/name is %s" %
                            i)
                        logger.debug(
                            "####################################################################################################")
                        time.sleep(3)

                        # Extracting streamed incremental backup prior to preparing

                        if hasattr(self, 'stream'):
                            logger.debug("Using xbstream to extract from inc_backup.stream!")
                            xbstream_command = "%s %s < %s/%s/inc_backup.stream -C %s/%s" % (
                                self.xbstream,
                                self.xbstream_options,
                                self.inc_dir,
                                i,
                                self.inc_dir,
                                i
                            )

                            logger.debug(
                                "The following xbstream command will be executed %s",
                                xbstream_command)
                            if self.dry == 0 and isfile(
                                        ("%s/%s/inc_backup.stream") % (self.inc_dir, i)):
                                status, output = subprocess.getstatusoutput(xbstream_command)
                                if status == 0:
                                    logger.debug("XBSTREAM command succeeded.")
                                else:
                                    logger.error("XBSTREAM COMMAND FAILED!")
                                    time.sleep(5)
                                    logger.error(output)
                                    return False


                        # Check if decryption enabled
                        if hasattr(self, 'decrypt'):
                            if hasattr(self, 'remove_original_enc') and (self.remove_original_enc):
                                decr = "%s --decrypt=%s --encrypt-key=%s --target-dir=%s/%s --remove-original" % \
                                       (self.backup_tool,
                                        self.decrypt,
                                        self.encrypt_key,
                                        self.inc_dir,
                                        i)
                            else:
                                decr = "%s --decrypt=%s --encrypt-key=%s --target-dir=%s/%s" % \
                                                                (self.backup_tool,
                                                                    self.decrypt,
                                                                    self.encrypt_key,
                                                                    self.inc_dir,
                                                                    i)                                
                            logger.debug("Trying to decrypt backup")
                            logger.debug("Running decrypt command -> %s", decr)
                            if self.dry == 0:
                                status, output = subprocess.getstatusoutput(decr)
                                if status == 0:
                                    logger.debug(output[-27:])
                                    logger.debug("Decrypted!")
                                else:
                                    logger.error("FULL BACKUP DECRYPT FAILED!")
                                    time.sleep(5)
                                    logger.error(output)

                        # Check if decompression enabled, if it is, decompress
                        # backup prior prepare
                        if hasattr(self, 'decompress'):
                            if hasattr(self, 'remove_original_comp') and (self.remove_original_comp):
                                decmp = "%s --decompress=%s --target-dir=%s/%s --remove-original" % \
                                        (self.backup_tool,
                                         self.decompress,
                                         self.inc_dir,
                                         i)
                            else:
                                decmp = "%s --decompress=%s --target-dir=%s/%s" % \
                                        (self.backup_tool,
                                         self.decompress,
                                         self.inc_dir,
                                         i)                                
                            logger.debug("Trying to decompress backup")
                            logger.debug(
                                "Running decompress command -> %s", decmp)

                            if self.dry == 0:
                                status, output = subprocess.getstatusoutput(decmp)
                                if status == 0:
                                    logger.debug(output[-27:])
                                    logger.debug("Decompressed")
                                else:
                                    logger.error(
                                        "INCREMENTAL BACKUP DECOMPRESSION FAILED!")
                                    time.sleep(5)
                                    logger.error(output)
                                                             
                        
                        args2 = '%s --prepare --target-dir=%s/%s --incremental-dir=%s/%s' % \
                            (self.backup_tool,
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

                        logger.debug("Running prepare command -> %s", args2)
                        if self.dry == 0:
                            status2, output2 = subprocess.getstatusoutput(args2)
                            if status2 == 0:
                                logger.debug(output2)
                                #logger.debug(output2[-27:])
                            else:
                                logger.error("Incremental BACKUP PREPARE FAILED!")
                                time.sleep(5)
                                logger.error(output2)
                                return False

            logger.debug(
                "####################################################################################################")
            logger.debug(
                "The end of the Prepare Stage. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#")
            logger.debug(
                "####################################################################################################")
            time.sleep(3)

    ##########################################################################
    # COPY-BACK PREPARED BACKUP
    ##########################################################################

    def shutdown_mysql(self):

        # Shut Down MySQL
        logger.debug(
            "####################################################################################################")
        logger.debug(
            "Shutting Down MySQL server: - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#")
        logger.debug(
            "####################################################################################################")
        time.sleep(3)

        args = self.stop_mysql

        status, output = subprocess.getstatusoutput(args)
        if status == 0:
            logger.debug(output)
            return True
        else:
            logger.error("Could not Shutdown MySQL!")
            logger.error("Refer to MySQL Error log file")
            logger.error(output)
            return False

    def move_datadir(self):

        # Move datadir to new directory
        logger.debug(
            "####################################################################################################")
        logger.debug(
            "Moving MySQL datadir to {}  - - - - - - - - - - - - - - - - - - - - - - - - - - - -#".format(self.tmpdir))
        logger.debug(
            "####################################################################################################")
        time.sleep(3)
        if os.path.isdir(self.tmpdir):
            rmdirc = 'rm -rf %s' % self.tmpdir
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
                makedir = "mkdir %s" % (self.datadir)
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
            makedir = "mkdir %s" % (self.datadir)
            status2, output2 = subprocess.getstatusoutput(makedir)
            if status2 == 0:
                logger.debug("Datadir is Created! ...")
                return True
            else:
                logger.error("Error while creating datadir")
                logger.error(output2)
                return False

    def run_xtra_copyback(self):
        # Running Xtrabackup with --copy-back option

        copy_back = '%s --copy-back --target-dir=%s/%s --datadir=%s' % \
            (self.backup_tool,
             self.full_dir,
             self.recent_full_backup_file(),
             self.datadir)

        status, output = subprocess.getstatusoutput(copy_back)

        if status == 0:
            logger.debug(
                "####################################################################################################")
            logger.debug(
                "Data copied back successfully! - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #")
            logger.debug(
                "####################################################################################################")
            return True
        else:
            logger.error("Error occurred while copying back data!")
            logger.error(output)
            return False

    def giving_chown(self):
        # Changing owner of datadir to given user:group
        time.sleep(3)
        give_chown = "%s %s" % (self.chown_command, self.datadir)
        status, output = subprocess.getstatusoutput(give_chown)

        if status == 0:
            logger.debug(
                "####################################################################################################")
            logger.debug(
                "New copied-back data now owned by specified user! - - - - - - - - - - - - - - - - - - - - - - - - - - -#")
            logger.debug(
                "####################################################################################################")
            return True
        else:
            logger.error("Error occurred while changing owner!")
            logger.error(output)
            return False

    def start_mysql_func(self, options=None):
        # Starting MySQL
        logger.debug(
            "####################################################################################################")
        logger.debug("Starting MySQL/MariaDB server: ")
        logger.debug(
            "####################################################################################################")
        time.sleep(3)

        if options is not None:
            args = self.start_mysql
            start_command = "{} {}".format(args, options)
        else:
            args = self.start_mysql
            start_command = args
        status, output = subprocess.getstatusoutput(start_command)
        if status == 0:
            logger.debug("Starting MySQL ...")
            logger.debug(output)
            return True
        else:
            logger.error("Error occurred while starting MySQL!")
            logger.error(output)
            return False

    def copy(self, options=None):
        """
        Function for running:
          xtrabackup --copy-back
          giving chown to datadir
          starting mysql
        :return: True if succeeded. Error if failed
        """
        logger.debug(
            "####################################################################################################")
        logger.debug(
            "Copying Back Already Prepared Final Backup: - - - - - - - - - - - - - - - - - - - - - - - - - - - -#")
        logger.debug(
            "####################################################################################################")
        time.sleep(3)
        if len(os.listdir(self.datadir)) > 0:
            logger.debug("MySQL Datadir is not empty!")
            return False
        else:
            if self.run_xtra_copyback():
                if self.giving_chown():
                    if self.start_mysql_func(options=options):
                        return True
                    else:
                        "Error Occurred!"

    def copy_back_action(self, options=None):
        """
        Function for complete recover/copy-back actions
        :return: True if succeeded. Error if failed.
        """
        if self.shutdown_mysql():
            if self.move_datadir():
                if self.copy(options=options):
                    logger.debug(
                        "####################################################################################################")
                    logger.debug("All data copied back successfully. ")
                    logger.debug("Your MySQL server is UP again")
                    logger.debug(
                        "####################################################################################################")
                    return True
                else:
                    logger.error("Error Occurred!")

    ##########################################################################
    # FINAL FUNCTION FOR CALL: prepare_backup_and_copy_back()
    ##########################################################################

    def prepare_backup_and_copy_back(self):
        # Recovering/Copying Back Prepared Backup
        # print("#####################################################################################################")
        print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-")
        print("")
        print("Preparing full/inc backups!")
        print("What do you want to do?")
        print("1. Prepare Backups and keep for future usage. NOTE('Once Prepared Backups Can not be prepared Again')")
        print("2. Prepare Backups and restore/recover/copy-back immediately")
        print("3. Just copy-back previously prepared backups")

        prepare = int(
            input("Please Choose one of options and type 1 or 2 or 3: "))
        print("")
        print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-")
        time.sleep(3)
        # print("####################################################################################################")
        if prepare == 1:
            self.prepare_inc_full_backups()
        elif prepare == 2:
            self.prepare_inc_full_backups()
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
