import json
import os
import hashlib
import argparse
import logging
import datetime
import subprocess
import psutil
import socket

class IntrusionDetectionSystem:
    def __init__(self, log_file='/var/ids/ids.log', db_file='/var/ids/db.json', config_file='/etc/ids/config.json'):
        self.log_file = log_file
        self.db_file = db_file
        self.config_file = config_file

        if not os.path.exists('/etc/ids/'):
            os.makedirs('/etc/ids/')

        logging.basicConfig(filename=self.log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(console_handler)

        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            logging.error(f'The file {self.config_file} does not exist.')
            raise

    def save_config(self):
        with open(self.config_file, 'w') as config_file:
            json.dump(self.config, config_file, indent=2)

    def build(self, minify=False):
        data = {}

        for file_path in self.config["files_to_monitor"]:
            file_info = self.get_file_info(file_path)
            data[file_path] = file_info

        build_time = str(datetime.datetime.now())
        listening_ports = self.get_listening_ports()

        json_data = {'build_time': build_time, 'files': data, 'listening_ports': listening_ports}

        with open(self.db_file, 'w') as json_file:
            if minify:
                json.dump(json_data, json_file, separators=(',', ':'))
            else:
                json.dump(json_data, json_file, indent=2)

        logging.info('Commande build executee. Fichier JSON créé.')
        self.remove_spaces_and_newlines(self.db_file)

    def remove_spaces_and_newlines(self, file_path):
        with open(file_path, 'r') as json_file:
            content = json_file.read()

        content = content.replace(' ', '').replace('\n', '')

        with open(file_path, 'w') as json_file:
            json_file.write(content)

    def get_file_info(self, file_path):
        file_info = {
            'sha512': self.hash_file(file_path, 'sha512'),
            'sha256': self.hash_file(file_path, 'sha256'),
            'md5': self.hash_file(file_path, 'md5'),
            'last_modified': self.get_last_modified(file_path),
            'creation_time': self.get_creation_time(file_path),
            'owner': self.get_owner(file_path),
            'group_owner': self.get_group_owner(file_path),
            'size': self.get_size(file_path)
        }
        return file_info

    def hash_file(self, file_path, algorithm='sha256'):
        hasher = hashlib.new(algorithm)
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def get_last_modified(self, file_path):
        return str(datetime.datetime.fromtimestamp(os.path.getmtime(file_path)))

    def get_creation_time(self, file_path):
        return str(datetime.datetime.fromtimestamp(os.path.getctime(file_path)))

    def get_owner(self, file_path):
        return str(os.stat(file_path).st_uid)

    def get_group_owner(self, file_path):
        return str(os.stat(file_path).st_gid)

    def get_size(self, file_path):
        return str(os.path.getsize(file_path))

    def get_listening_ports(self):
        listening_ports = {"TCP": [], "UDP": []}

        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == psutil.CONN_LISTEN:
                    if conn.type == socket.SOCK_STREAM:
                        listening_ports["TCP"].append(conn.laddr.port)
                    elif conn.type == socket.SOCK_DGRAM:
                        listening_ports["UDP"].append(conn.laddr.port)
        except Exception as e:
            logging.error(f'Error retrieving listening ports: {str(e)}')
            listening_ports = "Error retrieving listening ports"

        return listening_ports

    def check(self):
        if not os.path.exists(self.db_file):
            logging.error(f'The file {self.db_file} does not exist. Run the "build" command first.')
            return

        with open(self.db_file, 'r') as json_file:
            expected_state = json.load(json_file)

        current_state = {file_path: self.get_file_info(file_path) for file_path in expected_state['files'].keys()}

        if current_state == expected_state['files']:
            logging.info('{"state": "ok"}')
        else:
            logging.warning('{"state": "divergent", "changes": %s}', json.dumps(self.find_changes(expected_state['files'], current_state)))

    def find_changes(self, expected_state, current_state):
        changes = {}
        for file_path in expected_state.keys():
            if expected_state[file_path] != current_state[file_path]:
                changes[file_path] = {
                    'expected_info': expected_state[file_path],
                    'current_info': current_state[file_path]
                }
        return changes

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IDS - Intrusion Detection System")
    parser.add_argument("command", choices=["build", "check"], help="Commande a executer")
    args = parser.parse_args()

    ids = IntrusionDetectionSystem()

    if args.command == "build":
        ids.save_config()
    elif args.command == "check":
        ids.check()
