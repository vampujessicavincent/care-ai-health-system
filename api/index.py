from flask import Flask, jsonify
import random
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Sensor API Running ✅"

@app.route('/api/sensor')
def sensor_data():
    data = {
        "hr": random.randint(70, 120),
        "bp": random.randint(110, 170),
        "spo2": random.randint(88, 99),
        "sugar": random.randint(80, 180),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    return jsonify(data)

def handler(request, context):
    return app(request.environ, lambda status, headers: None)