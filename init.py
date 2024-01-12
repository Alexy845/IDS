import os

LOG_FILE = '/var/ids/ids.log'
DB_FILE = '/var/ids/db.json'
IDS_PY_FILE = '/path/to/ids.py'

USERNAME = 'lebou'
GROUPNAME = 'lebou'

EXCLUDED_FILES = ['/etc/shadow']

def init():
    if not os.path.exists('/var/ids/'):
        os.makedirs('/var/ids/')

    os.system(f"touch {LOG_FILE}")
    os.system(f"chmod 664 {LOG_FILE}")
    os.system(f"chown {USERNAME}:{GROUPNAME} {LOG_FILE}")

    os.system(f"touch {DB_FILE}")
    os.system(f"chmod 664 {DB_FILE}")
    os.system(f"chown {USERNAME}:{GROUPNAME} {DB_FILE}")

    os.system(f"chmod 774 {IDS_PY_FILE}")
    os.system(f"chown {USERNAME}:{GROUPNAME} {IDS_PY_FILE}")

    for excluded_file in EXCLUDED_FILES:
        if os.path.exists(excluded_file):
            os.system(f"chmod 664 {excluded_file}")
            os.system(f"chown {USERNAME}:{GROUPNAME} {excluded_file}")

if __name__ == "__main__":
    init()
