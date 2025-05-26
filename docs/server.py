from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.db"
db = SQLAlchemy(app)

class WeatherEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    lux = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route("/data", methods=["POST"])
def receive_data():
    data = request.json
    entry = WeatherEntry(
        temperature=data.get("temperature"),
        humidity=data.get("humidity"),
        pressure=data.get("pressure"),
        lux=data.get("lux"),
        timestamp=datetime.now()
    )
    db.session.add(entry)
    db.session.commit()
    print("✅ Получены данные:", data)
    return jsonify({"status": "ok"})

@app.route("/data", methods=["GET"])
def get_data():
    entry = WeatherEntry.query.order_by(WeatherEntry.timestamp.desc()).first()
    if entry:
        return jsonify({
            "temperature": entry.temperature,
            "humidity": entry.humidity,
            "pressure": entry.pressure,
            "lux": entry.lux,
            "timestamp": entry.timestamp.isoformat()
        })
    return jsonify({"error": "no data"})

@app.route("/log", methods=["GET"])
def get_log():
    entries = WeatherEntry.query.order_by(WeatherEntry.timestamp.desc()).limit(100).all()
    return jsonify([
        {
            "temperature": e.temperature,
            "humidity": e.humidity,
            "pressure": e.pressure,
            "lux": e.lux,
            "timestamp": e.timestamp.isoformat()
        } for e in reversed(entries)
    ])

@app.route("/weekly")
def weekly_stats():
    from sqlalchemy import func

    start = request.args.get("start")
    end = request.args.get("end")

    query = db.session.query(
        func.date(WeatherEntry.timestamp),
        func.avg(WeatherEntry.temperature),
        func.avg(WeatherEntry.humidity),
        func.avg(WeatherEntry.pressure),
        func.avg(WeatherEntry.lux)
    )

    if start:
        query = query.filter(WeatherEntry.timestamp >= start)
    if end:
        query = query.filter(WeatherEntry.timestamp <= end)

    results = query.group_by(func.date(WeatherEntry.timestamp)).all()

    data = []
    for day, temp, hum, pres, lux in results:
        data.append({
            "date": day.isoformat(),
            "avg_temperature": round(temp, 2),
            "avg_humidity": round(hum, 2),
            "avg_pressure": round(pres, 2),
            "avg_lux": round(lux, 2)
        })

    return jsonify(data)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/archive")
def archive():
    return render_template("archive.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
