MySQL-AutoXtrabackup
====================

MySQL AutoXtrabackup commandline tool written in Python 3.
The source code fully typed with hints - structured the project mostly similar to
[FastAPI](https://fastapi.tiangolo.com/) and [Pydantic](https://github.com/samuelcolvin/pydantic)

For community from Azerbaijan MySQL User Community: [Python Azerbaijan Community](https://www.facebook.com/groups/python.az).

For any question please open an issue here.

What this project is about?
---------------------------

The idea for this tool, came from my hard times after accidentally
deleting the table data.
There was a full backup and 12 incremental backups.
It took me 20 minutes to prepare necessary commands for preparing
backups. If you have compressed + encrypted backups you need also,
decrypt and decompress, which is going to add extra time for preparing
backups. Then I decided to automate this process. In other words,
preparing necessary commands for backup and prepare stage were
automated.

We have nice CLI with necessary options:

```
autoxtrabackup --help
Usage: autoxtrabackup [OPTIONS]

Options:
  --dry-run                       Enable the dry run.
  --prepare                       Prepare/recover backups.
  --run-server                    Start the FastAPI app for serving API
  --backup                        Take full and incremental backups.
  --version                       Version information.
  --defaults-file TEXT            Read options from the given file  [default: /
                                  home/shako/.autoxtrabackup/autoxtrabackup.cn
                                  f]

  --tag TEXT                      Pass the tag string for each backup
  --show-tags                     Show backup tags and exit
  -v, --verbose                   Be verbose (print to console)
  -lf, --log-file TEXT            Set log file  [default: /home/shako/.autoxtr
                                  abackup/autoxtrabackup.log]

  -l, --log, --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set log level  [default: INFO]
  --log-file-max-bytes INTEGER    Set log file max size in bytes  [default:
                                  1073741824]

  --log-file-backup-count INTEGER
                                  Set log file backup count  [default: 7]
  --help                          Print help message and exit.
```


If you think, CLI is not for you. We have experimental feature where you can start API server 
and take backups using API call(ATTENTION: FastAPI involved)

```
sudo `which autoxtrabackup` --run-server
INFO:     Started server process [30238]
INFO:     Waiting for application startup.
app started
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:5555 (Press CTRL+C to quit)
```

```
$ curl -X POST http://127.0.0.1:5555/backup
{"result":"Successfully finished the backup process"}
```

For the rest please read the full documentation.

Development:
-------------------

Current major version is >= 2.0 - so if you want to help, please do changes on this branch and then kindly send PR :)
I also encourage you to upgrade from older version as the code base fully updated.
Do you have an idea, question please open an issue.

Read full documentation here:
----------------------------------------------

[**MySQL-AutoXtrabackup documentation!**](https://autoxtrabackup.azepug.az/)
