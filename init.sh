IDS_DIR="/var/ids"
CONFIG_FILE="/etc/ids/config.json"
DB_FILE="/var/ids/db.json"
LOG_FILE="/var/ids/ids.log"
GROUP_NAME="idsusers"

if ! getent group "$GROUP_NAME" >/dev/null; then
    sudo groupadd "$GROUP_NAME"
fi

if ! groups | grep -q "\b$GROUP_NAME\b"; then
    sudo usermod -aG "$GROUP_NAME" "$(whoami)"
fi

sudo chown -R :"$GROUP_NAME" "$IDS_DIR" "$CONFIG_FILE" "$DB_FILE" "$LOG_FILE"
sudo chmod -R 770 "$IDS_DIR" "$CONFIG_FILE" "$DB_FILE" "$LOG_FILE"
sudo touch "$LOG_FILE"

echo "Access configured for user $(whoami) and group $GROUP_NAME."


#!/bin/bash

IDS_DIR="/var/ids"
CONFIG_FILE="/etc/ids/config.json"
DB_FILE="/var/ids/db.json"
LOG_FILE="/var/ids/ids.log"
GROUP_NAME="idsusers"

if ! getent group "$GROUP_NAME" >/dev/null; then
    sudo groupadd "$GROUP_NAME"
fi

if ! groups | grep -q "\b$GROUP_NAME\b"; then
    sudo usermod -aG "$GROUP_NAME" "$(whoami)"
fi

sudo usermod -aG "$GROUP_NAME" "$(whoami)"

sudo chown lebou:idsusers "$IDS_DIR"
sudo chmod 770 "$IDS_DIR"

sudo chown :idsusers "$LOG_FILE"
sudo chmod 770 "$LOG_FILE"

sudo chown :idsusers "$CONFIG_FILE"
sudo chmod 770 "$CONFIG_FILE"

sudo chown :idsusers "$DB_FILE"
sudo chmod 770 "$DB_FILE"

echo "Access configured for user $(whoami) and group $GROUP_NAME."
