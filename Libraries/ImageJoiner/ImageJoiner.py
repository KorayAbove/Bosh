import os
import argparse
from PIL import Image
import time

parser = argparse.ArgumentParser(description='Join images in the given folder')
parser.add_argument('folder', metavar='FOLDER', type=str, help='The path to the folder containing the images to join')
args = parser.parse_args()

folder_path = args.folder
print(f"Processing images in the folder: {folder_path}")  

while True:
    try:
        files = os.listdir(folder_path)
        break
    except FileNotFoundError:
        pass
    
print(f"Files in the folder: {files}") 


files.sort()

image_batches = []

for i in range(0, len(files), 10):
    image_batches.append(files[i:i+10])

for i, batch in enumerate(image_batches):
    images = []
    for image_name in batch:
        try:
            image_path = os.path.join(folder_path, image_name)
            images.append(Image.open(image_path))
        except FileNotFoundError:
            continue

    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)
    new_im = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    output_path = os.path.join(folder_path, f"merged_image_{i+1}.jpg")
    new_im.save(output_path)
    new_im.verify()

    for image_name in batch:
        try:
            image_path = os.path.join(folder_path, image_name)
            os.remove(image_path)
        except FileNotFoundError:
            continue
