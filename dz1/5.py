import subprocess
sites = ['youtube.com', 'yandex.ru']
for site in sites:
    args = ['ping', site]
    subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in subproc_ping.stdout:
        print(line.decode('cp866'))
