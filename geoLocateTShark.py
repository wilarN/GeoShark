from argparse import ArgumentError
from geolite2 import geolite2
import socket
import os
import subprocess
import sys
import time

interfaceToCaptureOn = "enp5s0"

cmd = f"sudo tshark -i {interfaceToCaptureOn}"
print(f"----------------------\n Capturing on {interfaceToCaptureOn}.\n----------------------")
time.sleep(1)
print(" - Use argument ´-l´ to log to a file.")
process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
time.sleep(2)
#my_ip = socket.gethostbyname(socket.gethostname())

argument = str(sys.argv[1] if len(sys.argv) > 1 else '.')


globalLogPath = "./logs/globalLogFile.txt"


def createGlobalLogFile():
    if os.path.exists(globalLogPath):
        logFile = open(globalLogPath, "x")
        logFile.close()

createGlobalLogFile()

def write_to_file(text_to_write, path_to_file):
    if os.path.exists(path_to_file):
        write_file = open(path_to_file, "w")
        write_file.write(text_to_write)


def logOutput(msg, logType):
    # Log
    if logType == 1:
        # print("\n[ LOG ] " + msg)
        write_to_file("\n[ LOG ]" + msg, globalLogPath)
    # Error
    elif logType == 2:
        # print("\n[ ERROR ] " + msg)
        write_to_file("\n[ ERROR ]" + msg, globalLogPath)
    # Warning
    elif logType == 3:
        # print("\n[ WARNING ] " + msg)
        write_to_file("\n[ WARNING ]" + msg, globalLogPath)


if argument == "-l":
	print("\n[ WARNING ] " + "[ Logging to file activated... ]")
	logOutput("[ Logging to file activated... ]", 3)
else:
	print("\n[ WARNING ] " + "[ Not logging to file... ]")
	logOutput("[ Not logging to file... ]", 3)

time.sleep(1)

my_ip = "192.168.1.72"
print("\n[ LOG ] " + "Local_IP: " + my_ip)
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
	columns= str(line).split(" ")

	if "CLASSIC-STUN" in columns or "classicstun" in columns:

		if "->"  in columns:
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
			logOutput(("<" + src_ip + "> " + country + ", " + sub + ", " + city), 1)
			print("<" + src_ip + "> " + country + ", " + sub + ", " + city)
		except:
			try:
				real_ip = socket.gethostbyname(src_ip)
				country, sub, city = get_loc(real_ip)
				logOutput(("<" + src_ip + "> " + ">>> " + country + ", " + sub + ", " + city), 1)
				print("<" + src_ip + "> " + ">>> " + country + ", " + sub + ", " + city)
			except:
				print("Not found")