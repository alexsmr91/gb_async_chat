import subprocess
import ipaddress
import socket
from threading import Thread


class ThreadWithReturnValue(Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        self.args = args
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def get_args(self):
        return self.args

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def pping(node: str):
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(node))
    except socket.error:
        return f"{node} - Неверный адрес"
    else:
        result = subprocess.run(["ping", "-n", "1", str(ip)], capture_output=True, text=True)
        if result.returncode == 0:
            return f"{node} - Узел доступен"
        else:
            return f"{node} - Узел недоступен"

def pping_bool(node: str):
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(node))
    except socket.error:
        return None
    else:
        result = subprocess.run(["ping", "-n", "1", str(ip)], capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            return False


def host_ping(nodes: str):
    for node in nodes:
        print(pping(node))


def host_range_ping(start_ip: str, end_ip: str):
    threads = []
    try:
        ip_start = ipaddress.ip_address(start_ip)
        ip_end = ipaddress.ip_address(end_ip)
    except ValueError:
        return "Check IPs"
    for ip in range(int(ip_start), int(ip_end) + 1):
        ip = str(ipaddress.IPv4Address(ip))
        thread = ThreadWithReturnValue(target=pping, args=(ip,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        print(thread.join())


def host_range_ping_tab(start_ip: str, end_ip: str):
    from tabulate import tabulate
    threads = []
    results = {"Reachable": [], "Unreachable": [], "Error": []}
    try:
        ip_start = ipaddress.ip_address(start_ip)
        ip_end = ipaddress.ip_address(end_ip)
    except ValueError:
        return "Check IPs"
    for ip in range(int(ip_start), int(ip_end) + 1):
        ip = str(ipaddress.IPv4Address(ip))
        thread = ThreadWithReturnValue(target=pping_bool, args=(ip,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        res = thread.join()
        ip = thread.get_args()[0]
        if res == True:
            results["Reachable"].append(ip)
        elif res == None:
            results["Error"].append(ip)
        else:
            results["Unreachable"].append(ip)
    return tabulate(results, headers='keys')


if __name__ == "__main__":

    host_list = ["256.0.0.1", "127.0.0.1", "192.168.1.100", "google.com", "invalid_ip"]
    host_ping(host_list)

    start_ip = "192.168.1.1"
    end_ip = "192.168.1.100"
    host_range_ping(start_ip, end_ip)

    print(host_range_ping_tab(start_ip, end_ip))
