import os
import re
import time
import datetime

SDK = "C:/Users/Pandora/AppData/Local/Android/Sdk/platform-tools/"
ADB = "adb"
SHELL = "shell"
EXECOUT = "exec-out"
SCENARIO = "c:/s1.txt"

testsite_array = []


class Action:

    def __init__(self):
        self.start = None
        self.end = None
        self.subActions = []
        pass


def exportTime(line):
    match = re.search(r"\[([A-Za-z0-9_.]+)\]", line)
    if match is not None:
        return float(match.group(1))


# TAB signature
# *************************************
# /dev/input/event1: 0003 0039 00000000
# /dev/input/event1: 0003 0030 000001e0
# /dev/input/event1: 0003 003a 00000081
# /dev/input/event1: 0003 0035 00005425
# /dev/input/event1: 0003 0036 000062cc
# /dev/input/event1: 0000 0000 00000000
# /dev/input/event1: 0003 003a 00000081
# /dev/input/event1: 0003 0039 ffffffff
# /dev/input/event1: 0000 0000 00000000
# **************************************
# adb shell getevent -lp
# ABS_MT_POSITION_X     : value 0, min 0, max 32767, fuzz 0, flat 0, resolution 0
# ABS_MT_POSITION_Y     : value 0, min 0, max 32767, fuzz 0, flat 0, resolution 0
# x = round((23604/32767) * 1080)
# y = round((25940/32767)* 1920)
PHYSICAL_WIDTH = 1080
PHYSICAL_HEIGHT = 1920
MAX_RESOLUTION = 32767

actions = []

print("Loading Events File Format")
with open(SCENARIO) as my_file:
    ignoreNext = False
    payload = ''

    action = {}

    for line in my_file:
        x = 0
        y = 0

        try:
            line = re.sub(" +", " ", line)
            line = line.replace("'/dev/input/event1: ", "")
            line = line.replace("[ ", "[")
            s = line.split(" ")
            if len(s) >= 4:
                TM = exportTime(s[0])
                if TM is None:
                    continue

                EV = int(s[2], 16)
                CM = int(s[3], 16)
                VA = int(s[4], 16)

                # press down
                if EV == 3 and CM == 57 and VA == 0:
                    action = Action()
                    action.start = TM
                    action.end = TM

                # major
                if EV == 3 and CM == 48:
                    pass

                # touch pressure
                if EV == 3 and CM == 58:
                    pass

                # X coordinate
                if EV == 3 and CM == 53:
                    x = round((VA / MAX_RESOLUTION) * PHYSICAL_WIDTH)
                    action.subActions.append({"TM": TM, "X": x, "AXIS": "X"})
                    action.end = TM

                # Y coordinate
                if EV == 3 and CM == 54:
                    y = round((VA / MAX_RESOLUTION) * PHYSICAL_HEIGHT)
                    action.subActions.append({"TM": TM, "Y": y, "AXIS": "Y"})
                    action.end = TM

                if EV == 3 and CM == 57 and VA > 1:
                    actions.append(action)
                    action = None
                    action.end = TM
        except:
            pass

    print("Translate Events To Actions Complete \nStart To Execute:")

    if len(actions) != 0:
        print("Going To Execute:" + str(len(actions)) + " Actions")
        previousTime = None
        for a in actions:
            print("TAP Execute")
            if len(a.subActions) == 2:
                command = SDK + ADB + " " + SHELL + " input touchscreen swipe " + str(a.subActions[0]["X"]) \
                          + " " + str(a.subActions[1]["Y"]) + " " + str(a.subActions[0]["X"]) \
                          + " " + str(a.subActions[1]["Y"]) + " " + str(int(a.end - a.start))

                if previousTime is None:
                    previousTime = a.end

                delta = a.end - previousTime
                previousTime = a.end

                time.sleep(delta * 0.8)
                os.system(command)
                print(command + " Delta:" + str(delta))

            elif len(a.subActions) > 2:
                l = len(a.subActions)
                print("Swipe Execute")

                xlist = [item for item in a.subActions if item["AXIS"] == "X"]
                ylist = [item for item in a.subActions if item["AXIS"] == "Y"]

                command = SDK + ADB + " " + SHELL + " input touchscreen swipe " + str(xlist[0]["X"]) \
                          + " " + str(ylist[0]["Y"]) + " " + str(xlist[len(xlist) - 1]["X"]) \
                          + " " + str(ylist[len(ylist) - 1]["Y"]) + " " + str(int((a.end - a.start) * 1000))

                if previousTime is None:
                    previousTime = a.end

                delta = a.end - previousTime
                previousTime = a.end

                time.sleep(delta * 0.8)
                os.system(command)
                print(command + " Delta:" + str(delta))
