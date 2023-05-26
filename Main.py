import os
import tkinter as tk
import subprocess
import time
import sys
import shutil
from PIL import Image, ImageTk
from pynput import keyboard
from tkinter import messagebox
from tkinter import filedialog
from tkinter import *
from tkinter.ttk import *

class App(tk.Frame):
    
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry("400x300")
        self.pack()
        self.create_widgets()
        self.grid(padx=20, pady=20)
        self.master.resizable(False, False)
    
    def join_images(self):
        script_path = os.path.join(os.getcwd(), "Libraries", "ImageJoiner", "imagejoiner.py")
        self.process = subprocess.Popen(["python", script_path])
        self.status_label.config(text="Status: Joining Images", bg='yellow')
        self.process.wait()
        self.imageviewer_button.config(state='normal')
        self.status_label.config(text="Status: Finished Joining Images", bg='green')

    def open_image_viewer(self):
        script_path = os.path.join(os.getcwd(), "Libraries", "ImageViewer", "imageviewer.py")
        self.process = subprocess.Popen(["python", script_path])
        self.status_label.config(text="Status: Running Image Viewer", bg='Green')
    
    def create_widgets(self):
        self.select_button = tk.Button(self, text="Select Zone", command=self.select_folder, width=50, height=5)
        self.select_button.pack()
        self.start_button = tk.Button(self, text="Process Zone", command=self.start_program, width=50, height=1, state='disabled')
        self.start_button.pack()
        self.status_label = tk.Label(self, text="Status: Idle", bg='white', width=50, height=2)
        self.status_label.pack()
        self.imageviewer_button = tk.Button(self, text="Image Viewer", command=self.open_image_viewer, width=50, height=5)
        self.imageviewer_button.pack()
        self.reset_button = tk.Button(self, text="Reset", command=self.reset_program, width=50, height=1)
        self.reset_button.pack()

    def select_folder(self):
        selected_folder = tk.filedialog.askdirectory()
        if not selected_folder:
            return
        self.selected_folder = selected_folder
        self.start_button.config(state='normal')

    def start_program(self):
        input_arg = os.path.join(self.selected_folder, "*.seq")
        self.output_folder = os.path.join(os.getcwd(), "zones")
        script_path = os.path.join(os.getcwd(), "split_seqs.py")
        self.process = subprocess.Popen(["python", script_path, "-o", self.output_folder, "-i", input_arg, "-v", "info", "--preview_format", "jpg", "--jpeg_quality", "100", "--merge_folders", "--split_filetypes", "--export_meta", "--export_tiff", "--no_export_raw", "--export_preview", "--no_skip_thermal", "--no_sync_rgb"])
        self.start_button.config(state='disabled')
        self.status_label.config(text="Status: Processing Images", bg='yellow')
        self.master.after(1000, self.check_process)
        
    def check_process(self):
        if self.process.poll() is not None:
            self.status_label.config(text="Status: Finished Processing Images", bg='Yellow')
            self.start_button.config(state='normal')
            self.status_label.config(text="Status: Finished Processing Images", bg='Yellow')
            self.status_label.config(text="Status: Merging Images", bg='Yellow')
            self.join_images()
        else:
            self.master.after(1000, self.check_process)
        
    def stop_program(self):
        self.process.kill()
        messagebox.showinfo("Bosh", "Flirpy dead")
        
    def reset_program(self):
        folder_path = os.path.join(os.getcwd(), "Zones")
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
            self.status_label.config(text="Status: Reset Complete", bg='green')
        else:
            self.status_label.config(text="Status: Zones folder not found", bg='red')
    

root = tk.Tk()
photo = tk.PhotoImage(file="Libraries/logo/logo.png")
root.iconphoto(False, photo)
root.title("Bosh")
app = App(master=root)
app.mainloop()
