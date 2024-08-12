import pyautogui
import time
import keyboard
import tkinter as tk
import json

# Function to load character vectors from JSON file
def load_vectors(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Function to draw a character based on vector instructions
def draw_vector_char(char, start_x, start_y, scale=1):
    if char in vectors:
        vector_set = vectors[char]
        for vector in vector_set:
            x_start, y_start, x_end, y_end = vector
            pyautogui.moveTo(start_x + x_start * scale, start_y + y_start * scale)
            pyautogui.dragTo(start_x + x_end * scale, start_y + y_end * scale, duration=0.001)

# Function to draw text
def draw_text():
    text_to_draw = text_entry.get()
    scale = scale_slider.get()

    # Short delay to allow you to switch to Paint
    status_label.config(text="You have 5 seconds to switch to Paint...")
    window.update()
    time.sleep(5)

    # Set the starting position for the text drawing
    start_x, start_y = pyautogui.position()

    # Adjust this for spacing between characters
    x_offset = 40 * scale

    # Draw each character
    for char in text_to_draw:
        draw_vector_char(char.upper(), start_x, start_y, scale=scale)
        start_x += x_offset

    status_label.config(text="Drawing complete!")

# Load the character vectors
vectors = load_vectors("char_vectors.json")

# Set up the tkinter window
window = tk.Tk()
window.title("Paint Text Drawer")

# Text entry
tk.Label(window, text="Enter Text:").pack()
text_entry = tk.Entry(window, width=30)
text_entry.pack()

# Scale slider
tk.Label(window, text="Scale:").pack()
scale_slider = tk.Scale(window, from_=1, to_=10, orient=tk.HORIZONTAL)
scale_slider.set(1)  # Default scale is 1
scale_slider.pack()

# Draw button
draw_button = tk.Button(window, text="Draw in Paint", command=draw_text)
draw_button.pack()

# Status label
status_label = tk.Label(window, text="")
status_label.pack()

# Run the tkinter loop
window.mainloop()
