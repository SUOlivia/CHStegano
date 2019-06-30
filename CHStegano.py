# Import built-in libraries
import time
import os
import sys
from PIL import Image
import argparse
import itertools

args = argparse.ArgumentParser(description="Script to extract and parse data from Clone Hero's screenshots")

args.add_argument('-a', '--analyse', action="store_true", dest="analyse", default=False, help="Analyse extracted data provided with -i")

args.add_argument('-i', '--input', action="store", dest="screenshot", type=str, help="Path to the screenshot")
args.add_argument('-o', '--output', action="store", dest="outf", type=str, help="Path to extract the extracted data")

# Define fancy class cuz i wanna do print(CHScore.Player)
class CHScore:
    SongChecksum = ""
    SongName = ""
    Artist = ""
    Charter = ""
    Score = 0
    Stars = ""
    Instrument = ""
    Player = ""
    Modifiers = []
    NotesHit = 0
    NotesTotal = 0
    Accuracy = 0.0
    Streak = 0
    SPPhases_Hit = 0
    SPPhases_Total = 0
    FC = False

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
        return "Keys"
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
    CHScore.SongChecksum = str(Data[pos:pos+0x20], 'utf-8')
    pos += 0x20
    CurLen = Data[pos]
    pos += 0x01
    CHScore.SongName = str(Data[pos:pos+CurLen], 'utf-8')
    pos += CurLen
    CurLen = Data[pos]
    pos += 0x01
    CHScore.Artist = str(Data[pos:pos+CurLen], 'utf-8')
    pos += CurLen
    CurLen = Data[pos]
    pos += 0x01
    CHScore.Charter = str(Data[pos:pos+CurLen], 'utf-8')
    pos += CurLen
    pos += 0x0C
    CHScore.Score = int.from_bytes(Data[pos:pos+0x04], 'little')
    pos += 0x04
    i = 0
    if Data[pos] == 0:
        CHScore.Stars = "None"
    else:
        while i < Data[pos]:
            CHScore.Stars += '⭐' 
            i += 1 
    pos += 0x08
    CHScore.Instrument = IdentifyInstrument(Data[pos])
    pos += 0x08
    CurLen = Data[pos]
    pos += 0x01
    CHScore.Player = str(Data[pos:pos+CurLen], 'utf-8')
    pos += CurLen + 0x01
    CHScore.Modifiers = DetectModifiers(int.from_bytes(Data[pos:pos+0x01], 'little'))
    pos += 0x1F
    CHScore.NotesHit = int.from_bytes(Data[pos:pos+0x04], 'little')
    pos += 0x04
    CHScore.NotesTotal = int.from_bytes(Data[pos:pos+0x04], 'little')
    CHScore.Accuracy = (CHScore.NotesHit / CHScore.NotesTotal) * 100 if CHScore.NotesTotal != 0 else 0.0
    pos += 4
    CHScore.Streak = int.from_bytes(Data[pos:pos+0x04], 'little')
    pos += 4
    CHScore.SPPhases_Hit = int.from_bytes(Data[pos:pos+0x04], 'little')
    pos += 4
    CHScore.SPPhases_Total = int.from_bytes(Data[pos:pos+0x04], 'little')
    pos += 4
    CHScore.FC = bool(Data[pos])
    
    print(f"Checksum:       {CHScore.SongChecksum}")
    print(f"SongName:       {CHScore.SongName}")
    print(f"Artist:         {CHScore.Artist}")
    print(f"Charter:        {CHScore.Charter}")
    print(f"Score:          {CHScore.Score}")
    print(f"Accuracy:       {CHScore.NotesHit}/{CHScore.NotesTotal} ({CHScore.Accuracy}%)")
    print(f"Longest streak: {CHScore.Streak}")
    print(f"SP Phases:      {CHScore.SPPhases_Hit}/{CHScore.SPPhases_Total}")
    print(f"Stars:          {CHScore.Stars}")
    print(f"FC:             {CHScore.FC}")
    print(f"Instrument:     {CHScore.Instrument}")
    print(f"Player:         {CHScore.Player}")
    i = 1
    for Modifier in CHScore.Modifiers:
        print(f"Modifier {i}:     {Modifier}")
        i += 1

if paths.analyse == False:
    StartTime = time.time()
    EmbedScreenshot = Image.open(paths.screenshot, 'r').transpose(Image.FLIP_TOP_BOTTOM)
    Pixels = itertools.islice(EmbedScreenshot.getdata(), 0x1000)

    PixelData = [subpixel for pixel in Pixels for subpixel in pixel if subpixel != 0xFF] # Get Separated RGBA values for each pixels
    LSBs = [SB & 1 for SB in PixelData] # Get least significant bits


    EmbedData = [sum([byte[b] << b for b in range(0,8)])
                for byte in zip(*(iter(LSBs),) * 8)
                ] # https://stackoverflow.com/questions/20541023/in-python-how-to-convert-array-of-bits-to-array-of-bytes
    EmbedData = bytes(EmbedData)
    if paths.outf != None and os.name == "nt":
        os.write(os.open(paths.outf, os.O_CREAT | os.O_BINARY | os.O_WRONLY), EmbedData)
    elif paths.outf != None and os.name == "posix":
        os.write(os.open(paths.outf, os.O_CREAT | os.O_WRONLY), EmbedData)

    print(f"It took {(time.time() - StartTime) * 1000} ms to extract the data from the screenshot")
else:
    EmbedData = os.read(os.open(paths.screenshot, os.O_RDONLY | os.O_BINARY), os.path.getsize(paths.screenshot))

AnalyseData(EmbedData)