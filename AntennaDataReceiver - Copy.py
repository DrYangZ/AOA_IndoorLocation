import paho.mqtt.client as mqtt
import os
import datetime
import json

test_var = 1234

def get_filename():
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    file_name = f"C:/Users/adminptca13/Desktop/WebSocket_Server/data_record_{date_str}.txt"
    return file_name

def on_connect(client, userdata, flags, rc):
    print(f"connected with result code {rc}")
    topic = "silabs/aoa/angle/ble-pd-0C4314F469A4/ble-pd-84FD27EEE588"
    client.subscribe(topic)


def on_message(client, userdata, msg):
    message = msg.payload.decode()
    topic = msg.topic
    print(f"Receive message '{message}' on topic '{topic}'")

    data = {
        "topic" : topic,
        "message" : message,
        "timestamp" : datetime.datetime.now().isoformat()
    }

    filename = get_filename()
    with open(filename, 'a') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.write(f",\n")


def main():
    client = mqtt.Client(transport='websockets')

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", 8766)

    client.loop_forever()


if __name__ == '__main__':
    main()