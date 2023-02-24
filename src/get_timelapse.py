import os
import shutil
from PIL import Image
import pickle
import subprocess


def create_image(hex_array, index, output_dir):
    height = len(hex_array)
    width = len(hex_array[0])
    img = Image.new('RGB', (width, height), color='white')
    pixels = img.load()

    for y in range(height):
        for x in range(width):
            hex_color = hex_array[y][x]
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:], 16)
            pixels[x, y] = (r, g, b)

    output_p = os.path.join(output_dir, f'output_{index}.png')
    img.save(output_p)


# Load the pickled file
with open('history/history.pkl', 'rb') as f:
    hex_arrays = []
    while True:
        try:
            o = pickle.load(f)
        except EOFError:
            break
        hex_arrays.append(o)

# Create the output directory if it doesn't exist
output_dir = 'frames'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
else:
    shutil.rmtree(output_dir)
    os.makedirs(output_dir)

# Iterate through each 2D array and create an image
for i, hex_array in enumerate(hex_arrays):
    create_image(hex_array, i, output_dir)

# Generate the video using FFmpeg
ffmpeg_path = 'ffmpeg'  # change to your own path if necessary
input_path = os.path.join(output_dir, 'output_%d.png')
output_path = 'output.mp4'
subprocess.run(
    [ffmpeg_path, '-y', '-framerate', '30', '-i', input_path, '-vf', f'scale=-1:2160:flags=neighbor', '-c:v', 'libx264',
     '-pix_fmt', 'yuv420p', output_path], check=True)
