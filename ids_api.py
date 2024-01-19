from flask import Flask, jsonify, request
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = b'SECRET_KEY'

# Structure pour stocker les rapports
reports = []

# Fonction pour générer un rapport au format demandé
def generate_report(state, changes=None):
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "state": state,
        "changes": changes or {}
    }

# Charger la configuration des fichiers à surveiller
def load_configuration():
    try:
        with open("/var/ids/db.json", "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return {"files": []}

# Enregistrer la configuration des fichiers à surveiller
def save_configuration(config):
    with open("/var/ids/db.json", "w") as config_file:
        json.dump(config, config_file, indent=4)

# Endpoint pour effectuer un check
@app.route('/check', methods=['POST'])
def check():
    print("API: POST /check")

    # Charger la configuration des fichiers à surveiller
    config = load_configuration()

    # Effectuer la vérification ici
    # ...

    # Exemple de rapport
    state = "ok"  # ou "divergent" si quelque chose a changé
    report = generate_report(state, changes={"file1": "modified", "file2": "unchanged"})

    # Stocker le rapport
    reports.append(report)

    return jsonify(report)

# Endpoint pour récupérer tous les rapports
@app.route('/reports', methods=['GET'])
def get_reports():
    print("API: GET /reports")
    return jsonify(reports)

# Endpoint pour récupérer un seul rapport par ID
@app.route('/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    print(f"API: GET /reports/{report_id}")

    if 0 <= report_id < len(reports):
        return jsonify(reports[report_id])
    else:
        return jsonify({"error": "Report not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
