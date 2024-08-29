import json
import time
import threading
import keyboard
import sys
import numpy as np
import mss
from mss import mss as mss_module
from ctypes import WinDLL
from PIL import Image, ImageDraw
import win32api
import subprocess
from pystray import Icon, MenuItem, Menu

def exiting():
    print("Exiting the script...")
    try:
        sys.exit()  # Cleanly exit the script
    except SystemExit:
        pass  # Handle the system exit, so it doesn't propagate as an error

user32, kernel32, shcore = (
    WinDLL("user32", use_last_error=True),
    WinDLL("kernel32", use_last_error=True),
    WinDLL("shcore", use_last_error=True),
)

shcore.SetProcessDpiAwareness(2)
WIDTH, HEIGHT = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

ZONE = 5
GRAB_ZONE = (
    int(WIDTH / 2 - ZONE+1),
    int(HEIGHT / 2 - ZONE-14),
    int(WIDTH / 2 + ZONE-1),
    int(HEIGHT / 2 + ZONE - 1),
)

script = "Vandal.AHK"

def exit_program(icon, item):
    print("Exit program triggered from tray menu.")
    icon.stop()
    exiting()

def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        [width // 2, 0, width, height // 2],
        fill=color2)
    dc.rectangle(
        [0, height // 2, width // 2, height],
        fill=color2)
    return image

class CaptureGraphicValues:
    def __init__(self):
        print("Initializing CaptureGraphicValues class...")
        self.sct = mss_module()
        self.captureGraphicValues = False
        self.captureGraphicValue_BoardMemory = True
        self.exit_program = False
        self.toggle_lock = threading.Lock()

        with open('config.json') as json_file:
            data = json.load(json_file)

        try:
            self.ViewGraph_hotkey = int(data["ViewGraph_hotkey"], 16)
            print(f"Hotkey set to: {hex(self.ViewGraph_hotkey)}")
            self.always_enabled = data["always_enabled"]
            self.screenMS_delay = data["screenMS_delay"]
            self.base_delay = data["base_delay"]
            self.just_delay = 120  # Set the delay to 120 ms
            self.FindBroken_pixel = data["FindBroken_pixel"]
            self.R, self.G, self.B = (250, 100, 250)  # purple
            print(f"Color detection set to: R={self.R}, G={self.G}, B={self.B}")
        except Exception as e:
            print(f"Error in initializing CaptureGraphicValues: {e}")
            exiting()

    def cooldown(self):
        time.sleep(0.1)
        with self.toggle_lock:
            self.captureGraphicValue_BoardMemory = True
            print(f"CaptureGraphicValues toggled to: {self.captureGraphicValues}")
            if self.captureGraphicValues:
                kernel32.Beep(440, 75)
                kernel32.Beep(700, 100)
            else:
                kernel32.Beep(440, 75)
                kernel32.Beep(200, 100)

    def searcherino(self):
        print("Capturing screen for color detection...")
        img = np.array(self.sct.grab(GRAB_ZONE))

        pmap = np.array(img)
        pixels = pmap.reshape(-1, 4)

        color_mask = (
            (pixels[:, 0] > self.R - self.FindBroken_pixel) & (pixels[:, 0] < self.R + self.FindBroken_pixel) &
            (pixels[:, 1] > self.G - self.FindBroken_pixel) & (pixels[:, 1] < self.G + self.FindBroken_pixel) &
            (pixels[:, 2] > self.B - self.FindBroken_pixel) & (pixels[:, 2] < self.B + self.FindBroken_pixel)
        )

        matching_pixels = pixels[color_mask]
        print(f"Matching pixels detected: {len(matching_pixels)}")

        if self.captureGraphicValues and len(matching_pixels) > 0:
            delay_percentage = self.screenMS_delay / 100.0
            actual_delay = self.base_delay * delay_percentage
            print(f"Calculated delay: {actual_delay} seconds")

            print(f"Running AutoHotkey script: {script}")
            subprocess.run(["C:\\Program Files\\AutoHotkey\\AutoHotkey.exe", script])

            time.sleep(self.just_delay / 1000)
            print(f"Script executed with delay: {self.just_delay / 1000} seconds")

    def toggle(self):
        if keyboard.is_pressed("f10"):
            with self.toggle_lock:
                if self.captureGraphicValue_BoardMemory:
                    self.captureGraphicValues = not self.captureGraphicValues
                    print(f"CaptureGraphicValues toggled to: {self.captureGraphicValues}")
                    self.captureGraphicValue_BoardMemory = False
                    threading.Thread(target=self.cooldown).start()

        if keyboard.is_pressed("ctrl+shift+x"):
            print("Exit command detected. Exiting...")
            self.exit_program = True
            exiting()

    def hold(self):
        global script
        while True:
            if keyboard.is_pressed("shift"):  # Check for Left Shift key
                if keyboard.is_pressed("f8"):
                    self.just_delay = 25
                    script = "Sheriff.ahk"
                    print(f"Script switched to: {script}")
                    kernel32.Beep(700, 1000)
                    time.sleep(1)
                elif keyboard.is_pressed("f7"):
                    self.just_delay = 120  # Set delay to 120 ms
                    script = "Vandal.ahk"
                    print(f"Script switched to: {script}")
                    kernel32.Beep(700, 500)
                    time.sleep(1)
                elif keyboard.is_pressed("f6"):
                    self.just_delay = 5
                    script = "Pistol.ahk"
                    print(f"Script switched to: {script}")
                    kernel32.Beep(700, 200)
                    time.sleep(1)

                if win32api.GetAsyncKeyState(self.ViewGraph_hotkey) & 0x8000:
                    print(f"Hotkey {hex(self.ViewGraph_hotkey)} pressed. Starting color detection...")
                    self.captureGraphicValues = True
                    self.searcherino()
                else:
                    time.sleep(0.1)
            else:
                time.sleep(0.1)  # Wait while LSHIFT is not pressed

            if keyboard.is_pressed("ctrl+shift+x"):
                print("Exit command detected. Exiting...")
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

def main():
    print("Starting the main program...")
    image = create_image(64, 64, 'black', 'white')
    menu = Menu(
        MenuItem('Exit', exit_program)
    )
    icon = Icon("test", image, "Tray Icon Example", menu)

    tray_thread = threading.Thread(target=icon.run)
    tray_thread.daemon = True
    tray_thread.start()
    CaptureGraphicValues().starterino()

main()
