import json
import paho.mqtt.client as mqtt
from sympy import *
import matplotlib.pyplot as plt
import datetime
import matplotlib.image as mpimg
from matplotlib.animation import FuncAnimation
from math import *

# MQTT setup
MQTT_BROKER = "localhost"  # or the IP address of your Mosquitto server
MQTT_PORT = 8766  # default WebSocket port for Mosquitto
MQTT_TOPIC1 = "silabs/aoa/angle/ble-pd-0C4314F469A4/ble-pd-84FD27EEE588"
MQTT_TOPIC2 = "silabs/aoa/angle/ble-pd-0C4314F45C80/ble-pd-84FD27EEE588"

# Initialize SymPy symbols
x, y = symbols('x y')

# Global variables to hold the latest angles
angle1 = None
angle2 = None

def get_filename():
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    file_name = f"C:/Users/adminptca13/Desktop/WebSocket_Server/location_record_{date_str}.txt"
    return file_name

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_TOPIC1)
    client.subscribe(MQTT_TOPIC2)

# Callback when a message is received
def on_message(client, userdata, msg):
    global angle1, angle2
    data = json.loads(msg.payload.decode())
    # print(f"topic:{msg.topic}, message:{msg.payload.decode()}")
    if msg.topic == MQTT_TOPIC1:
        angle1 = 90 + data['azimuth']
    elif msg.topic == MQTT_TOPIC2:
        angle2 = 270 + data['azimuth']
    # print(angle1, angle2)

# Process data and update plot
def process_data():
    global angle1, angle2
    if angle1 is not None and angle2 is not None:
        print(f"angle_1 and angle_2 are {[angle1, angle2]}")
        # Define the line equations for topic1 and topic2
        line1 = Eq(y, tan(radians(angle1)) * (x - 1000) + 700)
        line2 = Eq(y, tan(radians(angle2)) * (x - 1000))

        # Solve the intersection point
        intersection_point = solve((line1, line2), (x, y))
        plot_point(intersection_point)

# Plot the intersection point on the map
def plot_point(point):
    global scatter
    # Convert the coordinates to the image coordinate system
    # Assuming the image has its origin at the lower left corner
    x_img = point[x]
    y_img = point[y]

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
ax.imshow(img)

height, width = img.shape[:2]
print(height, width)
# ax.set_xlim(0, width)  # 横坐标范围从0到宽度
# ax.set_ylim(height, 0)  # 纵坐标范围从高度到0

# Create a scatter plot for the point
scatter = ax.scatter([], [], color='red', marker='o')

# Start the animation
ani = FuncAnimation(fig, animate, interval=10, blit=False)  # 100 ms = 0.1 seconds

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