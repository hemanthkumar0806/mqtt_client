import time
import paho.mqtt.client as mqtt
import ssl
import json
import _thread
import pandas as pd

# AWS IoT configuration
HOST = "a209vpgon02vvn-ats.iot.ap-south-1.amazonaws.com"
ROOT_CA = "/home/srkr/client/RootCA.pem"
PRIVATE_KEY = "/home/srkr/client/private.pem.key"
CERTIFICATE = "/home/srkr/client/certificate.pem.crt"

TOPIC = "solar_power_data/topic"
CLIENT_ID = "MySolarThing"
PORT = 8883

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker."""
    print("Connected to AWS IoT: " + str(rc))
    if rc == 0:
        print("Connection successful!")
    else:
        print("Connection failed with code " + str(rc))

def publish_excel_data(thread_name):
    """Publishes real-time data from a CSV file to AWS IoT Core."""
    print(f"Starting thread: {thread_name}")

    csv_file = "/home/srkr/client/real_time_data.CSV"

    try:
        df = pd.read_csv(csv_file, skiprows=2, encoding='ISO-8859-1', delimiter=';')
        df.columns = df.columns.str.strip()
        print("CSV file loaded successfully.")
        
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return

    for index, row in df.iterrows():
        try:
            payload = row.to_dict()
            payload["mqtt_timestamp"] = int(time.time())
            
            message_json = json.dumps(payload, default=str)
            
            print(f"Publishing data from row {index}: {message_json}")
            client.publish(TOPIC, payload=message_json, qos=1, retain=False)
            
            # Pause for 10 seconds before sending the next data point
            time.sleep(10)
        except Exception as e:
            print(f"An error occurred during publishing: {e}")
            continue

# Main script execution
client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
client.on_connect = on_connect

client.tls_set(
    ca_certs=ROOT_CA,
    certfile=CERTIFICATE,
    keyfile=PRIVATE_KEY,
    tls_version=ssl.PROTOCOL_TLSv1_2
)
client.tls_insecure_set(True)

print("Attempting to connect to AWS IoT...")
client.connect(HOST, PORT, 60)

try:
    _thread.start_new_thread(publish_excel_data, ("DataPublisher",))
except Exception as e:
    print(f"Error starting thread: {e}")

client.loop_forever()
