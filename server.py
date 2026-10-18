

import paho.mqtt.client as mqtt
import ssl
import json

# Network Configuration
# BROKER = "test.mosquitto.org"
# BROKER = "broker.hivemq.com"


MQTT_BROKER = "se1a1a00.ala.eu-central-1.emqxsl.com"
MQTT_PORT = 8883
MQTT_USER = "Yashraj_Omar"
MQTT_PASSWORD = "Yashraj1"

PORT = 1883
TOPIC_TELEMETRY = "yashraj/device_test/telemetry"
TOPIC_COMMAND = "yashraj/device_test/commands"



# Callback: Triggers when hardware sends data
def on_message(client, userdata, msg):
    try:
        # The backend doesn't care what the hardware is, it just parses the JSON
        payload = json.loads(msg.payload.decode())
        print(f"\n[Telemetry Received]: {payload}")
    except json.JSONDecodeError:
        print("\n[Error]: Received malformed data")

# Setup MQTT Client
# client = mqtt.Client()
# client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
# client.tls_set()

# client.on_message = on_message
# client.connect(BROKER, PORT, 60)


# Setup MQTT Client
client = mqtt.Client()

client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.tls_set()

client.on_message = on_message

# Updated to use the correct EMQX variables and TLS port
client.connect(MQTT_BROKER, MQTT_PORT, 60)



print("Connected to broker. Listening for hardware telemetry...")
client.subscribe(TOPIC_TELEMETRY)
client.loop_start()

# Asynchronous Command Dispatcher
try:
    while True:
        # Send dynamic JSON commands (e.g., {"actuator": "relay", "state": 1})
        raw_input = input("Enter command JSON (or press Ctrl+C to quit): ")
        client.publish(TOPIC_COMMAND, raw_input)
        print(f"[Command Sent]: {raw_input}")
except KeyboardInterrupt:
    print("\nShutting down server...")
    client.loop_stop()