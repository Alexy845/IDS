"""Intrusion Detection System."""

import json
import os
import hashlib
import argparse
import logging
import datetime
import socket
import psutil


class IntrusionDetectionSystem:
    """Class representing an Intrusion Detection System."""

    def __init__(
        self,
        log_file="/var/ids/ids.log",
        db_file="/var/ids/db.json",
        config_file="/etc/ids/config.json",
    ):
        """Initialize the IntrusionDetectionSystem."""
        self.log_file = log_file
        self.db_file = db_file
        self.config_file = config_file

        if not os.path.exists("/etc/ids/"):
            os.makedirs("/etc/ids/")

        self.setup_logging()

        self.config = self.load_config()

    def setup_logging(self):
        """Set up logging for the system."""
        log_dir = os.path.dirname(self.log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(console_handler)

        self.config = self.load_config()

    def load_config(self):
        """Load configuration from the config file."""
        try:
            with open(self.config_file, "r", encoding="utf-8") as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            logging.error("The file %s does not exist.", self.config_file)
            raise

    def save_config(self):
        """Save the configuration to the config file."""
        with open(self.config_file, "w", encoding="utf-8") as config_file:
            json.dump(self.config, config_file, indent=2)

    def build(self, minify=False):
        """Build the system configuration."""
        data = {}

        files_to_monitor = self.config.get("files_to_monitor", [])

        for file_path in files_to_monitor:
            file_info = self.get_file_info(file_path)
            data[file_path] = file_info

        build_time = str(datetime.datetime.now())
        listening_ports = self.get_listening_ports()

        json_data = {
            "build_time": build_time,
            "files": data,
            "listening_ports": listening_ports,
        }

        try:
            with open(self.db_file, "w", encoding="utf-8") as json_file:
                if minify:
                    json.dump(json_data, json_file, separators=(",", ":"))
                else:
                    json.dump(json_data, json_file, indent=2)

            logging.info("Commande build executee. Fichier JSON créé.")
            self.remove_spaces_and_newlines(self.db_file)
        except FileNotFoundError as e:
            logging.error("Error saving data to %s: %s", self.db_file, str(e))

    @staticmethod
    def remove_spaces_and_newlines(file_path):
        """Remove spaces and newlines from the given file."""
        with open(file_path, "r", encoding="utf-8") as json_file:
            content = json_file.read()

        content = content.replace(" ", "").replace("\n", "")

        with open(file_path, "w", encoding="utf-8") as json_file:
            json_file.write(content)

    @staticmethod
    def get_file_info(file_path):
        """Get information about a file."""
        file_info = {
            'sha512': IntrusionDetectionSystem.hash_file(file_path, 'sha512'),
            'sha256': IntrusionDetectionSystem.hash_file(file_path, 'sha256'),
            'md5': IntrusionDetectionSystem.hash_file(file_path, 'md5'),
            'last_modified': IntrusionDetectionSystem.get_last_modified(file_path),
            'creation_time': IntrusionDetectionSystem.get_creation_time(file_path),
            'owner': IntrusionDetectionSystem.get_owner(file_path),
            'group_owner': IntrusionDetectionSystem.get_group_owner(file_path),
            'size': IntrusionDetectionSystem.get_size(file_path)
        }
        return file_info

    @staticmethod
    def hash_file(file_path, algorithm="sha256"):
        """Hash a file using the specified algorithm."""
        hasher = hashlib.new(algorithm)
        with open(file_path, "rb") as file:
            while chunk := file.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def get_last_modified(file_path):
        """Get the last modified time of a file."""
        return str(datetime.datetime.fromtimestamp(os.path.getmtime(file_path)))

    @staticmethod
    def get_creation_time(file_path):
        """Get the creation time of a file."""
        return str(datetime.datetime.fromtimestamp(os.path.getctime(file_path)))

    @staticmethod
    def get_owner(file_path):
       """Get the owner of a file."""
       return str(os.stat(file_path).st_uid)

    @staticmethod
    def get_group_owner(file_path):
        """Get the group owner of a file."""
        return str(os.stat(file_path).st_gid)

    @staticmethod
    def get_size(file_path):
        """Get the size of a file."""
        return str(os.path.getsize(file_path))

    @staticmethod
    def get_listening_ports():
        """Get the listening ports."""
        listening_ports = {"TCP": [], "UDP": []}

        try:
            for conn in psutil.net_connections(kind="inet"):
                if conn.status == psutil.CONN_LISTEN:
                    if conn.type == socket.SOCK_STREAM:
                        listening_ports["TCP"].append(conn.laddr.port)
                    elif conn.type == socket.SOCK_DGRAM:
                        listening_ports["UDP"].append(conn.laddr.port)
        except FileNotFoundError as e:
            logging.error("Error retrieving listening ports: %s", str(e))
            listening_ports = "Error retrieving listening ports"

        return listening_ports

    def check(self):
        """Check the system's configuration."""
        if not os.path.exists(self.db_file):
            logging.error(
                'The file %s does not exist. Run the "build" command first.',
                self.db_file,
            )
            return

        with open(self.db_file, "r", encoding="utf-8") as json_file:
            expected_state = json.load(json_file)

        current_state = {
            file_path: self.get_file_info(file_path)
            for file_path in expected_state["files"].keys()
        }

        if current_state == expected_state["files"]:
            logging.info('{"state": "ok"}')
        else:
            logging.warning(
                '{"state": "divergent", "changes": %s}',
                json.dumps(self.find_changes(expected_state["files"], current_state)),          
            )

    @staticmethod
    def find_changes(expected_state, current_state):
        """Find changes between expected and current states."""
        changes = {}
        for file_path in expected_state.keys():
            if expected_state[file_path] != current_state[file_path]:
                changes[file_path] = {
                    "expected_info": expected_state[file_path],
                    "current_info": current_state[file_path],
                }
        return changes

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IDS - Intrusion Detection System")
    parser.add_argument(
        "command", choices=["build", "check"], help="Commande a executer"
    )
    args = parser.parse_args()

    ids = IntrusionDetectionSystem()

    if args.command == "build":
        ids.setup_logging()
        ids.save_config()
        ids.build()    
    elif args.command == "check":
        ids.check()
