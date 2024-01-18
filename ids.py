import json
import os
import hashlib
import argparse
import logging
import datetime
import subprocess
import psutil
import socket

LOG_FILE = '/var/ids/ids.log'
DB_FILE = '/var/ids/db.json'

if not os.path.exists('/var/ids/'):
    os.makedirs('/var/ids/')

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

def build(minify=False):
    data = {}

    file_path = '/etc/shadow'
    file_info = get_file_info(file_path)
    data[file_path] = file_info

    build_time = str(datetime.datetime.now())
    listening_ports = get_listening_ports()

    json_data = {'build_time': build_time, 'files': data, 'listening_ports': listening_ports}

    with open(DB_FILE, 'w') as json_file:
        if minify:
            json.dump(json_data, json_file, separators=(',', ':'))
        else:
            json.dump(json_data, json_file, indent=2)

    logging.info('Commande build executee. Fichier JSON cree.')
    remove_spaces_and_newlines(DB_FILE)

def remove_spaces_and_newlines(file_path):
    with open(file_path, 'r') as json_file:
        content = json_file.read()

    content = content.replace(' ', '').replace('\n', '')

    with open(file_path, 'w') as json_file:
        json_file.write(content)

def get_file_info(file_path):
    file_info = {
        'sha512': hash_file(file_path, 'sha512'),
        'sha256': hash_file(file_path, 'sha256'),
        'md5': hash_file(file_path, 'md5'),
        'last_modified': get_last_modified(file_path),
        'creation_time': get_creation_time(file_path),
        'owner': get_owner(file_path),
        'group_owner': get_group_owner(file_path),
        'size': get_size(file_path)
    }
    return file_info

def hash_file(file_path, algorithm='sha256'):
    hasher = hashlib.new(algorithm)
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_last_modified(file_path):
    return str(datetime.datetime.fromtimestamp(os.path.getmtime(file_path)))

def get_creation_time(file_path):
    return str(datetime.datetime.fromtimestamp(os.path.getctime(file_path)))

def get_owner(file_path):
    return str(os.stat(file_path).st_uid)

def get_group_owner(file_path):
    return str(os.stat(file_path).st_gid)

def get_size(file_path):
    return str(os.path.getsize(file_path))

def get_listening_ports():
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

def check():
    if not os.path.exists(DB_FILE):
        logging.error(f'The file {DB_FILE} does not exist. Run the "build" command first.')
        return

    with open(DB_FILE, 'r') as json_file:
        expected_state = json.load(json_file)

    current_state = {file_path: get_file_info(file_path) for file_path in expected_state['files'].keys()}

    if current_state == expected_state['files']:
        logging.info('{"state": "ok"}')
    else:
        logging.warning('{"state": "divergent", "changes": %s}', json.dumps(find_changes(expected_state['files'], current_state)))

def find_changes(expected_state, current_state):
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
    parser.add_argument("--minify", action="store_true", help="Minifier le fichier JSON (sans indentation)")
    args = parser.parse_args()

    if args.command == "build":
        build(minify=args.minify)
    elif args.command == "check":
        check()