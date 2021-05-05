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

If you think, CLI is not for you. We have experimental feature where you can start API server 
and take backups using API call.

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

Read full documentation here:
----------------------------------------------

[**MySQL-AutoXtrabackup documentation!**](https://autoxtrabackup.azepug.az/)
