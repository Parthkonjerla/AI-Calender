import re
import json
import dateparser
from flask import Flask, request, jsonify

# --------------------------
# Calendar Agent Functions
# --------------------------
events = []

def add_event(date, description):
    events.append({"date": date, "description": description})
    return f"Added event: '{description}' on {date}"

def show_events():
    if not events:
        return "No events found."
    return [{"date": e["date"], "description": e["description"]} for e in events]

def delete_event(description):
    global events
    before = len(events)
    events = [e for e in events if e["description"].lower() != description.lower()]
    after = len(events)
    return f"Deleted {before - after} event(s) with description '{description}'."

# --------------------------
# Flask Web App
# --------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "AI Calendar Agent is running successfully on Render!"

@app.route("/add", methods=["POST"])
def add():
    data = request.get_json()
    date_str = data.get("date")
    description = data.get("description")

    if not date_str or not description:
        return jsonify({"error": "Both 'date' and 'description' are required"}), 400

    date = dateparser.parse(date_str)
    if not date:
        return jsonify({"error": "Invalid date format"}), 400

    result = add_event(date.strftime("%Y-%m-%d"), description)
    return jsonify({"message": result})

@app.route("/show", methods=["GET"])
def show():
    return jsonify(show_events())

@app.route("/delete", methods=["DELETE"])
def delete():
    data = request.get_json()
    description = data.get("description")

    if not description:
        return jsonify({"error": "'description' is required"}), 400

    result = delete_event(description)
    return jsonify({"message": result})

# --------------------------
# Run the app
# --------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
