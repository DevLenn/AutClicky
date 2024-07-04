import tkinter as tk
from tkinter import messagebox, filedialog, PhotoImage
from tkinter import ttk
import json
import time
import pyautogui
import subprocess
import os
import sys
import argparse

class ClickApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutClick")
        self.root.configure(bg='#2e2e2e')
        self.root.resizable(False, False)

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pp.png')
        if os.path.exists(icon_path):
            icon = PhotoImage(file=icon_path)
            self.root.iconphoto(False, icon)


        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#2e2e2e')
        self.style.configure('TLabel', background='#2e2e2e', foreground='white')
        self.style.configure('TButton', background='#444444', foreground='white', borderwidth=0, focuscolor='none')
        self.style.configure('TEntry', fieldbackground='#444444', foreground='white')
        self.style.map('TButton', background=[('active', '#666666')])

        self.entries = []
        self.overlay_process = None

        self.main_frame = ttk.Frame(root)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.canvas = tk.Canvas(self.main_frame, bg='#2e2e2e')
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.entry_frame = ttk.Frame(self.canvas)
        self.entry_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.entry_frame, anchor="nw")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.button_frame = ttk.Frame(root)
        self.button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.load_button = ttk.Button(self.button_frame, text="Load Config", command=self.load_config)
        self.load_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.save_button = ttk.Button(self.button_frame, text="Save Config", command=self.save_config)
        self.save_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.add_button = ttk.Button(self.button_frame, text="Plus", command=self.add_entry)
        self.add_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.click_button = ttk.Button(self.button_frame, text="Click", command=self.start_clicks)
        self.click_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.repetitions_label = ttk.Label(self.button_frame, text="Repetitions:")
        self.repetitions_label.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

        self.repetitions_entry = ttk.Entry(self.button_frame, validate="key", validatecommand=(root.register(self.validate_int), '%P'))
        self.repetitions_entry.grid(row=0, column=5, padx=5, pady=5, sticky="ew")
        self.repetitions_entry.insert(0, "1")

        self.overlay_button = ttk.Button(self.button_frame, text="Toggle Overlay", command=self.toggle_overlay)
        self.overlay_button.grid(row=0, column=6, padx=5, pady=5, sticky="ew")

        self.add_entry()

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.entry_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.grid_columnconfigure(3, weight=1)
        self.button_frame.grid_columnconfigure(4, weight=1)
        self.button_frame.grid_columnconfigure(5, weight=1)
        self.button_frame.grid_columnconfigure(6, weight=1)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def toggle_overlay(self):
        if self.overlay_process is None:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reader.py')
            self.overlay_process = subprocess.Popen([sys.executable, script_path])
        else:
            self.overlay_process.terminate()
            self.overlay_process = None

    def add_entry(self):
        frame = ttk.Frame(self.entry_frame)
        frame.grid(pady=5, padx=5, sticky="ew")

        x_label = ttk.Label(frame, text="x:")
        x_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        x_entry = ttk.Entry(frame, validate="key", validatecommand=(self.root.register(self.validate_int), '%P'))
        x_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        y_label = ttk.Label(frame, text="y:")
        y_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        y_entry = ttk.Entry(frame, validate="key", validatecommand=(self.root.register(self.validate_int), '%P'))
        y_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        speed_label = ttk.Label(frame, text="speed:")
        speed_label.grid(row=0, column=4, padx=5, pady=5, sticky="e")
        speed_entry = ttk.Entry(frame, validate="key", validatecommand=(self.root.register(self.validate_float), '%P'))
        speed_entry.grid(row=0, column=5, padx=5, pady=5, sticky="ew")
        speed_entry.bind('<Return>', lambda event: self.add_entry())
        speed_entry.bind('<Delete>', lambda event, f=frame: self.remove_entry(f))

        remove_button = ttk.Button(frame, text="Remove", command=lambda f=frame: self.remove_entry(f))
        remove_button.grid(row=0, column=6, padx=5, pady=5, sticky="ew")

        self.entries.append((x_entry, y_entry, speed_entry, frame))


        for i in range(7):
            frame.grid_columnconfigure(i, weight=1)

        self.entry_frame.grid_rowconfigure(len(self.entries) - 1, weight=1)

    def remove_entry(self, frame):
        for entry in self.entries:
            if entry[3] == frame:
                entry[3].grid_forget()
                self.entries.remove(entry)
                break

    def validate_int(self, value):
        return value.lstrip('-').isdigit() or value == ""

    def validate_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return value == ""

    def start_clicks(self):
        coords = []
        for entry in self.entries:
            try:
                x = int(entry[0].get())
                y = int(entry[1].get())
                speed = float(entry[2].get())
                coords.append((x, y, speed))
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers.")
                return

        try:
            repetitions = int(self.repetitions_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of repetitions.")
            return

        self.root.after(1000, self.countdown, 3, coords, repetitions)

    def countdown(self, count, coords, repetitions):
        if count > 0:
            self.click_button.config(text=f"Click ({count})")
            self.root.after(1000, self.countdown, count - 1, coords, repetitions)
        else:
            self.click_button.config(text="Click")
            self.perform_clicks(coords, repetitions)

    def perform_clicks(self, coords, repetitions):
        for _ in range(repetitions):
            for i, (x, y, speed) in enumerate(coords):
                if i > 0:
                    time.sleep(coords[i-1][2])
                pyautogui.click(x, y)
            time.sleep(coords[-1][2])

    def save_config(self):
        coords = []
        for entry in self.entries:
            try:
                x = int(entry[0].get())
                y = int(entry[1].get())
                speed = float(entry[2].get())
                coords.append((x, y, speed))
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers.")
                return

        config = {
            "coords": coords,
            "repetitions": self.repetitions_entry.get()
        }

        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(config, f)

    def load_config(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                config = json.load(f)

            for entry in self.entries:
                entry[3].grid_forget()
            self.entries = []

            for coord in config["coords"]:
                self.add_entry()
                self.entries[-1][0].insert(0, coord[0])
                self.entries[-1][1].insert(0, coord[1])
                self.entries[-1][2].insert(0, coord[2])

            self.repetitions_entry.delete(0, tk.END)
            self.repetitions_entry.insert(0, config["repetitions"])

    def on_closing(self):
        if self.overlay_process is not None:
            self.overlay_process.terminate()
        self.root.destroy()

def cmd_mode():
    config_path = input("Path to config file (.json): ")
    if not os.path.exists(config_path):
        print("Config file not found!")
        return

    with open(config_path, 'r') as f:
        config = json.load(f)

    change_reps = input("Want to change reps? (y/n): ").strip().lower()
    if change_reps == 'y':
        reps = input("Enter new number of repetitions: ").strip()
        if reps.isdigit():
            config['repetitions'] = reps
        else:
            print("Invalid input, must be a number.")
            return

    execute = input("Execute (y/n): ").strip().lower()
    if execute == 'y':
        coords = config['coords']
        repetitions = int(config['repetitions'])
        for _ in range(repetitions):
            for i, (x, y, speed) in enumerate(coords):
                if i > 0:
                    time.sleep(coords[i-1][2])
                pyautogui.click(x, y)
            time.sleep(coords[-1][2])

        save_reps = input("Do you want to save the reps in your config (.json) file (y/n)?: ").strip().lower()
        if save_reps == 'y':
            save_option = input("Existing or new one? (e/n): ").strip().lower()
            if save_option == 'e':
                with open(config_path, 'w') as f:
                    json.dump(config, f)
            elif save_option == 'n':
                new_path = input("Enter path and filename to save new config: ").strip()
                with open(new_path, 'w') as f:
                    json.dump(config, f)
            else:
                print("Invalid input.")
        else:
            print("Config not saved.")
    else:
        print("Execution aborted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutClick Application")
    parser.add_argument("-c", "--cmd", action="store_true", help="Run in command line mode")
    args = parser.parse_args()

    if args.cmd:
        cmd_mode()
    else:
        root = tk.Tk()
        app = ClickApp(root)
        root.mainloop()
