from argparse import ArgumentError
from ast import arg
from asyncore import write
from geolite2 import geolite2
import socket
import os
import subprocess
import sys
import time
from datetime import datetime
import shutil
import json

interfaceToCaptureOn = "enp5s0"

settings = {
    "log": False,
    "network_interface": "cH4nG3_tH1S",
}

globalLogPath = "./logs/globalLogFile.log"
globalLatestLogPath = "./logs/latest.log"
global_settings_path = "./settings.json"
now = datetime.now()


def read_from_json(json_path: str):
    with open(json_path, "r") as json_file:
        data = json.load(json_file)
    json_file.close()
    return data


def createGlobalLogFile():
    # Master Global Log File
    if not os.path.exists(globalLogPath):
        logFile = open(globalLogPath, "a+")
        logFile.close()

    # Json settings file
    if not os.path.exists(global_settings_path):
        json_settings = json.dumps(settings)

        with open("settings.json", "w") as jsonfile:
            jsonfile.write(json_settings)
        jsonfile.close()

    # Master Global Latest Log File
    if os.path.exists(globalLatestLogPath):
        os.remove(globalLatestLogPath)
    if not os.path.exists(globalLatestLogPath):
        logFile = open(globalLatestLogPath, "a+")
        logFile.close()


if not os.path.exists('./logs'):
    os.makedirs('./logs')

createGlobalLogFile()

interfaceToCaptureOn = read_from_json("./settings.json")

cmd = f"sudo tshark -i {interfaceToCaptureOn}"
print(f"----------------------\n Capturing on {interfaceToCaptureOn}.\n----------------------")
time.sleep(1)
print(" - Use argument ´-l // --log´ to log to a file. And ´-c // --clear´ to clear logs.")
process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
time.sleep(2)

# my_ip = socket.gethostbyname(socket.gethostname())

argument = str(sys.argv[1] if len(sys.argv) > 1 else '.')

dt_string = now.strftime("%d/%m/%Y %H:%M:%S")


def write_to_file(text_to_write, path_to_file, typeOfWrite):
    if os.path.exists(path_to_file):
        write_file = open(path_to_file, typeOfWrite)
        write_file.write(text_to_write)
        write_file.close()


def logOutput(msg, logType):
    # Log
    if logType == 1:
        # print("\n[ LOG ] " + msg)
        write_to_file("\n[LOG] " + msg, globalLogPath, "a+")
        write_to_file("\n[LOG] " + msg, globalLatestLogPath, "a+")
    # Error
    elif logType == 2:
        # print("\n[ ERROR ] " + msg)
        write_to_file("\n[ERROR] " + msg, globalLogPath, "a+")
        write_to_file("\n[ERROR] " + msg, globalLatestLogPath, "a+")
    # Warning
    elif logType == 3:
        # print("\n[ WARNING ] " + msg)
        write_to_file("\n[WARNING] " + msg, globalLogPath, "a+")
        write_to_file("\n[WARNING] " + msg, globalLatestLogPath, "a+")


global logging

if argument == "-l" or argument == "--log":
    logging = True
    logOutput("-------------" + dt_string + "-------------", 3)
    write_to_file("-------------" + dt_string + "-------------", globalLatestLogPath, "w")
    write_to_file(dt_string, globalLatestLogPath, "w")
    print("\n[ WARNING ] " + "[ Logging to file activated... ]")
    # logOutput("[ Logging to file activated... ]", 3)
elif argument == "-c" or argument == "--clear":
    if os.path.exists("./logs"):
        shutil.rmtree("./logs", ignore_errors=True)
    logging = False
    print("Deleted all logs and exited with code 0.")
    exit(1)
else:
    logging = False
    print("\n[ WARNING ] " + "[ Not logging to file... ]")
    # logOutput("[ Not logging to file... ]", 3)

time.sleep(1)

my_ip = "192.168.1.72"
print("\n[ LOG ] " + "Local_IP: " + my_ip)
if logging:
    logOutput(f"Local_IP = {my_ip}", 1)

reader = geolite2.reader()


def get_loc(ip):
    location = reader.get(ip)

    try:
        country = location["country"]["names"]["en"]
    except:
        country = "Unknown"

    try:
        subdivision = location["subdivisions"][0]["names"]["en"]
    except:
        subdivision = "Unknown"

    try:
        city = location["city"]["names"]["en"]
    except:
        city = "Unknown"

    return country, subdivision, city


for line in iter(process.stdout.readline, b""):
    columns = str(line).split(" ")

    if "CLASSIC-STUN" in columns or "classicstun" in columns:

        if "->" in columns:
            src_ip = columns[columns.index("->") - 1]

        elif "\\xe2\\x86\\x92" in columns:
            src_ip = columns[columns.index("\\xe2\\x86\\x92") - 1]
        else:
            continue

        if "192" in src_ip:
            continue

        if src_ip == my_ip:
            continue

        try:
            country, sub, city = get_loc(src_ip)
            if logging:
                logOutput(("<" + src_ip + "> " + country + ", " + sub + ", " + city), 1)
            print("<" + src_ip + "> " + country + ", " + sub + ", " + city)
        except:
            try:
                real_ip = socket.gethostbyname(src_ip)
                country, sub, city = get_loc(real_ip)
                if logging:
                    logOutput(("<" + src_ip + "> " + ">>> " + country + ", " + sub + ", " + city), 1)
                print("<" + src_ip + "> " + ">>> " + country + ", " + sub + ", " + city)
            except:
                print("Not found")
