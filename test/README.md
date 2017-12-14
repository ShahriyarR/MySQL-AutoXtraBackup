# Special information on using autoxtrabackup --test_mode

## Preparing environment:

* Edit /etc/bck.conf and specify testpath under [TestConf] - in which path the test environment should be constructed, created.
* ps_branches - specify which branches of PS should be cloned and build.
* pxb_branches - specify which branches of PXB should be cloned and build.
* gitcmd - specify a link of PS repo.
* pxb_gitcmd - specify a link of PXB repo.

**Running with bats**:

The reason I choose to call PyTests from bats is, it gives an elegant way to constructs tests.

So what you need basically the BATS framework:

[installing-bats-from-source](https://github.com/sstephenson/bats#installing-bats-from-source)

**Running whole environment setup**

The thing you need is to run:

`bats prepare_env.bats`

That's it, it will do the all job.

**Running specific bats files**

I have prepared separate bats files to run specific things:

* `test_clone_percona_qa.bats` -> will clone percona-qa repo.
* `test_clone_ps_server_from_conf.bats` -> will clone PS servers based on specified branches.
* `test_clone_pxb.bats` -> will clone specified PXB based on specified branches.
* `test_build_pxb.bats` -> will build cloned PXBs and create separate binary archives for each branch.
* `test_build_server.bats` -> will build PS servers.
* `test_prepare_startup.bats` -> will run startup.sh from percona-qa inside PS basedirs.
* `test_prepare_start_dynamic.bats` -> will create start_dynamic scripts inside PS basedirs, which is going to be used in slave setup etc.
* `test_start_server.bats` -> will start PS servers with default values(executing start script inside basedirs).
* `test_extract_xb_archive.bats` -> will extracting PXB binary archives to the target folder inside testpath(which is grabbed from config file).
* `test_generate_config_files.bats` -> will generate specific config files based on PXB and PS versions.

