import json
import os
import hashlib
import argparse
import logging

LOG_FILE = '/var/log/ids/ids.log'
DB_FILE = '/var/ids/db.json'

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def build():
    data = {}
    files_to_monitor = load_config()

    for file_path in files_to_monitor:
        file_info = get_file_info(file_path)
        data[file_path] = file_info

    with open(DB_FILE, 'w') as json_file:
        json.dump(data, json_file, indent=2)

    logging.info('Commande build exécutée. Fichier JSON créé.')

def check():
    if not os.path.exists(DB_FILE):
        logging.error(f'Le fichier {DB_FILE} n\'existe pas. Exécutez d\'abord la commande "build".')
        return

    with open(DB_FILE, 'r') as json_file:
        expected_state = json.load(json_file)

    current_state = {file_path: get_file_info(file_path) for file_path in expected_state.keys()}

    if current_state == expected_state:
        logging.info('{"state": "ok"}')
    else:
        logging.warning('{"state": "divergent", "changes": %s}', json.dumps(find_changes(expected_state, current_state)))

def hash_file(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_file_info(file_path):
    file_stat = os.stat(file_path)
    file_owner = os.path.basename(file_path)
    file_group_owner = os.path.basename(file_path)
    file_size = file_stat.st_size
    file_creation_time = file_stat.st_ctime
    file_last_modification_time = file_stat.st_mtime

    file_info = {
        "file_path": file_path,
        "file_owner": file_owner,
        "file_group_owner": file_group_owner,
        "file_size": file_size,
        "file_creation_time": file_creation_time,
        "file_last_modification_time": file_last_modification_time,
        "hash_sha256": hash_file(file_path)
    }

    return file_info

def find_changes(expected_state, current_state):
    changes = {}
    for file_path in expected_state.keys():
        if expected_state[file_path] != current_state[file_path]:
            changes[file_path] = {
                'expected_info': expected_state[file_path],
                'current_info': current_state[file_path]
            }
    return changes

def load_config():
    with open('/etc/ids_config.json', 'r') as config_file:
        config = json.load(config_file)
    return config.get('files_to_monitor', [])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IDS - Intrusion Detection System")
    parser.add_argument("command", choices=["build", "check"], help="Commande à exécuter")
    args = parser.parse_args()

    if args.command == "build":
        build()
    elif args.command == "check":
        check()

