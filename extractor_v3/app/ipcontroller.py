import logging
import os, shutil
import subprocess

#Логер
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler('/srv/extractor_v3/logs/creatorcontroller.log', mode='a')

logging.basicConfig(format='%(asctime)s, %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.WARNING
    )
loger = logging.getLogger(__name__)
loger.setLevel(logging.WARNING)
loger.addHandler(stream_handler)
loger.addHandler(file_handler)


class IpController:
    def __init__(self, ip):
        self.ip = ip

    def unban(self):
        loger.error(f'Unban user {self.ip}..')

        a = subprocess.check_output(f'f2b-remote --unban --subnet --ip {self.ip}', shell=True)
        loger.error(f"first command: {a}")
        
        a = subprocess.check_output(f'f2b-remote --unban --ip {self.ip}', shell=True)
        loger.error(f"Second command: {a}")

    def ban(self):
        loger.error(f'Ban user {self.ip}..')

        a = subprocess.check_output(f'f2b-remote --subnet --ip {self.ip}', shell=True)
        loger.error(f"Command output: {a}")