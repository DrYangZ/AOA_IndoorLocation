import json
import paho.mqtt.client as mqtt
from sympy import *
import matplotlib.pyplot as plt
import datetime
import matplotlib.image as mpimg
from matplotlib.animation import FuncAnimation
from math import *
import time

# MQTT setup
MQTT_BROKER = "localhost"  # or the IP address of your Mosquitto server
MQTT_PORT = 9001  # default WebSocket port for Mosquitto
MQTT_TOPIC1 = "silabs/aoa/angle/ble-pd-0C4314F469A4/ble-pd-84FD27EEE588"
MQTT_TOPIC2 = "silabs/aoa/angle/ble-pd-0C4314F45C80/ble-pd-84FD27EEE588"
MQTT_TOPIC3 = "silabs/aoa/angle/ble-pd-0C4314F45C82/ble-pd-84FD27EEE588"
MQTT_TOPIC4 = "silabs/aoa/angle/ble-pd-0C4314F46A08/ble-pd-84FD27EEE588"

# Initialize SymPy symbols
x, y = symbols('x y')

# Global variables to hold the latest angles
angle1 = None
angle2 = None
angle3 = None
angle4 = None
cluster_dict = {}
distance_dict = {
    'Antenna_1': None,
    'Antenna_2': None,
    'Antenna_3': None,
    'Antenna_4': None
}
flag = False
closest_antenna = None
plot_points = {
    x: 200,
    y: 100
}
antenna_location = {
    'Antenna_1': [50, 30],
    'Antenna_2': [680, 30],
    'Antenna_3': [620, 980],
    'Antenna_4': [220, 980]
}

def get_filename():
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    file_name = f"C:/Users/adminptca13/Desktop/WebSocket_Server/data/location_record_{date_str}.txt"
    return file_name

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC1)
    client.subscribe(MQTT_TOPIC2)
    client.subscribe(MQTT_TOPIC3)
    client.subscribe(MQTT_TOPIC4)

# Callback when a message is received
def on_message(client, userdata, msg):
    global angle1, angle2, angle3, angle4, distance_dict, closest_antenna
    try:
        data = json.loads(msg.payload.decode())
        if msg.topic == MQTT_TOPIC1:
            angle1 = -data['azimuth']
            distance_dict['Antenna_1'] = data['distance']
        elif msg.topic == MQTT_TOPIC2:
            angle2 = -data['azimuth']
            distance_dict['Antenna_2'] = data['distance']
        elif msg.topic == MQTT_TOPIC3:
            angle3 = -data['azimuth']
            distance_dict['Antenna_3'] = data['distance']
        elif msg.topic == MQTT_TOPIC4:
            angle4 = -data['azimuth']
            distance_dict['Antenna_4'] = data['distance']

        flag = all(distance_dict.values())
        if flag:
            sorted_items = sorted(distance_dict.items(), key=lambda item: item[1])
            closest_antenna = sorted_items[0][0]
    except Exception as e:
        print(f"Error processing message: {e}")

def calculate_intersection(line1, line2):
    # 解方程组
    solution = solve((line1, line2), (x, y))
    return [solution[x], solution[y]]

# Process data and update plot
def process_data():
    global angle1, angle2, angle3, angle4, distance_dict, closest_antenna, plot_points
    if closest_antenna is not None:
        # Define the line equations for topic1 and topic2 并计算交点
        if 'Antenna_1' == closest_antenna or 'Antenna_2' == closest_antenna:
            line1 = Eq(y, tan(radians(angle1)) * (x-50) + 30)
            line2 = Eq(y, tan(radians(angle2)) * (x-680) + 30)
            cal_x, cal_y = calculate_intersection(line1, line2)
            if 733 > cal_x > 0 or 1036 > cal_y > 0:
                plot_points[x], plot_points[y] = cal_x, cal_y
        elif 'Antenna_3' == closest_antenna or 'Antenna_4' == closest_antenna:
            line3 = Eq(y, tan(radians(angle3)) * (x - 620) + 980)
            line4 = Eq(y, tan(radians(angle4)) * (x - 220) + 980)
            cal_x, cal_y = calculate_intersection(line3, line4)
            if 733 > cal_x > 0 or 1036 > cal_y > 0:
                plot_points[x], plot_points[y] = cal_x, cal_y

        plot_point([plot_points[x], plot_points[y]])

# Plot the intersection point on the map
def plot_point(point):
    global scatter_beacon, scatter_antenna_1, scatter_antenna_2, antenna_location
    # Convert the coordinates to the image coordinate system
    x_img = point[0]
    y_img = point[1]

    timestamp = datetime.datetime.now().isoformat()

    data_and_time = {
        "timestamp": timestamp,
        "x": str(x_img),
        "y": str(y_img)
    }

    filename = get_filename()
    try:
        with open(filename, 'a') as file:
            json.dump(data_and_time, file)
            file.write(f",\n")
    except Exception as e:
        print(f"Error writing to file: {e}")

    scatter_beacon.set_offsets([x_img, y_img])

    # Draw the closest antenna(s) as blue stars if applicable
    if closest_antenna in ['Antenna_1', 'Antenna_2']:
        scatter_antenna_1.set_offsets(antenna_location['Antenna_1'])
        scatter_antenna_2.set_offsets(antenna_location['Antenna_2'])
    elif closest_antenna in ['Antenna_3', 'Antenna_4']:
        scatter_antenna_1.set_offsets(antenna_location['Antenna_3'])
        scatter_antenna_2.set_offsets(antenna_location['Antenna_4'])

    fig.canvas.draw_idle()  # Redraw the figure to show the updated scatter plot

# Function to be called periodically by FuncAnimation
def animate(i):
    process_data()

# Create an MQTT client instance
client = mqtt.Client(transport="websockets")
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Load the map image
img = mpimg.imread('./ptc_lab.jpg')

# Create a figure and axis for the plot
fig, ax = plt.subplots()
height, width = img.shape[:2]
ax.imshow(img, extent=[0, width, 0, height])

# Create a scatter plot for the point
scatter_beacon = ax.scatter([], [], color='red', marker='o')
scatter_antenna_1 = ax.scatter([], [], color='blue', marker='^')
scatter_antenna_2 = ax.scatter([], [], color='blue', marker='^')

# Start the animation
ani = FuncAnimation(fig, animate, interval=100, blit=False)  # 100 ms = 0.1 seconds

# Start the loop to process network traffic
client.loop_start()

# Show the plot
plt.show()

# Keep the script running until interrupted
try:
    while True:
        pass
except KeyboardInterrupt:
    client.disconnect()
    client.loop_stop()