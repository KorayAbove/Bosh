import os
import tkinter as tk
from PIL import Image, ImageTk
import argparse

class ImageViewer:
    
    def __init__(self, master, image_dir, rgb_dir):
        self.master = master
        self.master.geometry("1920x600") 

        self.image_dir = image_dir
        self.rgb_dir = rgb_dir 

        self.image_canvas = tk.Canvas(self.master)
        self.image_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.rgb_canvas = tk.Canvas(self.master) 
        self.rgb_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True) 

        self.prev_button = tk.Button(self.master, text='<< Prev', command=self.prev_image)
        self.prev_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.next_button = tk.Button(self.master, text='Next >>', command=self.next_image)
        self.next_button.pack(side=tk.RIGHT, padx=20, pady=20)

        self.current_image_index = 0

        self.master.bind('<Left>', lambda event: self.prev_image())
        self.master.bind('<Right>', lambda event: self.next_image())

        # Load images and schedule the first call to show_image
        self.load_images()
        self.master.after(100, self.show_image)
        
    def load_images(self):
        self.image_files = sorted([f for f in os.listdir(self.image_dir) if f.startswith('merged_image_') and f.endswith('.jpg')], key=lambda x: os.path.getctime(os.path.join(self.image_dir, x)))
        self.rgb_files = sorted([f for f in os.listdir(self.rgb_dir) if f.startswith('merged_image_') and f.endswith('.jpg')], key=lambda x: os.path.getctime(os.path.join(self.rgb_dir, x)))

    def show_image(self):
        image_path = os.path.join(self.image_dir, self.image_files[self.current_image_index])
        image = Image.open(image_path)

        rgb_path = os.path.join(self.rgb_dir, self.rgb_files[self.current_image_index])  
        rgb_image = Image.open(rgb_path)  

        window_width, window_height = self.master.winfo_width(), self.master.winfo_height()
        window_height = window_height // 2  

        image_ratio = image.width / image.height

        new_width = min(window_width, image.width)
        new_height = min(new_width / image_ratio, window_height)

        if new_height == window_height:
            new_width = new_height * image_ratio

        try:
            image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
            rgb_image = rgb_image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
        except ValueError:
            pass  

        photo = ImageTk.PhotoImage(image)
        rgb_photo = ImageTk.PhotoImage(rgb_image)  

        self.image_canvas.delete('all')
        self.image_canvas.create_image((window_width-new_width)//2, 0, anchor=tk.NW, image=photo)
        self.image_canvas.photo = photo

        self.rgb_canvas.delete('all')  
        self.rgb_canvas.create_image((window_width-new_width)//2, 0, anchor=tk.NW, image=rgb_photo) 
        self.rgb_canvas.photo = rgb_photo 

        set_number = self.current_image_index + 1

    def next_image(self):
        self.load_images()
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
        self.show_image()

    def prev_image(self):
        self.load_images()
        if self.current_image_index > 0:
            self.current_image_index -= 1
        self.show_image()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Join images in the given folder')
    parser.add_argument('folder', metavar='FOLDER', type=str, help='The path to the folder containing the images to join')
    parser.add_argument('rgb_folder', metavar='RGBFOLDER', type=str, help='The path to the RGB folder')
    args = parser.parse_args()

    root = tk.Tk()
    root.title("Bosh")
    image_viewer = ImageViewer(root, args.folder, args.rgb_folder)
    root.mainloop()
