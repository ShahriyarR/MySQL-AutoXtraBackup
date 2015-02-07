#!/usr/local/bin/python3

import os

for i in sorted(os.listdir('/home/MySQL-AutoXtraBackup/backup_dir/inc')):
    if i == max(os.listdir('/home/MySQL-AutoXtraBackup/backup_dir/inc')):
        print("Fuck")
    else:
        print("Fuck2")
