import tkinter as tk
import pyautogui
import signal
import sys

def update_mouse_position():
    x, y = pyautogui.position()
    mouse_position_label.config(text=f"x: {x}    y: {y}")
    overlay.after(100, update_mouse_position)

def signal_handler(sig, frame):
    overlay.destroy()
    sys.exit(0)

overlay = tk.Tk()
overlay.attributes('-alpha', 0.7)
overlay.overrideredirect(True)

mouse_position_label = tk.Label(overlay, text="", font=("Helvetica", 16), fg="white", bg="black")
mouse_position_label.pack(padx=10, pady=10)

update_mouse_position()

signal.signal(signal.SIGINT, signal_handler)

screen_width = overlay.winfo_screenwidth()
screen_height = overlay.winfo_screenheight()

offset_percentage = 10 / 100
overlay_x = int(screen_width * (1 - offset_percentage))
overlay_y = 0

overlay_width = int(screen_width * 0.1)
overlay_height = int(screen_height * 0.05)

overlay.geometry(f"{overlay_width}x{overlay_height}+{overlay_x}+{overlay_y}")

overlay.lift()
overlay.attributes('-topmost', True)

overlay.mainloop()
