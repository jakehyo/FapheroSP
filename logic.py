import datetime
import os
import random
import time
from configparser import ConfigParser
from os import listdir, path

import cv2
import requests

import configwrite

# Checks for all your files.
time.sleep(0.75)
print("Welcome to Fap Land")
print("Checking Files...")
print("")
time.sleep(0.5)

# Configures Settings File
if path.exists("Game_Settings.txt"):
    print("Config File Loaded!")
else:
    print("Config File was not found. Generating New Config...")
    configwrite.loadconfig()
    time.sleep(0.5)
    print("")

fap_config = ConfigParser()
_ = fap_config.read("Game_Settings.txt")
file_config = fap_config["Custom_File_Locations"]
inv_config = fap_config["Invasions"]
mod_config = fap_config["Modifiers"]
gen_config = fap_config["General"]
perk_config = fap_config["Perks"]
curse_config = fap_config["Curses"]
random_config = fap_config["Randomization"]
time.sleep(0.5)

# Configures Save Data
if gen_config["Start from Last Checkpoint?"] == "ON":
    if path.exists("SaveData.txt"):
        print("Save File Loaded!")
    else:
        print("No Save Data was not found. Generating Save File...")
        configwrite.savedata(
            1,
            inv_config["Invasion Chance Percentage"],
            mod_config["Modifier Chance Percentage"],
            gen_config["Default Die Min Size"],
            gen_config["Default Die Max Size"],
            0,
            "OFF",
        )
        time.sleep(0.5)
        print("")
    save_config = ConfigParser()
    _ = save_config.read("SaveData.txt")
    # have savedata saved like other _setting methods
    savecheckpoint = save_config["Save"]["Last Checkpoint"]

# Sets any custom paths for the files
mpv_path = file_config["mpv"]
fl_path = file_config["Fapland_Videos"]
inv_path = file_config["Invastions"]
mod_path = file_config["Modifiers"]
int_path = file_config["Intervals"]

# Checks for all necessary files
if path.exists("mpv.exe"):
    mpv_path = ""
    print("MPV Loaded!")
elif path.exists(mpv_path):
    print("MPV Loaded!")
else:
    print("")
    print("MPV.exe was not found.")
    print("")
time.sleep(0.5)

if path.exists("Fapland Videos/2.mp4"):
    fl_path = "Fapland Videos/"
    print("FapLand Videos Loaded!")
elif path.exists(fl_path):
    print("FapLand Videos Loaded")
else:
    print("")
    print("-Fapland Videos were not found.-")
    print("")
time.sleep(0.5)

if path.exists("invasions") and inv_config["Invasion Rounds?"] == "ON":
    inv_path = "invasions/"
    invexist = True
elif path.exists(inv_path) and inv_config["Invasion Rounds?"] == "ON":
    invexist = True
else:
    print("")
    print("-Invasions Folder was not found.-")
    print("")
    invexist = False
if invexist:
    print("Invasions Folder found!")
    if listdir(inv_path):
        print("Invasion Videos Loaded!")
        invexist = True
    else:
        print("")
        print("-No Invasion Videos were found.-")
        print("")
        invexist = False
time.sleep(0.5)

if path.exists("modifiers") and mod_config["Modifiers?"] == "ON":
    mod_path = "modifiers/"
    print("Modifiers Folder Found!")
    modexist = True
elif path.exists(mod_path):
    print("Modifiers Folder Loaded!")
    modexist = True
else:
    print("")
    print("-Modifiers Folder was not found.-")
    print("")
    modexist = False
time.sleep(0.5)

if path.exists("intervals") and gen_config["Image Breaks between Rounds?"] == "ON":
    int_path = "intervals/"
    intexist = True
elif path.exists(int_path) and gen_config["Image Breaks between Rounds?"] == "ON":
    intexist = True
else:
    print("")
    print("-Invasions Folder was not found.-")
    print("")
    intexist = False
