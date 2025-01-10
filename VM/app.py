import paho.mqtt.client as mqtt
import sqlite3
from flask import Flask, render_template
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime
import threading

# Initialiser Flask
app = Flask(__name__)

# Navnet på databasen
DB_NAME = "pablo.db"

# Opret database-tabellen
def create_table():
    query = """CREATE TABLE IF NOT EXISTS pablo(
        datetime TEXT NOT NULL,
        count INTEGER NOT NULL
    )"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    conn.close()

create_table()

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Forbundet til broker!")
        client.subscribe("pilledata")  
    else:
        print(f"Forbindelsesfejl med kode {rc}")

def on_message(client, userdata, msg):
    try:
        pilledata = int(msg.payload.decode())
        print(f"Pilledata modtaget og konverteret: {pilledata}")
        insert_data(pilledata)
    except ValueError as e:
        print(f"Fejl ved konvertering af pilledata: {msg.payload.decode()} - {e}")

def insert_data(pilledata):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M") 
    cur.execute("INSERT INTO pablo (datetime, count) VALUES (?, ?)", (timestamp, pilledata))
    conn.commit()
    conn.close()
    print(f"Pilledata ({pilledata}) gemt i databasen.")


# Flask-rute
@app.route("/")
def home():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H")
    cur.execute("SELECT datetime, count FROM pablo")
    data = cur.fetchall()
    conn.close()

    if not data:
        return "Ingen data at vise."

    x = [row[0] for row in data]
    y = [row[1] for row in data]

    fig = plt.figure(figsize=(8, 4))
    plt.bar(x, y, color='skyblue')
    plt.title("Medicinforbrug over tid")
    plt.xlabel("Tid")
    plt.ylabel("Antal piller")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    img = BytesIO()
    fig.savefig(img, format="png")
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()

    return render_template("index.html", graph=graph_url)

def start_flask():
    app.run(host="0.0.0.0", port=5000)

def start_mqtt():
    broker_ip = "localhost"
    client = mqtt.Client()
    client.enable_logger()

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print(f"Forbinder til MQTT broker på {broker_ip}...")
        client.connect(broker_ip, 1883, 60)
        client.loop_forever()
    except Exception as e:
        print(f"Der opstod en fejl: {e}")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask)
    mqtt_thread = threading.Thread(target=start_mqtt)

    flask_thread.start()
    mqtt_thread.start()

    flask_thread.join()
    mqtt_thread.join()