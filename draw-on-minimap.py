import win32api
import win32con
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
    # Filter out characters not in vector_data
    valid_chars = [char for char in text if char in vector_data]

    if not valid_chars:
        return 1, 1, 0, 0  # No valid characters, return default values

    def get_max_dimension(dim_index):
        # Collect dimensions for the specified index
        dimensions = []
        for char in valid_chars:
            vectors = vector_data.get(char, [])
            for x_start, y_start, x_end, y_end in vectors:
                if dim_index == 0:  # Width
                    dimensions.append(abs(x_end - x_start))
                elif dim_index == 1:  # Height
                    dimensions.append(abs(y_end - y_start))
        return max(dimensions, default=0)

    char_width = get_max_dimension(0)
    char_height = get_max_dimension(1)

    lines_needed = -(-len(text) // (area_width // (char_width + 10)))  # Round up
    scale_height = area_height / (lines_needed * char_height + 10 * lines_needed)
    scale_width = area_width / ((area_width // (char_width + 10)) * char_width)

    scale = min(scale_width, scale_height)
    return scale, lines_needed, char_width, char_height


# Function to fit text into the drawing area and calculate the scaling
def fit_text_to_area(text, vector_data, area_width, area_height):
    # Determine maximum scale based on the area size and the text
    scale, lines_needed, char_width, char_height = calculate_max_scale(text, vector_data, area_width, area_height,
                                                                       max_lines=None)
    # Calculate the number of characters per line
    chars_per_line = int(area_width / (char_width * scale + 5))

    # Split the text into lines based on the number of characters per line
    lines = [text[i:i + chars_per_line] for i in range(0, len(text), chars_per_line)]

    # Calculate the height per line dynamically based on the number of lines
    line_height = area_height // len(lines) if len(lines) > 0 else area_height

    return scale, lines, char_width, line_height


# Function to draw a character based on vector instructions
def draw_vector_char(char, start_x, start_y, scale=1):
    # Check if the character is in vectors and has valid segments
    if char in vectors and vectors[char]:
        # vector_set = vectors[char]
        first_segment = vectors[char][0]
        x_start = start_x + first_segment[0] * scale
        y_start = start_y + first_segment[1] * scale
        win32api.SetCursorPos((int(x_start), int(y_start)))
        time.sleep(0.05)  # Small delay to ensure the game processes the movement
        # Press CTRL and LEFT MOUSE BUTTON only when starting to draw the character
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        # Draw each segment of the character
        for segment in vectors[char]:
            if keyboard.is_pressed('esc'):  # Check for 'ESC' key press
                # Release 'Ctrl' key and mouse button
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                status_label.config(text="Drawing canceled!")
                return

            # Get the start and end points of the segment
            x_start_segment, y_start_segment, x_end_segment, y_end_segment = segment

            # Scale coords and set the starting and ending points
            x_start_segment = start_x + x_start_segment * scale
            y_start_segment = start_y + y_start_segment * scale
            x_end_segment = start_x + x_end_segment * scale
            y_end_segment = start_y + y_end_segment * scale

            # Ensure drawing happens within the selected area
            x_start_segment = max(min(x_start_segment, DRAWING_AREA[2]), DRAWING_AREA[0])
            y_start_segment = max(min(y_start_segment, DRAWING_AREA[3]), DRAWING_AREA[1])
            x_end_segment = max(min(x_end_segment, DRAWING_AREA[2]), DRAWING_AREA[0])
            y_end_segment = max(min(y_end_segment, DRAWING_AREA[3]), DRAWING_AREA[1])

            # Move to the starting point of the segment WITHOUT holding mouse button
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)  # Ensure mouse is released
            win32api.SetCursorPos((int(x_start_segment), int(y_start_segment)))
            time.sleep(0.005)  # Small delay to ensure proper movement

            # Ensure mouse button is fully released before proceeding
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            time.sleep(0.01)  # A short delay to ensure no accidental line drawing

            # Press LEFT MOUSE BUTTON to start drawing the segment
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)

            # # win32api.SetCursorPos((int(x_start), int(y_start)))
            # win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)

            # Interpolate movement between the start and end points for smooth drawing
            steps = 50  # Number of steps for smoother movement
            dx = (x_end_segment - x_start_segment) / steps
            dy = (y_end_segment - y_start_segment) / steps

            for i in range(steps):
                x_current = x_start_segment + dx * i
                y_current = y_start_segment + dy * i
                win32api.SetCursorPos((int(x_current), int(y_current)))
                time.sleep(0.005)  # Small delay for each step

            # win32api.SetCursorPos((int(x_end), int(y_end)))
            # Release 'Ctrl' key and mouse button
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            time.sleep(0.01)  # Ensure no line drawing between segments
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)


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

    # Filter the text to include only characters present in vector_data
    filtered_text = ''.join(char for char in text_to_draw if char in vectors)

    # If no valid characters, show an error message
    if not filtered_text:
        status_label.config(text="No valid characters to draw.")
        return

    scale, lines, char_width, line_height = fit_text_to_area(text_to_draw, vectors, area_width, area_height)

    # Adjust the spacing dynamically based on the size of characters
    spacing_ratio = 0.2

    # Maximize the Paint window
    maximize_window("Dota")

    # Move cursor to the starting position without holding 'Ctrl' and left click
    win32api.SetCursorPos((DRAWING_AREA[0], DRAWING_AREA[1]))
    time.sleep(1)  # Wait for 1 second

    # Set the starting position for the text drawing
    start_x, start_y = DRAWING_AREA[0], DRAWING_AREA[1]

    # Draw each line
    for line in lines:
        current_x = start_x
        for char in line:
            if keyboard.is_pressed('esc'):  # Check for 'ESC' key press
                # Release 'Ctrl' key and mouse button
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                status_label.config(text="Drawing canceled!")
                return
                # Check if the character is in the vectors and has valid segments
                # if char in vectors and vectors[char]:
                #     # Move the cursor to the starting position of the character WITHOUT holding keys
                #     first_segment = vectors[char][0]
                #     x_start = current_x + first_segment[0] * scale
                #     y_start = start_y + first_segment[1] * scale
                #     win32api.SetCursorPos((int(x_start), int(y_start)))
                #     time.sleep(0.05)  # Optional: add a small delay to ensure the game processes the movement
            draw_vector_char(char, current_x, start_y, scale=scale)
            # Adjust spacing between characters
            current_x += int((char_width * scale) + (char_width * spacing_ratio * scale))
        start_y += line_height  # Move down to the next line
    status_label.config(text="Drawing complete!")


# Load the character vectors
vectors = load_vectors("char_vectors.json")

# Set up the themed tkinter window
window = ThemedTk(theme="arc")
window.title("Text to Minimap Painter")
window.geometry("400x200")

# Text entry
ttk.Label(window, text="Enter Text:").pack(pady=5)
text_entry = ttk.Entry(window, width=30)
text_entry.pack(pady=10)

# Draw button
draw_button = ttk.Button(window, text="Draw", command=draw_text)
draw_button.pack(pady=10)

# Status label
status_label = ttk.Label(window, text="")
status_label.pack(pady=10)

# Run the tkinter loop
window.mainloop()
