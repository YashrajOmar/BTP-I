import os
from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
import paho.mqtt.client as mqtt
import json

# Load the secrets from the .env file
load_dotenv()

# Read the variables securely
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT")) # Convert string to integer for Paho
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
TOPIC_COMMAND = "yashraj/device_test/commands"
TOPIC_TELEMETRY = "yashraj/device_test/telemetry"



# Setup MQTT Client
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.tls_set()


def on_message(client, userdata, msg):
    global latest_telemetry
    # Decode the JSON packet from the ESP32
    latest_telemetry = json.loads(msg.payload.decode())
    print(f"--- Incoming Telemetry: {latest_telemetry} ---")

client.on_message = on_message

# Standard practice: Manage external connections asynchronously
@asynccontextmanager
async def lifespan(app: FastAPI):
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(TOPIC_TELEMETRY)
    client.loop_start() # Runs the MQTT listener in a background thread
    print("--- MQTT Connected & Background Loop Started ---")
    yield # The web server runs while yielding
    client.loop_stop()
    client.disconnect()
    print("--- MQTT Disconnected safely ---")

app = FastAPI(lifespan=lifespan)

# REST Endpoint to trigger the hardware
@app.post("/led")
async def control_led(level: int, blink: int = 0):
    command = {"actuator": "led", "level": level, "blink": blink}
    
    print(f"Sending command to ESP32: {command}")
    
    # Dispatch the command over the cloud broker
    client.publish(TOPIC_COMMAND, json.dumps(command))
    
    return {"status": "Success", "dispatched_payload": command}

@app.get("/telemetry")
async def get_sensor_data():
    return {"status": "Success", "data": latest_telemetry}