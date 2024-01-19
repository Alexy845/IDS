import os

LOG_FILE = '/var/ids/ids.log'
DB_FILE = '/var/ids/db.json'
IDS_PY_FILE = '/etc/ids/ids.py'
CONFIG_FILE = '/etc/ids/config.json'

USERNAME = 'lebou'
GROUPNAME = 'lebou'

def init():
    if not os.path.exists('/etc/ids/'):
        os.makedirs('/etc/ids/')

    os.system(f"touch {CONFIG_FILE}")
    os.system(f"chmod 664 {CONFIG_FILE}")
    os.system(f"chown {USERNAME}:{GROUPNAME} {CONFIG_FILE}")

    os.system(f"touch {LOG_FILE}")
    os.system(f"chmod 664 {LOG_FILE}")
    os.system(f"chown {USERNAME}:{GROUPNAME} {LOG_FILE}")

    os.system(f"touch {DB_FILE}")
    os.system(f"chmod 664 {DB_FILE}")
    os.system(f"chown {USERNAME}:{GROUPNAME} {DB_FILE}")

    os.system(f"chmod 774 {IDS_PY_FILE}")
    os.system(f"chown {USERNAME}:{GROUPNAME} {IDS_PY_FILE}")

if __name__ == "__main__":
    init()
