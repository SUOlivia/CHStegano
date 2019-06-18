# Import built-in libraries
import time
import os
import sys
from PIL import Image
import argparse

args = argparse.ArgumentParser(description="Script to extract and parse data from Clone Hero's screenshots")

args.add_argument('-i', '--input', action="store", dest="screenshot", type=str, help="Path to the screenshot")
args.add_argument('-o', '--output', action="store", dest="outf", type=str, help="Path to extract the extracted data")

if len(sys.argv) < 3:
    args.print_help()
    exit(0)
paths = args.parse_args()

StartTime = time.time()
EmbedScreenshot = Image.open(paths.screenshot, 'r').transpose(Image.FLIP_TOP_BOTTOM)
Pixels = list(EmbedScreenshot.getdata())

PixelData = [subpixel for pixel in Pixels for subpixel in pixel] # Get Separated RGBA values for each pixels
PixelData = [bin(Val) for Val in PixelData if Val != 0xFF] # Transform each subpixel values to binary while eliminating the alpha channel because no data is hidden in it
LSBs = [int(SB[-1], 2) for SB in PixelData] # Get least significant bits


EmbedData = [sum([byte[b] << b for b in range(0,8)])
            for byte in zip(*(iter(LSBs),) * 8)
            ] # https://stackoverflow.com/questions/20541023/in-python-how-to-convert-array-of-bits-to-array-of-bytes
EmbedData = bytearray(EmbedData)
os.write(os.open(paths.outf, os.O_CREAT | os.O_BINARY | os.O_WRONLY), EmbedData)

print(f"It took {time.time() - StartTime} seconds to extract the data from the screenshot")