import os
import socket
import urllib.request

import requests

class Tcp:
    @staticmethod
    def get_localhost_ip() -> str:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = '127.0.0.1'
        try:
            sock.connect(('8.8.8.8', 80))
            ip = sock.getsockname()[0]
        except:
            pass
        finally:
            sock.close()
        return ip

    @staticmethod
    def get_hostname() -> str:
        hostname = socket.gethostname()
        return hostname

my_hostname = Tcp.get_hostname()
# name='mytest'