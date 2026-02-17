import os
from gpiozero import Button, RotaryEncoder
from signal import pause
from PIL import Image, ImageTk
import tkinter as tk
import subprocess

# -----------------------------
# Settings
# -----------------------------
IMAGE_FOLDER = "/home/mm/wk2pngs"
SOUND_FOLDER = "/home/mm/wk2sound"

ENCODER_DT = 17  # GPIO17
ENCODER_CLK = 27  # GPIO27
SHUTDOWN_BTN_GPIO = 22  # GPIO22
SOUND_BTN_GPIO = 23     # GPIO23

DISPLAY_SIZE = 800  # 800x800 round display

# -----------------------------
# Load media
# -----------------------------
# Images
image_files = sorted([
    os.path.join(IMAGE_FOLDER, f)
    for f in os.listdir(IMAGE_FOLDER)
    if f.lower().endswith(".png")
])
if not image_files:
    raise Exception("No PNG images found in folder!")

current_image_index = 0

# Sounds
sound_files = sorted([
    os.path.join(SOUND_FOLDER, f)
    for f in os.listdir(SOUND_FOLDER)
    if f.lower().endswith(".m4a")
])
if not sound_files:
    raise Exception("No .m4a sound files found in folder!")

current_sound_index = 0
current_process = None  # currently playing audio

# -----------------------------
# Tkinter setup
# -----------------------------
root = tk.Tk()
root.geometry(f"{DISPLAY_SIZE}x{DISPLAY_SIZE}+0+0")
root.configure(background='black')

# Optional: press Escape to exit GUI
root.bind("<Escape>", lambda e: root.destroy())

label = tk.Label(root, bg="black")
label.pack(expand=True)

def show_image(index):
    img = Image.open(image_files[index]).resize((DISPLAY_SIZE, DISPLAY_SIZE))
    tk_img = ImageTk.PhotoImage(img)
    label.config(image=tk_img)
    label.image = tk_img
    root.update()

# Show first image
show_image(current_image_index)

# -----------------------------
# Rotary encoder setup
# -----------------------------
encoder = RotaryEncoder(a=ENCODER_DT, b=ENCODER_CLK, max_steps=0)

def rotated():
    global current_image_index
    if encoder.steps > 0:  # Clockwise
        current_image_index = (current_image_index + 1) % len(image_files)
    elif encoder.steps < 0:  # Counter-clockwise
        current_image_index = (current_image_index - 1) % len(image_files)
    encoder.steps = 0
    show_image(current_image_index)

encoder.when_rotated = rotated

# -----------------------------
# Sound button setup
# -----------------------------
sound_btn = Button(SOUND_BTN_GPIO, pull_up=True)

def play_sound():
    global current_sound_index, current_process

    # Stop current sound
    if current_process is not None and current_process.poll() is None:
        current_process.terminate()
        current_process.wait()

    # Play next sound
    next_sound = sound_files[current_sound_index]
    print(f"Playing index {current_sound_index + 1}/{len(sound_files)}: {next_sound}", flush=True)
    current_process = subprocess.Popen(["cvlc", "--play-and-exit", next_sound])

    # Increment index for next press
    current_sound_index += 1
    if current_sound_index >= len(sound_files):
        current_sound_index = 0

sound_btn.when_pressed = play_sound

# -----------------------------
# Shutdown button setup
# -----------------------------
shutdown_btn = Button(SHUTDOWN_BTN_GPIO, pull_up=True)

def shutdown():
    print("Shutting down...", flush=True)
    subprocess.Popen(["sudo", "shutdown", "now"])

shutdown_btn.when_pressed = shutdown

# -----------------------------
# Start event loop
# -----------------------------
print("Ready: rotate encoder to cycle images, GPIO23 to play sounds, GPIO22 to shutdown.", flush=True)
root.mainloop()
pause()
