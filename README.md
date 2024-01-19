# IDS
installer :
pip
psutil

mettre le user et le group dans init.py
lancer en sudo
puis build
et check
backup.service = reboot
```
[lebou@localhost ~]$ journalctl -u backup.service
Jan 18 10:57:30 localhost.localdomain systemd[1]: Started Backup Service for IDS.
Jan 18 10:57:30 localhost.localdomain systemd[1]: backup.service: Deactivated successfully.
```
backup.timer
```
[lebou@localhost ~]$ journalctl -u backup.timer
Jan 18 10:21:42 localhost systemd[1]: Started Timer for Backup Service.
Jan 18 11:41:45 localhost.localdomain systemd[1]: backup.timer: Deactivated successfully.
Jan 18 11:41:45 localhost.localdomain systemd[1]: Stopped Timer for Backup Service.
Jan 18 11:41:45 localhost.localdomain systemd[1]: Stopping Timer for Backup Service...
Jan 18 11:41:45 localhost.localdomain systemd[1]: Started Timer for Backup Service.
```

[lebou@localhost ~]$ cat /var/ids/db.json | tr -d ' \n' | sudo tee /var/ids/db.json > /dev/null
[lebou@localhost ~]$ cat /var/ids/db.json
{"build_time":"2024-01-1812:20:26.671421","files":{"/etc/shadow":{"sha512":"deb33a0dce347cdb3ee85e62b1320dce443ead6522d2bffef0c9b1477a53b5c829193c9a4894d0f65d747e882b56b520f43a30de97d83aaa3c91ec594824fec3","sha256":"4f7a8231fe95a520784da40d7f1140d63d604f1e4e24314e15c3388997b4271a","md5":"d0b1e7d198ef60177647f7e9e8a783e8","last_modified":"2023-11-0617:29:59.468779","creation_time":"2024-01-1210:32:13.905631","owner":"0","group_owner":"0","size":"886"}},"listening_ports":{"TCP":[22,22],"UDP":[]}}


pip install Flask