if intexist:
    print("Interval Images Folder Found!")
    if listdir(int_path):
        print("Interval Images Loaded!")
        intexist = True
    else:
        print("")
        print("-No interval images were found.-")
        print("")
        intexist = False

time.sleep(0.5)

time.sleep(0.5)
print("")

euri = "https://localhost:5000/Edi/"


def playEDI(file: str, seek: int) -> None:
    _ = requests.post("http://localhost:5000/Edi/Play/" + file + "?seek=" + str(seek))


def stopEDI() -> None:
    _ = requests.post("http://localhost:5000/Edi/Stop")


def pauseEDI() -> None:
    _ = requests.post("http://localhost:5000/Edi/Pause")


def resumeEDI() -> None:
    _ = requests.post("http://localhost:5000/Edi/Resume")


def getVideoLength(dirpath: str, filename: str) -> float:
    len = 0
    complete_path = os.getcwd() + "\\" + dirpath.replace("/", "\\") + filename
    if ".mp4" not in filename:
        complete_path += ".mp4"

    if os.path.exists(complete_path):
        cap = cv2.VideoCapture(complete_path)
        if not cap.isOpened():
            raise ValueError("Failed to open video")
        len = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
        cap.release()
    else:
        print(f"File {complete_path} not found")
    return len


# Plays requested videos and processes invasions/modifiers
def video(currentval: int, invasionchance: int, modifierchance: int):
    # Converts playroom number [1-100] into a string
    file = str(currentval)
    # Initializes invadedCount to 0.
    invaded = 0
    # Appends "- Start" to the file name if it's the first video and the file name is not "1.mp4"
    if currentval == 1 and not path.exists("1.mp4"):
        file = "1 - Start"
    # Appends "- Checkpoint" to the file name for all checkpoint videos and "- End" for the last video.
    elif currentval % 25 == 0 and not path.exists("25.mp4"):
        if currentval != 100:
            file = str(currentval) + " - Checkpoint"
        else:
            file = str(currentval) + " - End"
    # Initializes savepoint as 0
    savepoint = 0
    lastinv = ""

    # Initializes power to be 100. Invasion chance will change the power level based on how high it is.
    power = 100

    if invasionchance > 0:
        power = random.randint(1, (100 // invasionchance) * 10)

    moddy = 100
    if modifierchance > 0:
        moddy = random.randint(1, (100 // modifierchance))

    while (
        power <= 10
        and savepoint + 5 <= 80
        and currentval % 25 != 0
        and currentval != 1
        and inv_config["Invasion Rounds?"] == "ON"
        and inv_config["Invasion Rounds During Videos?"] == "ON"
        and invexist
    ):
        surprise = random.randint(savepoint + 5, 80)

        roundLength = getVideoLength(fl_path, file)  # Get the length of the video file
        start = int((savepoint / 100.0) * roundLength)
        playEDI(file, start)  # Starts EDI play script seeking to savepoint percentage.
        _ = os.system(
            mpv_path  # Directory path for mpv.exe
            + "mpv.exe "  # Command to execute mpv.exe
            + '"'  # Start of command string
            + fl_path  # Path to file to play
            + file  # File name
            + '.mp4"'  # File extension and closing quote
            + " -msg-level=all=no -fullscreen -start="  # Turns all verbose messages off, enter fullscreen, and beginning of -start option
            + str(start)
            + " -end="
            + str(surprise)
            + "%"
            + " -ontop"
        )
        stopEDI()
        savepoint = surprise
        inv_unpicked = True

        invader = ""
        while inv_unpicked:
            invader = random.choice(listdir(inv_path))
            if invader is not lastinv:
                invaded += 1
                print("Invasion!\n")

                roundLength = getVideoLength(
                    inv_path, invader
                )  # Get the length of the invasion round.

                #   Check if invasion round is longer than 2 minutes.
                #   If so, pick a random start time between 40 and 100 seconds.
                #   Else, the round is originally less than 2 minutes long, so we play the whole round.
                begin = 0
                invasionLength = 120
                if roundLength > 120.0:
                    invasionLength = random.randint(40, 100)
                    begin = random.randint(0, int(roundLength - invasionLength))
                    print("Invasion Length :", invasionLength)
                else:
                    print("Invasion Length:", roundLength)
                print("Invasion Start:", begin)
                playEDI(
                    invader, begin
                )  # Starts EDI play script seeking to invasion start time.
                _ = os.system(
                    mpv_path
                    + "mpv.exe "
                    + '"'
                    + inv_path
                    + invader
                    + '" --start='
                    + str(begin)
                    + " --end="
                    + str(begin + invasionLength)
                    + " -ontop -msg-level=all=no --fullscreen"
                )
                stopEDI()
                inv_unpicked = False
        lastinv = invader
        if inv_config["Multiple Invasions During Videos"] == "ON":
            power += 7 - currentval // 25
        else:
            power += 10
        print("Resuming...")
        print("")
    if (
        moddy == 1
        and currentval % 25 != 0
        and currentval != 1
        and mod_config["Modifiers?"] == "ON"
        and modexist
    ):
        unpicked = True
        while unpicked:
            modifier = random.randint(1, 3)
            if modifier == 1 and mod_config["Speed Up Modifier"] == "ON":
                unpicked = False
                print("Modifier: Speed Up")
                print("")
                #   No PlayEDI() for Speed Up because EDI doesn't support speed up?
                _ = os.system(
                    mpv_path
                    + "mpv.exe "
                    + '"'
                    + mod_path
                    + "Speed Up"
                    + '.mp4"'
                    + " -msg-level=all=no --fullscreen -ontop"
                )
                _ = os.system(
                    mpv_path
                    + "mpv.exe "
                    + '"'
                    + fl_path
                    + file
                    + '.mp4"'
                    + " -msg-level=all=no --fullscreen -start="
                    + str(savepoint)
                    + "%"
                    + " -speed=1.20"
                    + ' -ontop -sub-file="modifiers/Speed_Up.srt" -sub-scale=0.7 -sub-pos=0 -sub-color=1.0/1.0/1.0/0.55 -sub-border-size=0 -sub-bold=yes -sub-font="Tahoma" -sub-shadow-offset=-3 -sub-shadow-color=0.0/0.0/0.0/0.2'
                )
            elif modifier == 2 and mod_config["Squeeze Shaft Modifier"] == "ON":
                unpicked = False
                print("Modifier: Squeeze Shaft")
                print("")
                _ = os.system(
                    mpv_path
                    + "mpv.exe "
                    + '"'
                    + mod_path
                    + "SQUEEZE SHAFT"
                    + '.mp4"'
                    + " -msg-level=all=no --fullscreen -ontop"
                )

                roundLength = getVideoLength(
                    fl_path, file
                )  # Get the length of the video file
                start = int((savepoint / 100.0) * roundLength)
                playEDI(file, start)
                _ = os.system(
                    mpv_path
                    + "mpv.exe "
                    + '"'
                    + fl_path
                    + file
                    + '.mp4"'
                    + " -msg-level=all=no --fullscreen -start="
                    + str(start)
                    + ' -ontop -sub-file="modifiers/SQUEEZE_SHAFT.srt" -sub-scale=0.7 -sub-pos=1 -sub-color=1.0/0.2/0.2/0.55 -sub-border-size=0 -sub-bold=yes -sub-font="Impact" -sub-shadow-offset=-3 -sub-shadow-color=0.0/0.0/0.0/0.3'
                )
                stopEDI()
            elif modifier == 3 and mod_config["Hold Breath Modifier"] == "ON":
                unpicked = False
                print("Modifier: Hold Breath")
                print("")
                _ = os.system(
                    mpv_path
                    + "mpv.exe "
                    + '"'
                    + mod_path
                    + "Hold Breath"
                    + '.mp4"'
                    + " -msg-level=all=no --fullscreen -ontop"
                )
                roundLength = getVideoLength(
                    fl_path, file
                )  # Get the length of the video file
                start = int((savepoint / 100.0) * roundLength)
                playEDI(file, start)
                _ = os.system(
                    mpv_path
                    + "mpv.exe "
                    + '"'
                    + fl_path
                    + file
                    + '.mp4"'
                    + " -msg-level=all=no --fullscreen -start="
                    + str(start)
                    + ' -ontop -sub-file="modifiers/Hold_Breath.srt" -sub-scale=1.0 -sub-pos=1 -sub-color=1.0/1.0/1.0/0.55 -sub-border-size=2 -sub-border-color=0.0/0.0/0.0/0.55 -sub-bold=yes -sub-font="Tahoma" -sub-shadow-offset=-3 -sub-shadow-color=0.0/0.0/0.0/0.3'
                )
                stopEDI()
            elif (
                mod_config["Hold Breath Modifier"] == "OFF"
                and mod_config["Speed Up Modifier"] == "OFF"
                and mod_config["Squeeze Shaft Modifier"] == "OFF"
            ):
                print("No Modifiers Active...")
                print("")
                unpicked = False

    else:
        roundLength = getVideoLength(fl_path, file)  # Get the length of the video file
        start = int((savepoint / 100.0) * roundLength)
        playEDI(file, start)
        _ = os.system(
            mpv_path
            + "mpv.exe "
            + '"'
            + fl_path
            + file
            + '.mp4"'
            + " -msg-level=all=no --fullscreen -start="
            + str(start)
            + " -ontop"
        )
        stopEDI()

    return invaded


def image(invasionchance: int):
    invaded = 0
    if intexist and gen_config["Image Breaks between Rounds?"] == "ON":
        imageFile = os.listdir(int_path)
        imagefound = False
        while not imagefound:
            random_file = random.choice(imageFile)
            name, ext = os.path.splitext(random_file)
            if (
                ext == ".png"
                or ext == ".jpg"
                or ext == ".jfif"
                or ext == ".jpeg"
                or ext == ".gif"
                or ext == ".mp4"
                or ext == ".webm"
            ):
                imagefound = True
        fullImagePath = int_path + random_file
        breaktime = int(gen_config["Breaktime"])
        if invasionchance > 0:
            power = random.randint(1, (100 // invasionchance) * 10)
        else:
            power = 100
        if (
            inv_config["Invasion Rounds During Break?"] == "ON"
            and power <= 10
            and invexist
        ):
            invader = random.choice(listdir(inv_path))
            divsec = random.randint(1, breaktime)

            if ext == ".gif" or ext == ".mp4" or ext == ".webm":
                _ = os.system(
                    mpv_path
                    + "mpv.exe "
                    + '"'
                    + fullImagePath
                    + '"'
                    + " -ontop -msg-level=all=no --fullscreen -loop-file="
                    + str(divsec)
                    + ' -sub-file="modifiers/interval.srt" -sub-scale=0.7 -sub-pos=0 -sub-color=1.0/1.0/1.0/0.8 -sub-border-size=0 -sub-bold=yes -sub-font="Tahoma" -sub-shadow-offset=-3 -sub-shadow-color=0.0/0.0/0.0/0.2'
                )
            else:
                _ = os.system(
                    mpv_path
                    + "mpv.exe - --fullscreen --image-display-duration="
                    + str(divsec)
                    + ' "'
                    + fullImagePath
                    + '"'
                    + ' -ontop -sub-file="modifiers/interval.srt" -sub-scale=0.7 -sub-pos=0 -sub-color=1.0/1.0/1.0/0.8 -sub-border-size=0 -sub-bold=yes -sub-font="Tahoma" -sub-shadow-offset=-3 -sub-shadow-color=0.0/0.0/0.0/0.2'
                )

            roundLength = getVideoLength(
                inv_path, invader
            )  # Get the length of the invasion round.

            #   Check if invasion round is longer than 2 minutes.
            #   If so, pick a random start time between 40 and 100 seconds.
            #   Else, the round is originally less than 2 minutes long, so we play the whole round.
            begin = 0
            invasionLength = 120
            if roundLength > 120.0:
                invasionLength = random.randint(30, 50)
                begin = random.randint(0, int(roundLength) - invasionLength)
                print("Invasion length:", invasionLength)
            else:
                print("Invasion length:", roundLength)
            print("Invasion Start:", begin)
            playEDI(invader, begin)
            _ = os.system(
                mpv_path
                + "mpv.exe "
                + '"'
                + inv_path
                + invader
                + '" --start='
                + str(begin)
                + " --end="
                + str(begin + invasionLength)
                + " -msg-level=all=no --fullscreen"
                + " -ontop"
            )
            stopEDI()
            invaded += 1
            breaktime = breaktime - divsec
        if ext == ".gif" or ext == ".mp4" or ext == ".webm":
            _ = os.system(
                mpv_path
                + "mpv.exe "
                + '"'
                + fullImagePath
                + '"'
                + " -msg-level=all=no --fullscreen -loop-file="
                + str(breaktime)
                + ' -ontop -sub-file="modifiers/interval.srt" -sub-scale=0.7 -sub-pos=0 -sub-color=1.0/1.0/1.0/0.8 -sub-border-size=0 -sub-bold=yes -sub-font="Tahoma" -sub-shadow-offset=-3 -sub-shadow-color=0.0/0.0/0.0/0.2'
            )
        else:
            _ = os.system(
                mpv_path
                + "mpv.exe - --fullscreen --image-display-duration="
                + str(breaktime)
                + ' "'
                + fullImagePath
                + '"'
                + ' -ontop -sub-file="modifiers/interval.srt" -sub-scale=0.7 -sub-pos=0 -sub-color=1.0/1.0/1.0/0.8 -sub-border-size=0 -sub-bold=yes -sub-font="Tahoma" -sub-shadow-offset=-3 -sub-shadow-color=0.0/0.0/0.0/0.2'
            )
    return invaded


# Gets general settings in class
class generalsettings:
    def __init__(self):
        # Default checkpoint is 1. If savedata exists, load checkpoint from savedata.
        round = 1
        points = 0
        if gen_config["Start from Last Checkpoint?"] == "ON":
            round = int(savecheckpoint)
            points = int(save_config["Save"]["Current Points"])
        self.checkpoint = round
        self.played = points
        self.breaktime = gen_config["Breaktime"]
        self.checkp = gen_config["Start from Last Checkpoint?"]
        if random_config["Randomize Invasion Chance?"] == "ON":
            self.inv = random.randint(1, int(inv_config["Invasion Chance Cap"]))
        else:
            # if savedata exists, load invase chance from savedata. Otherwise load defautl value.
            self.inv = int(save_config["Save"]["Current Invasion Chance"])
        if random_config["Randomize Modifier Chance?"] == "ON":
            self.mod = random.randint(1, int(mod_config["Modifier Chance Cap"]))
        else:
            # if savedata exists, load modifier chance from savedata. Otherwise load default value.
            self.mod = int(save_config["Save"]["Current Modifier Chance"])
        self.checkmod = int(mod_config["Modifier Chance Increase on Checkpoint"])
        self.checkinv = int(inv_config["Invasion Chance Increase on Checkpoint"])
        self.invon = inv_config["Invasion Rounds?"]
        self.modon = mod_config["Modifiers?"]
        # Set diemin and diemax default values if savedata does not exist. Otherwise load previous die values.
        self.defaultmin = int(gen_config["Default Die Min Size"])
        self.defaultmax = int(gen_config["Default Die Max Size"])
        self.diemin = int(save_config["Save"]["Current Die Min Size"])
        self.diemax = int(save_config["Save"]["Current Die Max Size"])
        self.ranround = random_config["Randomized Rounds"]
        self.modcap = int(mod_config["Modifier Chance Cap"])
        self.invcap = int(inv_config["Invasion Chance Cap"])


def general():
    return generalsettings()


class perksettings:
    def __init__(self):
        perklist = []
        if perk_config['"Die Size Increase" Perk'] == "ON":
            perklist.append("Increase Die Size")
        # if perk_config['"Double Roll" Perk'] == "ON":
        # perklist.append("doubleroll")
        if perk_config['"Video Skip" Perk'] == "ON":
            perklist.append("Skip 1 Video")
        # if perk_config['"Pause Video" Perk'] == "ON":
        # perklist.append("Pause Each Video for 10 Seconds")
        if inv_config["Invasion Rounds?"] == "ON":
            if perk_config['"Invasion Decrease" Perk'] == "ON":
                perklist.append("Decrease Invasion Chance")
            if perk_config['"No Invasions Next Round" Perk'] == "ON":
                perklist.append("No Invasions Next Round")
        if (
            perk_config['"Modifier Decrease" Perk'] == "ON"
            and mod_config["Modifiers?"] == "ON"
        ):
            perklist.append("Decrease Modifier Chance")

        self.rewardlist = perklist
        self.morerollnum = int(perk_config["Increase Die Size by?"])
        # self.pausenum = int(perk_config["Allowed Pause Time"])
        self.invnum = int(perk_config["Decrease Invasion Chance by what %?"])
        self.modnum = int(perk_config["Decrease Modifier Chance by what %?"])
        self.ppp = int(perk_config["Points per Perk"])
        self.perks = perk_config["Perks?"]


def perks():
    return perksettings()


class cursesettings:
    def __init__(self):
        curselist = []
        if curse_config['"Decrease Die Max Size" Curse'] == "ON":
            curselist.append("Decreased Die's Maximum Size!")
        if curse_config['"Decrease Die Min Size" Curse'] == "ON":
            curselist.append("Decreased Die's Minimum Size!")
        if curse_config['"Invasion Increase" Curse'] == "ON":
            curselist.append("Invasion Chance Increased!")
        if curse_config['"Modifier Increase" Curse'] == "ON":
            curselist.append("Modifier Chance Increased!")
        if (
            curse_config['"Go Back" Curse'] == "ON"
            and int(curse_config["Max Rounds to go back?"]) > 0
        ):
            curselist.append("Moving Back X Rounds!")
        self.curselist = curselist
        self.curse = curse_config["Curses?"]
        self.movebackmax = int(curse_config["Max Rounds to go back?"])
        self.baseinv = int(curse_config["Chance of Curse Per Invasion"])
        self.invnum = int(curse_config["Increase Invasion Chance by what %?"])
        self.modnum = int(curse_config["Increase Modifier Chance by what %?"])
        self.diemindec = int(curse_config["Decrease Die Min by?"])
        self.diemaxdec = int(curse_config["Decrease Die Max by?"])


def curses():
    return cursesettings()


# Gets save file data for main
# def loadsave():
#     if gen_config["Start from Last Checkpoint?"] == "ON":
#         return int(savecheckpoint)
#     else:
#         return 1


def saveit(
    checkpoint: int,
    currentinvasionchance: int,
    currentmodifierchance: int,
    mindie: int,
    maxdie: int,
    currentpoints: int,
):
    # if gen_config["Start from Last Checkpoint?"] == "ON":
    configwrite.savedata(
        checkpoint,
        currentinvasionchance,
        currentmodifierchance,
        mindie,
        maxdie,
        currentpoints,
    )


def deletesave():
    if path.exists("Savedata.txt"):
        os.remove("SaveData.txt")


random.seed(int(datetime.datetime.now().strftime("%Y%m%d%H%M%S")))
