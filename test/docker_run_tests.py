from docker_env_for_test import run_commands, get_current_git_branch, get_container_instance_object

name = get_current_git_branch()
cnt = get_container_instance_object(name)

CMD = [
    ('bats --tap test_backup.bats', '/home/MySQL-AutoXtraBackup/test')
]


def run_tests(cnt):
    for cmd in CMD:
        if len(cmd) == 1:
            print(run_commands(cnt, cmd[0]))
        else:
            print(run_commands(cnt, cmd[0], cmd[1]))


if __name__ == "__main__":
    cnt = get_container_instance_object(name)
    run_tests(cnt=cnt)
