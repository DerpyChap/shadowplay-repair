import os
import re
import subprocess
from argparse import ArgumentParser
from PIL import Image

# Yoinked from https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

parser = ArgumentParser(description='A command-line tool aimed to create usable footage out of a borked NVIDIA Share recording')

parser.add_argument('input', type=str, help='The input video file.')

args = parser.parse_args()

os.mkdir('frames')

# Extract frames
# TODO: make framerate user adjustable
# TODO: Stream the video file directly instead of just exporting frames for PIL
print('Extracting frames')
subprocess.call(['ffmpeg', '-i', args.input, '-filter:v', 'fps=fps=60', 'frames/frame%d.jpg'])

print('Extracting audio')
subprocess.call(['ffmpeg', '-i', args.input, '-vn', '-c:a', 'copy', 'audio.aac'])

last_frame = None

# Iterate over frames
files = sorted([i for i in os.listdir("frames/") if i.endswith("jpg")], key=natural_keys)

print('Scanning frames')
for file in files:
    location = f'frames/{file}'
    print(location)
    frame = Image.open(location)
    pixels = frame.getdata()
    is_black = True
    for pixel in pixels:
        if pixel > (10, 10, 10):
            is_black = False
            break
    if is_black:
        print('Frame is blank!')
        if last_frame:
            last_frame.save(location)
    else:
        last_frame = frame

print('Exporting video')
# Export new video file
# TODO: Let's not hardcode ffmpeg arguments
subprocess.call(['ffmpeg', '-framerate', '60', '-i', 'frames/frame%d.jpg', '-i',
                'audio.aac', '-c:v', 'hevc_nvenc', '-preset', 'slow', '-b:v', '50M', '-c:a', 'copy', 'output.mp4'])
