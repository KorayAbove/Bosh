import os
import cv2

# Define input and output folders
input_folder = r"C:\Users\KorayKalkan\Documents\San-Michele-di-Ganzaria--PLANT-00572_1350_7088\OV-1"
output_folder = r"C:\Users\KorayKalkan\Documents\Project Bosh\OV-1\RGB"

# Loop through each file in input folder
for filename in os.listdir(input_folder):
    # Create video object
    video = cv2.VideoCapture(os.path.join(input_folder, filename))
    frame_counter = 0
    # Loop through each frame of video object
    while True:
        ret, frame = video.read()
        # Check if current frame number is divisible by 30
        if frame_counter % 30 == 0:
            # Save frame as .jpg file in output folder
            output_filename = filename[:-4] + "_frame%d.jpg" % frame_counter
            cv2.imwrite(os.path.join(output_folder, output_filename), frame)
        frame_counter += 1
        # Break loop if end of video is reached
        if not ret:
            break
    # Release video object
    video.release()
