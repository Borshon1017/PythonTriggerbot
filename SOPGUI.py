import tkinter as tk
from tkinter import messagebox
import threading
import keyboard
import sys
import time  # Add this line to import the time module
import numpy as np
import mss
from mss import mss as mss_module
from ctypes import WinDLL
import win32api
import subprocess

# Set up the GUI
class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry("200x400")
        self.root.title("Script Controller")

        self.running = False
        self.color_choice = tk.StringVar(value="purple")
        self.hotkey = tk.StringVar(value="0xa0")
        self.delay = tk.IntVar(value=120)

        self.start_button = tk.Button(root, text="Start", command=self.toggle_script)
        self.start_button.pack(pady=20)

        self.color_label = tk.Label(root, text="Choose Color:")
        self.color_label.pack()

        self.purple_radio = tk.Radiobutton(root, text="Purple", variable=self.color_choice, value="purple")
        self.purple_radio.pack()

        self.yellow_radio = tk.Radiobutton(root, text="Yellow", variable=self.color_choice, value="yellow")
        self.yellow_radio.pack()

        self.hotkey_label = tk.Label(root, text="Hotkey (Hex):")
        self.hotkey_label.pack()

        self.hotkey_entry = tk.Entry(root, textvariable=self.hotkey)
        self.hotkey_entry.pack()

        self.delay_label = tk.Label(root, text="Delay (ms):")
        self.delay_label.pack()

        self.delay_entry = tk.Entry(root, textvariable=self.delay)
        self.delay_entry.pack()

    def toggle_script(self):
        if not self.running:
            self.start_button.config(text="Stop")
            self.running = True
            threading.Thread(target=self.run_script).start()
        else:
            self.start_button.config(text="Start")
            self.running = False

    def run_script(self):
        capture_graphic_values = CaptureGraphicValues(
            color=self.color_choice.get(),
            hotkey=int(self.hotkey.get(), 16),
            delay=self.delay.get()
        )
        capture_graphic_values.starterino()

class CaptureGraphicValues:
    def __init__(self, color, hotkey, delay):
        self.sct = mss_module()
        self.captureGraphicValues = False
        self.captureGraphicValue_BoardMemory = True
        self.exit_program = False
        self.toggle_lock = threading.Lock()

        self.ViewGraph_hotkey = hotkey
        self.always_enabled = True
        self.screenMS_delay = 100
        self.base_delay = delay
        self.just_delay = delay

        if color == "purple":
            self.R, self.G, self.B = (250, 100, 250)
        elif color == "yellow":
            self.R, self.G, self.B = (255, 255, 0)  # Basic yellow

        self.FindBroken_pixel = 30

    def cooldown(self):
        time.sleep(0.1)
        with self.toggle_lock:
            self.captureGraphicValue_BoardMemory = True
            if self.captureGraphicValues:
                kernel32.Beep(440, 75)
                kernel32.Beep(700, 100)
            else:
                kernel32.Beep(440, 75)
                kernel32.Beep(200, 100)

    def searcherino(self):
        img = np.array(self.sct.grab(GRAB_ZONE))

        pmap = np.array(img)
        pixels = pmap.reshape(-1, 4)

        color_mask = (
            (pixels[:, 0] > self.R - self.FindBroken_pixel) & (pixels[:, 0] < self.R + self.FindBroken_pixel) &
            (pixels[:, 1] > self.G - self.FindBroken_pixel) & (pixels[:, 1] < self.G + self.FindBroken_pixel) &
            (pixels[:, 2] > self.B - self.FindBroken_pixel) & (pixels[:, 2] < self.B + self.FindBroken_pixel)
        )

        matching_pixels = pixels[color_mask]

        if self.captureGraphicValues and len(matching_pixels) > 0:
            delay_percentage = self.screenMS_delay / 100.0
            actual_delay = self.base_delay * delay_percentage

            subprocess.run(["C:\\Program Files\\AutoHotkey\\AutoHotkey.exe", script])

            time.sleep(self.just_delay / 1000)

    def toggle(self):
        if keyboard.is_pressed("f10"):
            with self.toggle_lock:
                if self.captureGraphicValue_BoardMemory:
                    self.captureGraphicValues = not self.captureGraphicValues
                    self.captureGraphicValue_BoardMemory = False
                    threading.Thread(target=self.cooldown).start()

        if keyboard.is_pressed("ctrl+shift+x"):
            self.exit_program = True
            exiting()

    def hold(self):
        global script
        while True:
            if keyboard.is_pressed("shift"):
                if win32api.GetAsyncKeyState(self.ViewGraph_hotkey) & 0x8000:
                    self.captureGraphicValues = True
                    self.searcherino()
                else:
                    time.sleep(0.1)
            else:
                time.sleep(0.1)

            if keyboard.is_pressed("ctrl+shift+x"):
                self.exit_program = True
                exiting()

    def starterino(self):
        while not self.exit_program:
            if self.always_enabled:
                self.toggle()
                if self.captureGraphicValues:
                    self.searcherino()
                else:
                    time.sleep(0.1)
            else:
                self.hold()

def exiting():
    sys.exit()

if __name__ == "__main__":
    user32, kernel32, shcore = (
        WinDLL("user32", use_last_error=True),
        WinDLL("kernel32", use_last_error=True),
        WinDLL("shcore", use_last_error=True),
    )

    shcore.SetProcessDpiAwareness(2)
    WIDTH, HEIGHT = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

    ZONE = 5
    GRAB_ZONE = (
        int(WIDTH / 2 - ZONE + 1),
        int(HEIGHT / 2 - ZONE - 14),
        int(WIDTH / 2 + ZONE - 1),
        int(HEIGHT / 2 + ZONE - 1),
    )

    script = "Vandal.AHK"

    root = tk.Tk()
    app = App(root)
    root.mainloop()
