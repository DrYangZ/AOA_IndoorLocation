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
    'Antenna_1' : None,
    'Antenna_2' : None,
    'Antenna_3' : None,
    'Antenna_4' : None
}
flag =  False
closest_antenna = None
plot_points = {
    x : 200,
    y : 100
}

def get_filename():
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    file_name = f"C:/Users/adminptca13/Desktop/WebSocket_Server/location_record_{date_str}.txt"
    return file_name

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_TOPIC1)
    client.subscribe(MQTT_TOPIC2)
    client.subscribe(MQTT_TOPIC3)
    client.subscribe(MQTT_TOPIC4)

# Callback when a message is received
def on_message(client, userdata, msg):
    global angle1, angle2, angle3, angle4, distance_dict, closest_antenna
    data = json.loads(msg.payload.decode())
    # print(f"topic:{msg.topic}, message:{msg.payload.decode()}")
    if msg.topic == MQTT_TOPIC1:
        angle1 = -data['azimuth']
        distance_dict['Antenna_1'] = data['distance']
        # print(f"Antenna 1 的距离是：{data['distance']}")
    elif msg.topic == MQTT_TOPIC2:
        angle2 = -data['azimuth']
        distance_dict['Antenna_2'] = data['distance']
        # print(f"Antenna 2 的距离是：{data['distance']}")
    elif msg.topic == MQTT_TOPIC3:
        angle3 = -data['azimuth']
        distance_dict['Antenna_3'] = data['distance']
        # print(f"Antenna 3 的距离是：{data['distance']}")
    elif msg.topic == MQTT_TOPIC4:
        angle4 = -data['azimuth']
        distance_dict['Antenna_4'] = data['distance']
        # print(f"Antenna 4 的距离是：{data['distance']}")
    # print(angle1, angle2, angle3, angle4)
    flag = all(distance_dict.values())
    if flag:
        # print(f"The current distances of all antennas are:\n{distance_dict}")
        sorted_items = sorted(distance_dict.items(), key=lambda item: item[1])
        closest_antenna = sorted_items[0][0]
        print(f"The closest antenna is:\n{closest_antenna}")


def calculate_intersection(line1, line2):
    # 解方程组
    solution = solve((line1, line2), (x, y))
    # print([solution[x], solution[y]])
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
            else:
                pass
        elif 'Antenna_3' == closest_antenna or 'Antenna_4' == closest_antenna:
            line3 = Eq(y, tan(radians(angle3)) * (x - 620) + 980)
            line4 = Eq(y, tan(radians(angle4)) * (x - 220) + 980)
            cal_x, cal_y = calculate_intersection(line3, line4)
            if 733 > cal_x > 0 or 1036 > cal_y > 0:
                plot_points[x], plot_points[y] = cal_x, cal_y
            else:
                pass

        print(f"当前定位点坐标为:\n{[plot_points[x], plot_points[y]]}\n")
        plot_point([plot_points[x], plot_points[y]])

# Plot the intersection point on the map
def plot_point(point):
    global scatter
    # Convert the coordinates to the image coordinate system
    # Assuming the image has its origin at the lower left corner
    x_img = point[0]
    y_img = point[1]

    timestamp = datetime.datetime.now().isoformat()

    data_and_time = {
        "timestamp": timestamp,
        "x": str(x_img),
        "y": str(y_img)
    }

    filename = get_filename()
    with open(filename, 'a') as file:
        json.dump(data_and_time, file)
        file.write(f",\n")
    print(x_img, y_img)

    # Update the scatter plot with new data
    scatter.set_offsets([x_img, y_img])
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

# # Set the limits of the axes to fix the origin at the bottom right corner
# ax.set_xlim(width, 0)  # 横坐标范围从宽度到0
# ax.set_ylim(0, height)  # 纵坐标范围从0到高度

# Create a scatter plot for the point
scatter = ax.scatter([], [], color='red', marker='o')

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