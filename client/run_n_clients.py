import subprocess
import sys


def run_clients(num_instances):
    server_ip = 'localhost'
    venv_python_path = '../../venvs/gb_async_chat/Scripts/python.exe'
    command = ['cmd', '/c', 'start', venv_python_path, 'client.py', server_ip, 'user_']

    for i in range(num_instances):
        command[len(command)-1] = f'user_{i+1}'
        subprocess.Popen(command)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        num_instances = int(sys.argv[1])
    else:
        num_instances = 2

    run_clients(num_instances)
