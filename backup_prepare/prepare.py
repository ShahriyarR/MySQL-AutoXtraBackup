#!/usr/local/bin/python3

# Backup Prepare and Copy-Back Script
# Originally Developed by Shahriyar Rzayev / rzayev.sehriyar@gmail.com
import configparser
import os
import shlex
import subprocess
import shutil
import time
from general_conf.generalops import GeneralClass

class Prepare(GeneralClass):
    def __init__(self):
        GeneralClass.__init__(self)



    def recent_full_backup_file(self):
        # Return last full backup dir name

        if len(os.listdir(self.full_dir)) > 0:
            return max(os.listdir(self.full_dir))
        else:
            return 0


    def check_inc_backups(self):
        # Check for Incremental backups

        if len(os.listdir(self.inc_dir)) > 0:
            return 1
        else:
            return 0


    #############################################################################################################
    # PREPARE ONLY FULL BACKUP
    #############################################################################################################

    def prepare_only_full_backup(self):
        if self.recent_full_backup_file() == 0:
            print("##############################################################################################")
            print("You have no FULL backups. Please take backup for preparing")
            print("##############################################################################################")

        elif self.check_inc_backups() == 0:
            print("##############################################################################################")
            print("Preparing Full backup 1 time")
            print("##############################################################################################")
            time.sleep(3)
            args = '%s %s %s/%s' % (self.backup_tool, self.xtrabck_prepare, self.full_dir, self.recent_full_backup_file())
            status, output = subprocess.getstatusoutput(args)
            if status == 0:
                print(output[-27:])
                print("##############################################################################################")
                print("Preparing Again Full Backup for final usage.  \n"
                      "It means that you have not got inc backups")
                print("##############################################################################################")

                args2 = '%s --apply-log %s/%s' % (self.backup_tool, self.full_dir, self.recent_full_backup_file())
                status2, output2 = subprocess.getstatusoutput(args2)
                if status2 == 0:
                    print(output2[-27:])
                    return True
                else:
                    print("FULL BACKUP 2nd PREPARE FAILED!")
                    time.sleep(5)
                    print(output2)
                    return False
            else:
                print("FULL BACKUP 1st PREPARE FAILED!")
                time.sleep(5)
                print(output)
                return False


        else:
            print("###############################################################################################")
            print("Preparing Full backup 1 time. It means that,\n"
                  " you have got incremental backups and final preparing,\n"
                  " will occur after preparing all inc backups")
            print("################################################################################################")
            time.sleep(3)
            args = '%s %s %s/%s' % (self.backup_tool, self.xtrabck_prepare, self.full_dir, self.recent_full_backup_file())
            status, output = subprocess.getstatusoutput(args)
            if status == 0:
                print(output[-27:])
                return True
            else:
                print("One time FULL BACKUP PREPARE FAILED!")
                time.sleep(5)
                print(output)
                return False


    ##############################################################################################################
    # PREPARE INC BACKUPS
    ##############################################################################################################

    def prepare_inc_full_backups(self):
        if self.check_inc_backups() == 0:
            print("################################################################################################")
            print("You have no Incremental backups. So will prepare only latest Full backup")
            print("################################################################################################")
            time.sleep(3)
            self.prepare_only_full_backup()
        else:
            print("################################################################################################")
            print("You have Incremental backups. \n"
                  "Will prepare latest full backup then based on it, will prepare Incs")
            print("Preparing Full backup: ")
            print("################################################################################################")
            time.sleep(3)
            if self.prepare_only_full_backup():
                print("################################################################################################")
                print("Preparing Incs: ")
                print("################################################################################################")
                time.sleep(3)
                list_of_dir = sorted(os.listdir(self.inc_dir))

                for i in list_of_dir:
                    if i != max(os.listdir(self.inc_dir)):
                        print("########################################################################################")
                        print("Preparing inc backups in sequence. inc backup dir/name is %s" % i)
                        print("########################################################################################")
                        time.sleep(3)
                        args = '%s %s %s/%s --incremental-dir=%s/%s' % (self.backup_tool, self.xtrabck_prepare,
                                                                        self.full_dir, self.recent_full_backup_file(),
                                                                        self.inc_dir, i)


                        status, output = subprocess.getstatusoutput(args)
                        if status == 0:
                            print(output[-27:])
                        else:
                            print("Incremental BACKUP PREPARE FAILED!")
                            time.sleep(5)
                            print(output)
                            return False

                    else:
                        print("########################################################################################")
                        print("Preparing Last Incremental backup, Inc backup dir/name is %s" % i)
                        print("########################################################################################")
                        time.sleep(3)
                        args2 = '%s --apply-log %s/%s --incremental-dir=%s/%s' % (self.backup_tool,
                                                                                 self.full_dir,
                                                                                 self.recent_full_backup_file(),
                                                                                 self.inc_dir, i)
                        status2, output2 = subprocess.getstatusoutput(args2)
                        if status2 == 0:
                            print(output2[-27:])
                        else:
                            print("Incremental BACKUP PREPARE FAILED!")
                            time.sleep(5)
                            print(output2)
                            return False

            print("################################################################################################")
            print("The end of Preparing Stage.")
            print("The last step of backup preparing is, \n"
                  "preparing FULL backup again for final usage")
            print("Preparing FULL backup Again:")
            print("################################################################################################")
            time.sleep(3)

            args3 = '%s --apply-log %s/%s' % (self.backup_tool, self.full_dir, self.recent_full_backup_file())

            status3, output3 = subprocess.getstatusoutput(args3)
            if status3 == 0:
                print(output3[-27:])
                return True
            else:
                print("Full BACKUP PREPARE FAILED!")
                time.sleep(5)
                print(output3)
                return False

    #############################################################################################################
    # COPY-BACK PREPARED BACKUP
    #############################################################################################################

    def shutdown_mysql(self):

        # Shut Down MySQL
        print("###################################################################################################")
        print("Shutting Down MySQL server: ")
        print("###################################################################################################")
        time.sleep(3)
        args = self.stop_mysql
        status, output = subprocess.getstatusoutput(args)
        if status == 0:
            print(output)
            return True
        else:
            print("Could not Shutdown MySQL!")
            print("Refer to MySQL Error log file, default PATH: /var/lib/mysql/hostname.err")
            print(output)
            return False


    def move_datadir(self):

        # Move datadir to new directory
        print("###################################################################################################")
        print("Moving MySQL datadir to /tmp/mysql: ")
        print("###################################################################################################")
        time.sleep(3)
        if os.path.isdir(self.tmpdir):
            rmdirc = 'rm -rf %s' % self.tmpdir
            status, output = subprocess.getstatusoutput(rmdirc)

            if status == 0:
                print("Emptied /tmp/mysql directory")

                try:
                    shutil.move(self.datadir, self.tmp)
                    print("Moved datadir to /tmp/mysql")
                except shutil.Error as err:
                    print("Error occurred while moving datadir")
                    print(err)
                    return False

                print("Creating an empty data directory")
                makedir = self.mkdir_command
                status2, output2 = subprocess.getstatusoutput(makedir)
                if status2 == 0:
                    print("/var/lib/mysql Created!")
                else:
                    print("Error while creating datadir")
                    print(output2)
                    return False

                return True

            else:
                print("Could not delete /tmp/mysql directory")
                print(output)
                return False

        else:
            try:
                shutil.move(self.datadir, self.tmp)
                print("Moved datadir to /tmp/mysql")
            except shutil.Error as err:
                print("Error occurred while moving datadir")
                print(err)
                return False

            print("Creating an empty data directory")
            makedir = self.mkdir_command
            status2, output2 = subprocess.getstatusoutput(makedir)
            if status2 == 0:
                print("/var/lib/mysql Created!")
                return True
            else:
                print("Error while creating datadir")
                print(output2)
                return False

    def run_xtra_copyback(self):
        # Running Xtrabackup with --copy-back option

        copy_back = '%s --copy-back %s/%s' % (self.backup_tool,
                                                  self.full_dir,
                                                  self.recent_full_backup_file())

        status, output = subprocess.getstatusoutput(copy_back)

        if status == 0:
            print("################################################################################################")
            print("Data copied back successfully!")
            print("################################################################################################")
            return True
        else:
            print("Error occurred while copying back data!")
            print(output)
            return False


    def giving_chown(self):
        # Changing owner of datadir to mysql:mysql
        time.sleep(3)
        give_chown = self.chown_command
        status, output = subprocess.getstatusoutput(give_chown)

        if status == 0:
            print("################################################################################################")
            print("New copied-back data now owned by mysql:mysql ")
            print("################################################################################################")
            return True
        else:
            print("Error occurred while chaning owner!")
            print(output)
            return False


    def start_mysql_func(self):
        # Starting or Bootstrapping(if it is a main NODE) MySQL/Mariadb
        print("################################################################################################")
        print("Starting MySQL server choose one of 2 options!: ")
        print("1. Run bootstrap command - service mysql bootstrap - because this server is main node in MariaDB Galera Cluster")
        print("2. Run start command - service mysql start - for usual usage or for secondary nodes")
        start = int(input("Please choose 1 or 2: "))
        print("################################################################################################")
        time.sleep(3)

        if start == 1:
            bootstrap = self.mariadb_cluster_bootstrap
            status, output = subprocess.getstatusoutput(bootstrap)
            if status == 0:
                print("Bootstrapping Node")
                print(output)
                return True
            else:
                print("Error occurred while bootstrapping node!")
                print(output)
                return False

        elif start == 2:
            start_command = self.start_mysql
            status, output = subprocess.getstatusoutput(start_command)
            if status == 0:
                print("Starting MySQL")
                print(output)
                return True
            else:
                print("Error occurred while starting MySQL!")
                print(output)
                return False

        else:
            print("Please choose 1 or 2")
            return False



    def copy(self):

        print("###################################################################################################")
        print("Copying Back Already Prepared Final Backup: ")
        print("###################################################################################################")
        time.sleep(3)
        if len(os.listdir(self.datadir)) > 0:
            print("MySQL Datadir is not empty!")
            return False
        else:
            if self.run_xtra_copyback():
                if self.giving_chown():
                    if self.start_mysql_func():
                        return True
                    else:
                        "Error Occurred!"




    def copy_back(self):

        if self.shutdown_mysql():
            if self.move_datadir():
                if self.copy():
                    print("################################################################################################")
                    print("All data copied back successfully your MySQL server is UP again. \n"
                            "Congratulations. \n"
                            "Backups are life savers")
                    print("################################################################################################")
                    return True
                else:
                    print("Error Occurred!")




    ##############################################################################################################
    # FINAL FUNCTION FOR CALL: PREPARE/PREPARE AND COPY-BACK/COPY-BACK
    ##############################################################################################################


    def prepare_backup_and_copy_back(self):
    # Recovering/Copying Back Prepared Backup
        print("#####################################################################################################")
        print("This script is Preparing full/inc backups!")
        print("What do you want to do?")
        print("1. Prepare Backups and keep for future usage.NOTE('Once Prepared Backups Can not be prepared Again')")
        print("2. Prepare Backups and restore/recover/copy-back immediately")
        print("3. Just copy-back previously prepared backups")

        prepare = int(input("Please Choose one of options and type 1 or 2 or 3: "))
        print("####################################################################################################")
        if prepare == 1:
            self.prepare_inc_full_backups()
        elif prepare == 2:
            self.prepare_inc_full_backups()
            self.copy_back()
        elif prepare == 3:
            self.copy_back()
        else:
            print("Please type 1 or 2 or 3 and nothing more!")


# a = Prepare()
# a.prepare_backup_and_copy_back()