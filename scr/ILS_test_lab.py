import tkinter as tk
from tkinter import* #neu
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

def update_circle_position(circle, x, y):
    circle.center = (x, y)
    circle.figure.canvas.draw()

def on_apply():
    x = float(entry_x.get())
    y = float(entry_y.get())
    update_circle_position(circle, x, y)

# Create Matplotlib plot
fig, ax = plt.subplots()
ax.set_xlim(750, 0)
ax.set_ylim(0, 465)

img = plt.imread("ptc_lab.jpg")
ax.imshow(img, extent=[750, 0, 0, 465])

# Initialize circle
center = (5, 5)
radius = 10
circle = Circle(center, radius, edgecolor='b', facecolor='b')
ax.add_patch(circle)

# Create tkinter GUI window
root = tk.Tk()
root.title("Circle Position Input")

# Label and Entry widgets for x and y coordinates label_x = tk.Label(root, text="X coordinate:")
label_x = tk.Label(root, text="X coordinate:")
label_x.pack()
entry_x = tk.Entry(root)
entry_x.pack()

label_y = tk.Label(root, text="Y coordinate:")
label_y.pack()
entry_y = tk.Entry(root)
entry_y.pack()

# Button to apply the coordinates
btn_apply = tk.Button(root, text="Apply", command=on_apply)
btn_apply.pack()

ax.set_title('ILS Test Lab made by PTC')
ax.set_aspect('equal')

plt.show()
root.mainloop()