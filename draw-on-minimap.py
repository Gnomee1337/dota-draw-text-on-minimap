import pyautogui
import time
import keyboard
import json

# Load vector data from JSON file
with open('char_vectors.json', 'r') as f:
    char_vectors = json.load(f)

# Function to draw a character based on vector instructions
def draw_vector_char(char, start_x, start_y, scale=1):
    vectors = char_vectors.get(char.upper(), [])
    for vector in vectors:
        x_start, y_start, x_end, y_end = vector
        pyautogui.moveTo(start_x + x_start * scale, start_y + y_start * scale)
        pyautogui.dragTo(start_x + x_end * scale, start_y + y_end * scale, duration=0.001)

# User inputs the text
text_to_draw = input("Enter the text to draw in Paint: ")

# Short delay to allow you to switch to Paint
print("You have 5 seconds to switch to Paint...")
time.sleep(5)

# Set the starting position for the text drawing
start_x, start_y = pyautogui.position()

# Adjust this for spacing between characters
x_offset = 40
scale = 1  # Scaling factor for the size of the drawn characters

# Draw each character
for char in text_to_draw:
    draw_vector_char(char, start_x, start_y, scale=scale)
    start_x += x_offset * scale  # Move to the next character's starting position

print("Drawing complete or canceled!")
