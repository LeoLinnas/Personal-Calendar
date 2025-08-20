from flask import Flask, jsonify
from my_calendar import Calendar

app = Flask(__name__)
c = Calendar()

@app.route("/api/calendar")
def get_calendar_json():

    with open("calendar.json", "r") as file:
        return jsonify(file.read())