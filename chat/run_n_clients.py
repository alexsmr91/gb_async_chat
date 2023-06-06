import subprocess


if __name__ == "__main__":
    server_ip = 'localhost'
    venv_python_path = '../../venvs/gb_async_chat/Scripts/python.exe'
    command = [venv_python_path, 'main.py', '']
    db_paths = ['user666.sqlite.db', 'chat.sqlite.db']  # , 'user2.sqlite.db', 'user1.sqlite.db', 'ddd.sqlite.db'

    for path in db_paths:
        command[len(command) - 1] = path
        subprocess.Popen(command)
