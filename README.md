# IDS

## Installation

Pour installer l'IDS, suivez ces étapes:
pip, psutil, flask

1. Installez les packages et dépendances requis:
```bash
dnf install pip
```
```bash
pip install psutil
```
```bash
pip install flask
```
1. Clonez le dépôt IDS:
```bash
git clone https://github.com/lyleb27/IDS.git
```

## Usage

Pour utiliser L'IDS, suivez ces étapes:

1. Exécutez l'application IDS avec l'option `--help` pour voir les options disponibles:
```bash
python ids.py --help
```

2. Pour build l'application IDS:
```bash
python ids.py build
```

3. Pour exécuter l'application IDS:
```bash
python ids.py check
```
4. Pour la backup de l'application IDS:
```bash
journalctl -u backup.service
```
```bash
journalctl -u backup.timer
```

## Configuration

Le fichier de configuration IDS (`config.json`) vous permet de personnaliser le comportement de l'application. Voici le schéma du fichier de configuration:
```json
{
  "files_to_monitor": [
    "/etc/shadow"
  ],
  "monitor_ports": true
}
```

