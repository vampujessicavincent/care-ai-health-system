from flask import Flask, jsonify
import random
import time
from waitress import serve   # ✅ production server for Windows

app = Flask(__name__)

@app.route('/sensor', methods=['GET'])
def sensor_data():
    data = {
        "hr": random.randint(70, 120),
        "bp": random.randint(110, 170),
        "spo2": random.randint(88, 99),
        "sugar": random.randint(80, 180),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    return jsonify(data)

@app.route('/')
def home():
    return "Sensor API Running ✅"

if __name__ == "__main__":
    print("🚀 Sensor API running on http://127.0.0.1:5000")
    serve(app, host="0.0.0.0", port=5000)