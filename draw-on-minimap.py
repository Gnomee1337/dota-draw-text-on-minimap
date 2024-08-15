import pyautogui
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import json
import pygetwindow as gw
import time
import keyboard

# Hardcoded coordinates for the drawing area
DRAWING_AREA = (15, 832, 269, 1056)  # (x1, y1, x2, y2)


# Function to load character vectors from JSON file
def load_vectors(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

# Function to calculate maximum scale that fits text in the drawing area
def calculate_max_scale(text, vector_data, area_width, area_height, max_lines):
    char_width = max(
        max(abs(x_end - x_start) for x_start, y_start, x_end, y_end in vector_data[char])
        for char in text if char in vector_data
    ) if text else 0
    char_height = max(
        max(abs(y_end - y_start) for x_start, y_start, x_end, y_end in vector_data[char])
        for char in text if char in vector_data
    ) if text else 0

    lines_needed = -(-len(text) // (area_width // (char_width + 10)))  # Round up
    scale_height = area_height / (lines_needed * char_height + 10 * lines_needed)
    scale_width = area_width / ((area_width // (char_width + 10)) * char_width)

    scale = min(scale_width, scale_height)
    return scale, lines_needed, char_width, char_height

# Function to fit text into the drawing area and calculate the scaling
def fit_text_to_area(text, vector_data, area_width, area_height):
    max_lines = (area_height // (40 * 2))  # Max lines that fit in the height of the area
    scale, lines_needed, char_width, char_height = calculate_max_scale(text, vector_data, area_width, area_height, max_lines)

    # Calculate the number of characters per line
    chars_per_line = int(area_width / (char_width * scale + 10))

    lines = [text[i:i + chars_per_line] for i in range(0, len(text), chars_per_line)]

    # Check if the text fits within the height of the area
    if len(lines) > max_lines:
        lines = lines[:max_lines]

    return scale, lines, char_width, char_height

# Function to draw a character based on vector instructions
def draw_vector_char(char, start_x, start_y, scale=1):
    if char in vectors:
        vector_set = vectors[char]
        for x_start, y_start, x_end, y_end in vector_set:
            if keyboard.is_pressed('esc'):  # Check for 'ESC' key press
                pyautogui.keyUp('ctrl')  # Release 'Ctrl' key
                pyautogui.mouseUp()  # Release mouse button
                status_label.config(text="Drawing canceled!")
                return
            # Scale coordinates and ensure drawing happens within the selected area
            x_start = start_x + x_start * scale
            y_start = start_y + y_start * scale
            x_end = start_x + x_end * scale
            y_end = start_y + y_end * scale
            x_start, y_start = max(min(x_start, DRAWING_AREA[2]), DRAWING_AREA[0]), \
                max(min(y_start, DRAWING_AREA[3]), DRAWING_AREA[1])
            x_end, y_end = max(min(x_end, DRAWING_AREA[2]), DRAWING_AREA[0]), \
                max(min(y_end, DRAWING_AREA[3]), DRAWING_AREA[1])
            pyautogui.moveTo(x_start, y_start)
            pyautogui.dragTo(x_end, y_end, duration=0)

# Function to maximize a specific window
def maximize_window(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        window.activate()
        window.maximize()
        time.sleep(1)  # Small delay to ensure the window is maximized
    except IndexError:
        status_label.config(text=f"Window with title '{window_title}' not found!")

# Function to move cursor to drawing area and start drawing
def draw_text():
    text_to_draw = text_entry.get().upper()

    # Fit text to the drawing area and calculate scale
    area_width = DRAWING_AREA[2] - DRAWING_AREA[0]
    area_height = DRAWING_AREA[3] - DRAWING_AREA[1]
    scale, lines, char_width, char_height = fit_text_to_area(text_to_draw, vectors, area_width, area_height)

    # Maximize the Paint window
    maximize_window("Untitled - Paint")

    # Move cursor to the starting position without holding 'Ctrl' and left click
    pyautogui.moveTo(DRAWING_AREA[0], DRAWING_AREA[1])
    time.sleep(1)  # Wait for 1 second

    # Hold 'Ctrl' key and perform left click
    pyautogui.keyDown('ctrl')
    pyautogui.mouseDown()

    # Set the starting position for the text drawing
    start_x, start_y = DRAWING_AREA[0], DRAWING_AREA[1]

    # Draw each line
    for line in lines:
        current_x = start_x
        for char in line:
            if keyboard.is_pressed('esc'):  # Check for 'ESC' key press
                pyautogui.keyUp('ctrl')  # Release 'Ctrl' key
                pyautogui.mouseUp()  # Release mouse button
                status_label.config(text="Drawing canceled!")
                return
            if char in vectors:
                draw_vector_char(char, current_x, start_y, scale=scale)
                current_x += int((char_width * scale) + 10)  # Adjust spacing between characters
        start_y += int((char_height * scale) + 10)  # Move down to the next line

    # Release 'Ctrl' key and mouse button
    pyautogui.keyUp('ctrl')
    pyautogui.mouseUp()

    status_label.config(text="Drawing complete!")

# Load the character vectors
vectors = load_vectors("char_vectors.json")

# Set up the themed tkinter window
window = ThemedTk(theme="arc")
window.title("Modern Paint Text Drawer")
window.geometry("400x200")

# Text entry
ttk.Label(window, text="Enter Text:").pack(pady=5)
text_entry = ttk.Entry(window, width=30)
text_entry.pack(pady=10)

# Draw button
draw_button = ttk.Button(window, text="Draw in Paint", command=draw_text)
draw_button.pack(pady=10)

# Status label
status_label = ttk.Label(window, text="")
status_label.pack(pady=10)

# Run the tkinter loop
window.mainloop()
