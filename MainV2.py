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
import threading
import cv2
import tqdm
from concurrent.futures import ThreadPoolExecutor

class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)

    def flush(self):
        pass

    
class App(tk.Frame):
    
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry("765x365")
        self.pack()
        self.create_widgets()
        self.grid(padx=20, pady=20)
        self.master.resizable(False, False)
        self.process_queue = []
        self.folders_tree.tag_configure("finished", background="green")
        self.folders_tree.tag_configure("processing", background="orange")
        self.rgb_input = None
        self.process_queue = []
        self.completed_processes = [] 
        self.processed_folders = []
                
    def join_images(self):
            script_path = os.path.join(os.getcwd(), "Libraries", "ImageJoiner", "imagejoiner.py")
            preview_folder = os.path.join(self.output_folder, "preview")
            print(f"Joining images for {self.folder_name}")  
            self.process = subprocess.run(["python", script_path, preview_folder])
            print(f"Finished joining {self.folder_name}...")  

            self.process_queue.pop(0)

            if self.process_queue:
                processing_thread = threading.Thread(target=self.start_program)
                processing_thread.start()
                
    def joinrgb_images(self):
            script_path = os.path.join(os.getcwd(), "Libraries", "ImageJoiner", "imagejoiner.py")
            rgb_folder = os.path.join("ZoneRGB", self.folder_name, 'RGB')
            print(f"Joining images for {self.folder_name}")  
            self.process = subprocess.run(["python", script_path, rgb_folder])
            print(f"Finished joining {self.folder_name}...")  
            messagebox.showinfo("Processing Complete", f"Finished processing {self.folder_name}...") 
                
            for item in self.folders_tree.get_children():
                if self.folders_tree.item(item)["values"][0] == self.folder_name:
                    self.folders_tree.item(item, tags=("finished",))
                    break

            if self.process_queue:
                processing_thread = threading.Thread(target=self.start_program)
                processing_thread.start()
            
    def open_image_viewer(self):
        script_path = os.path.join(os.getcwd(), "Libraries", "ImageViewer", "imageviewer.py")
        preview_folder = os.path.join(self.folder_name, self.output_folder, "preview")
        rgb_folder = os.path.join("ZoneRGB", self.folder_name, 'RGB')
        
        def run_viewer():
            subprocess.Popen(f'python "{script_path}" "{preview_folder}" "{rgb_folder}"', shell=True)
            
        threading.Thread(target=run_viewer).start()
        
    def create_widgets(self):
        self.select_button = tk.Button(self, text="Select Site Folder", command=self.select_and_reset, width=50, height=5)
        self.select_button.grid(row=0, column=0)

        self.folders_label = tk.Label(self, text="Zone and OV Folders:")
        self.folders_label.grid(row=2, column=0)

        self.folders_tree = Treeview(self, columns=("Folder", "Process", "View"), show="headings", height=7)
        self.folders_tree.column("Folder", width=150, anchor='center')
        self.folders_tree.column("Process", width=100, anchor='center')
        self.folders_tree.column("View", width=100, anchor='center')
        self.folders_tree.heading("Folder", text="Folder")
        self.folders_tree.heading("Process", text="Process")
        self.folders_tree.heading("View", text="View")
        self.folders_tree.grid(row=3, column=0)
        self.folders_tree.bind("<Double-1>", self.on_folder_double_click)

        self.reset_button = tk.Button(self, text="Process All", command=self.temperror, width=50, height=3)
        self.reset_button.grid(row=4, column=0)
        
        self.console_label = tk.Label(self, text="Console Output:")
        self.console_label.grid(row=0, column=1)
        
        self.console_output = tk.Text(self, wrap='word', height=15, width=45)
        self.console_output.grid(row=1, column=1, rowspan=7)

        sys.stdout = TextRedirector(self.console_output) 

    def temperror(self):
        messagebox.showerror("Bug", "Doesn't work yet it is being a pain")
        
    def process_all(self):
        for item in self.folders_tree.get_children():
            folder_name = self.folders_tree.item(item)["values"][0]
            folder_path = os.path.join(self.selected_folder, folder_name)
            input_arg = os.path.join(folder_path, "*.seq")
            rgb_input = os.path.join(folder_path, "*.mov")

            if (input_arg, rgb_input) in self.completed_processes:
                print(f"{folder_name} has already been processed. Skipping...")
                continue

            if all(input_arg not in i and rgb_input not in i for i in self.process_queue):
                self.process_queue.append((input_arg, rgb_input))

        if not self.process_queue:
            messagebox.showerror("Error", "No folder selected for processing")
            return

        if len(self.process_queue) >= 1:
            processing_thread = threading.Thread(target=self.start_program)
            processing_thread.start()

    def select_folder(self):
        selected_folder = tk.filedialog.askdirectory()
        if not selected_folder:
            return
        self.selected_folder = selected_folder
        self.start_button.config(state='normal')
        
    def create_new_folder(self, folder_name, base_dir):
        new_folder = os.path.join(base_dir, folder_name)
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)
        return new_folder

    def start_program(self):
        if not self.process_queue:
            messagebox.showerror("Error", "No folder selected for processing")
            return

        self.input_arg = self.process_queue[0]
        self.folder_name = os.path.basename(os.path.dirname(self.input_arg))

        if self.folder_name in self.processed_folders:
            print(f"{self.folder_name} has already been processed. Skipping...")
            self.process_queue.pop(0) 
            self.start_program() 
            return

        self.processed_folders.append(self.folder_name) 

        self.rgb_input = os.path.normpath(os.path.join(self.selected_folder, self.folder_name))
        rgboutput_folder = os.path.join("ZoneRGB", self.folder_name, 'RGB')
        os.makedirs(rgboutput_folder, exist_ok=True)

        print("Processing thermal")
        base_output_folder = os.path.join(os.getcwd(), "zones")
        if self.folder_name.startswith("Zone-"):
            self.output_folder = self.create_new_folder(self.folder_name, base_output_folder)
        elif self.folder_name.startswith("OV-"):
            self.output_folder = self.create_new_folder(self.folder_name, base_output_folder)
        script_path = os.path.join(os.getcwd(), "split_seqs.py")
        self.process = subprocess.Popen(["python", script_path, "-o", self.output_folder, "-i", self.input_arg, "-v", "info", "--preview_format", "jpg", "--jpeg_quality", "100", "--merge_folders", "--split_filetypes", "--export_meta", "--export_tiff", "--no_export_raw", "--export_preview", "--no_skip_thermal", "--no_sync_rgb"])

        self.process.wait()

        self.join_images()

        frame_count = 0  
        rgb_files_found = False  

        if not os.path.exists(self.rgb_input):
            print("RGB input folder does not exist:", self.rgb_input)
            return

        for filename in os.listdir(self.rgb_input):
            if filename.endswith(".MOV"):
                rgb_files_found = True
                try:
                    video_path = os.path.join(self.rgb_input, filename)
                    if not os.path.exists(video_path):
                        print("RGB video file does not exist:", video_path)
                        continue

                    video = cv2.VideoCapture(video_path)
                    if not video.isOpened():
                        print("Failed to open RGB video file:", video_path)
                        continue

                    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) 
                    while True:
                        ret, frame = video.read()
                        if frame_count % 30 == 0:
                            output_filename = filename[:-4] + "_frame%d.jpg" % frame_count
                            cv2.imwrite(os.path.join(rgboutput_folder, output_filename), frame, [cv2.IMWRITE_JPEG_QUALITY, 15])
                            print(f"Processing {self.folder_name}... {frame_count}/{total_frames} frames processed")
                        frame_count += 1 
                        if not ret:
                            break
                        if frame_count >= total_frames:  
                            break
                    video.release()
                except cv2.error as e:
                    print("Error processing RGB video:", e)
                    continue

        self.joinrgb_images()

        if not rgb_files_found:
            print("No RGB files found in the folder:", self.rgb_input)

        print("Finished processing RGB")

        if self.process_queue:
            self.process_queue.pop(0)
            self.start_program()
            
    def process_next_in_queue(self):
        if self.process_queue:
            self.start_program()    
            
    def scan_folders(self):
        folders = []
        ov_folders = []
        zone_folders = []
        for folder_name in os.listdir(self.selected_folder):
            folder_path = os.path.join(self.selected_folder, folder_name)
            if os.path.isdir(folder_path):
                folders.append(folder_path)
                if folder_name.startswith("OV-"):
                    ov_folders.append(folder_name)
                elif folder_name.startswith("Zone-"):
                    zone_folders.append(folder_name)
        if ov_folders and zone_folders:
            self.update_folders_treeview(ov_folders + zone_folders)
        else:
            messagebox.showerror("Error", "Could not find required folders")

    def update_folders_treeview(self, folder_names):
        for i in self.folders_tree.get_children():
            self.folders_tree.delete(i)

        for folder_name in folder_names:
            self.folders_tree.insert("", tk.END, text=folder_name, values=(folder_name, "Process", "View"))
    
    def on_folder_double_click(self, event):
        item = self.folders_tree.identify("item", event.x, event.y)
        column = self.folders_tree.identify("column", event.x, event.y)
        folder_name = self.folders_tree.item(item, "values")[0]
        tags = self.folders_tree.item(item, "tags")
        
        if column == "#2":
            folder_path = os.path.join(self.selected_folder, folder_name)
            input_arg = os.path.join(folder_path, "*.seq")
            if input_arg not in self.process_queue:
                self.process_queue.append(input_arg)
                if len(self.process_queue) == 1:  
                    processing_thread = threading.Thread(target=self.start_program)
                    processing_thread.start()
        elif column == "#3":
           
            if "finished" in tags:
                self.open_image_viewer()
                print(f"Viewing {folder_name}")
            else:
                messagebox.showerror("Error", "Process has not finished yet")

            
    def update_folders_treeview(self, folder_names):
        for i in self.folders_tree.get_children():
            self.folders_tree.delete(i)

        for folder_name in folder_names:
            self.folders_tree.insert("", tk.END, text=folder_name, values=(folder_name, "Process", "View"))
                        
    def on_select_folder(self, event=None):
        folder_path = self.folder_var.get()
        if folder_path == "No matching folders found":
            return
        messagebox.showinfo("Selected Folder", folder_path)
    
    def select_folder(self):
        selected_folder = tk.filedialog.askdirectory()
        if not selected_folder:
            return
        self.selected_folder = selected_folder
        self.scan_folders()
        
    def stop_program(self):
        self.process.kill()
        messagebox.showinfo("Bosh", "Flirpy dead")
    
    def select_and_reset(self):
        self.select_folder()
        self.reset_program()    
        
    def reset_program(self):
        print("Resetting Program...")
        print("Bosh is ready")
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
                folder_path = os.path.join(os.getcwd(), "Zones")
        rgbfolder_path = os.path.join(os.getcwd(), "ZoneRGB")        
        if os.path.exists(rgbfolder_path):
            for filename in os.listdir(rgbfolder_path):
                file_path = os.path.join(rgbfolder_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")

root = tk.Tk()
photo = tk.PhotoImage(file="Libraries/logo/logo.png")
root.iconphoto(False, photo)
root.title("Bosh")
app = App(master=root)
app.mainloop()
