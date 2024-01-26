"""Module containing the IDS API."""

from datetime import datetime
import json
from flask import Flask, jsonify

app = Flask(__name__)
app.secret_key = b"SECRET_KEY"

reports = []


def generate_report(state, changes=None):
    """Generate a report with timestamp, state, and changes."""
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "state": state,
        "changes": changes or {},
    }


def load_configuration():
    """Load configuration from the file."""
    try:
        with open("/var/ids/db.json", "r", encoding="utf-8") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return {"files": []}


def save_configuration(config):
    """Save configuration to the file."""
    with open("/var/ids/db.json", "w", encoding="utf-8") as config_file:
        json.dump(config, config_file, indent=4)


@app.route("/check", methods=["POST"])
def check():
    """Handle POST request to check the configuration."""
    print("API: POST /check")

    state = "ok" 
    report = generate_report(state, changes={"file1": "modified", "file2": "unchanged"})

    reports.append(report)

    return jsonify(report), 200


@app.route("/reports", methods=["GET"])
def get_reports():
    print("API: GET /reports")
    return jsonify(reports)


@app.route("/reports", methods=["GET"])
def get_reports():
    """Handle GET request to get all reports."""
    print("API: GET /reports")
    return jsonify(reports)


@app.route("/reports/<int:report_id>", methods=["GET"])
def get_report(report_id):
    """Handle GET request to get a specific report by ID."""
    print(f"API: GET /reports/{report_id}")

    if 0 <= report_id < len(reports):
        return jsonify(reports[report_id])
    return jsonify({"error": "Report not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
