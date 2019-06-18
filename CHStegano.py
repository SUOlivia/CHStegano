# Import built-in libraries
import time
import os
import sys
from PIL import Image
import argparse

args = argparse.ArgumentParser(description="Script to extract and parse data from Clone Hero's screenshots")

args.add_argument('-a', '--analyse', action="store_true", dest="analyse", default=False, help="Analyse extracted data provided with -i")

args.add_argument('-i', '--input', action="store", dest="screenshot", type=str, help="Path to the screenshot")
args.add_argument('-o', '--output', action="store", dest="outf", type=str, help="Path to extract the extracted data")

# Init variables
SongChecksum = ""
SongName = ""
Artist = ""
Charter = ""
Score = 0
Stars = ""
Player = ""
Instrument = ""

i = 0

if len(sys.argv) < 3:
    args.print_help()
    exit(0)
paths = args.parse_args()

def IdentifyInstrument(instrumentID: int=0):
    if instrumentID == 0:
        return "Guitar"
    elif instrumentID == 1:
        return "Bass"
    elif instrumentID == 2:
        return "Rhythm"
    elif instrumentID == 3:
        return "GuitarCoop"
    elif instrumentID == 4:
        return "GHLGuitar"
    elif instrumentID == 5:
        return "GHLBass"
    elif instrumentID == 6:
        return "Drums"
    elif instrumentID == 7:
        return"Keys"
    elif instrumentID == 8:
        return "Band"

def DetectModifiers(modifier: int=1):
    Modifiers = []
    AppendMod = Modifiers.append 
    if modifier - 2048 >= 0:
        AppendMod("ModPrep")
        modifier -= 2048
    if modifier - 1024 >= 0:
        AppendMod("ModLite")
        modifier -= 1024
    if modifier - 512 >= 0:
        AppendMod("ModFull")
        modifier -= 512
    if modifier - 256 >= 0:
        AppendMod("LightsOut")
        modifier -= 256
    if modifier - 128 >= 0:
        AppendMod("HOPOsToTaps")
        modifier -= 128
    if modifier - 64 >= 0:
        AppendMod("Shuffle")
        modifier -= 64
    if modifier - 32 >= 0:
        AppendMod("MirrorMode")
        modifier -= 32
    if modifier - 16 >= 0:
        AppendMod("AllOpens")
        modifier -= 16
    if modifier - 8 >= 0:
        AppendMod("AllTaps")
        modifier -= 8
    if modifier - 4 >= 0:
        AppendMod("AllHOPOs")
        modifier -= 4
    if modifier - 2 >= 0:
        AppendMod("AllStrums")
    if modifier == 1:
        AppendMod("None")
    return Modifiers    

def AnalyseData(Data: bytes):
    pos = 0x39
    SongChecksum = str(Data[pos:pos+0x20], 'utf-8')
    pos += 0x20
    CurLen = Data[pos]
    pos += 0x01
    SongName = str(Data[pos:pos+CurLen], 'utf-8')
    pos += CurLen
    CurLen = Data[pos]
    pos += 0x01
    Artist = str(Data[pos:pos+CurLen], 'utf-8')
    pos += CurLen
    CurLen = Data[pos]
    pos += 0x01
    Charter = str(Data[pos:pos+CurLen], 'utf-8')
    pos += CurLen
    pos += 0x0C
    Score = int.from_bytes(Data[pos:pos+0x04], 'little')
    pos += 0x04
    i = 0
    Stars = ""
    if Data[pos] == 0:
        Stars = "None"
    else:
        while i < Data[pos]:
            Stars += '⭐ ' 
            i += 1 
    pos += 0x08
    Instrument = IdentifyInstrument(Data[pos])
    pos += 0x08
    CurLen = Data[pos]
    pos += 0x01
    Player = str(Data[pos:pos+CurLen], 'utf-8')
    pos += CurLen + 0x01
    Modifiers = DetectModifiers(int.from_bytes(Data[pos:pos+0x02], 'little'))
    
    print(f"Checksum:   {SongChecksum}")
    print(f"SongName:   {SongName}")
    print(f"Artist:     {Artist}")
    print(f"Charter:    {Charter}")
    print(f"Score:      {Score}")
    print(f"Stars:     {Stars}")
    print(f"Instrument: {Instrument}")
    print(f"Player:     {Player}")
    i = 1
    for Modifier in Modifiers:
        print(f"Modifier {i}: {Modifier}")
        i += 1





if paths.analyse == False:
    StartTime = time.time()
    EmbedScreenshot = Image.open(paths.screenshot, 'r').transpose(Image.FLIP_TOP_BOTTOM)
    Pixels = list(EmbedScreenshot.getdata())

    PixelData = [subpixel for pixel in Pixels for subpixel in pixel] # Get Separated RGBA values for each pixels
    PixelData = [bin(Val) for Val in PixelData if Val != 0xFF] # Transform each subpixel values to binary while eliminating the alpha channel because no data is hidden in it
    LSBs = [int(SB[-1], 2) for SB in PixelData][0:0x1000] # Get least significant bits


    EmbedData = [sum([byte[b] << b for b in range(0,8)])
                for byte in zip(*(iter(LSBs),) * 8)
                ] # https://stackoverflow.com/questions/20541023/in-python-how-to-convert-array-of-bits-to-array-of-bytes
    EmbedData = bytes(EmbedData)
    os.write(os.open(paths.outf, os.O_CREAT | os.O_BINARY | os.O_WRONLY), EmbedData)

    print(f"It took {time.time() - StartTime} seconds to extract the data from the screenshot")
else:
    EmbedData = os.read(os.open(paths.screenshot, os.O_RDONLY | os.O_BINARY), os.path.getsize(paths.screenshot))
AnalyseData(EmbedData)