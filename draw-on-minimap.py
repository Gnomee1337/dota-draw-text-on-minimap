import pyautogui
import tkinter as tk
import json
import pygetwindow as gw
import time
import keyboard

# Function to load character vectors from JSON file
def load_vectors(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Function to draw a character based on vector instructions
def draw_vector_char(char, start_x, start_y, scale=1):
    if char in vectors:
        vector_set = vectors[char]
        for x_start, y_start, x_end, y_end in vector_set:
            if keyboard.is_pressed('esc'):  # Check for 'ESC' key press
                status_label.config(text="Drawing canceled!")
                return
            pyautogui.moveTo(start_x + x_start * scale, start_y + y_start * scale)
            pyautogui.dragTo(start_x + x_end * scale, start_y + y_end * scale, duration=0)

# Function to maximize a specific window (e.g., "Paint")
def maximize_window(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        window.activate()
        window.maximize()
        time.sleep(1)  # Small delay to ensure the window is maximized
    except IndexError:
        status_label.config(text=f"Window with title '{window_title}' not found!")

# Function to draw text
def draw_text():
    text_to_draw = text_entry.get().upper()
    scale = scale_slider.get()

    # Maximize the Paint window
    maximize_window("Untitled - Paint")

    # Set the starting position for the text drawing
    start_x, start_y = pyautogui.position()

    # Adjust this for spacing between characters
    x_offset = int(40 * scale)

    # Draw each character
    for char in text_to_draw:
        if keyboard.is_pressed('esc'):  # Check for 'ESC' key press
            status_label.config(text="Drawing canceled!")
            return
        if char in vectors:
            draw_vector_char(char, start_x, start_y, scale=scale)
            start_x += x_offset

    status_label.config(text="Drawing complete!")

# Load the character vectors
vectors = load_vectors("char_vectors.json")

# Set up the tkinter window
window = tk.Tk()
window.title("Paint Text Drawer")

# Text entry
tk.Label(window, text="Enter Text:").pack(pady=5)
text_entry = tk.Entry(window, width=30)
text_entry.pack()

# Scale slider
tk.Label(window, text="Scale:").pack(pady=5)
scale_slider = tk.Scale(window, from_=1, to_=10, orient=tk.HORIZONTAL)
scale_slider.set(1)  # Default scale is 1
scale_slider.pack()

# Draw button
draw_button = tk.Button(window, text="Draw in Paint", command=draw_text)
draw_button.pack(pady=10)

# Status label
status_label = tk.Label(window, text="")
status_label.pack()

# Run the tkinter loop
window.mainloop()
