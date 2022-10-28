#!/usr/bin/env python

'''
A helper script to process information about bluetooth 
power and devices

It's goals are:
- provide a list of available devices, and determine whether they are connected
  - print that list in .yuck format
- connect and disconnect to devices, managing eww's state during processing
- allowing scanning for a certain length of time (a few seconds right now)
'''

import os
import sys
import subprocess
import time

SCAN_SECONDS = 6

BLUETOOTH_YUCK_TEMPLATE = '''
(button 
  :onclick "./scripts/bluetooth-helper.py --on {uuid}" 
  :timeout "100s"
  :class {{ {connected} ? "popup-option selected": "popup-option" }} 
  (box 
    :space-evenly false 
    (box "{name}")))
'''

# process device data into list of ["Device", uuid, name]
def get_data():
  text = os.popen('bluetoothctl devices').read()
  data = []
  for line in text.split('\n'):
    line = line.split(' ')
    # ignore empty lines
    if len(line) < 2:
      continue
    # put the name back together
    line[2] = ' '.join(line[2:])
    # check for devices without names (where name = uuid.replace(:, -))
    if line[1].replace(':', '-') != line[2]:
      data.append(line)

  return data

# process controller data into
# dict. Powered and Discovering (scanning) 
# are the important keys
def get_info():
  text = os.popen('bluetoothctl show').read()
  info = {}
  for line in text.split('\n'):
    if len(line) == 0 or line[0] != '\t':
      continue
    line = line.strip().split(': ')
    # reconstruct later splits
    line[1] = ': '.join(line[1:])
    info[line[0]] = line[1]

  return info

# determines whether the device is connected
def get_connected(uuid):
  info = os.popen(f'bluetoothctl info {uuid}').read()
  return 'Connected: yes' in info

# print a list of devices in yuck
def print_devices():
  data = get_data()

  print('(box :orientation "v"')
  for line in data:
    print(BLUETOOTH_YUCK_TEMPLATE.format(name=line[2], uuid=line[1], connected="true" if get_connected(line[1]) else "false"))
  print(')')

# manage connections with progress
def connect(uuid):
  os.system('eww -c . update BT_IN_PROGRESS=true')

  # spawn a connection process
  process = None
  if get_connected(uuid):
    process = subprocess.Popen(['bluetoothctl', 'disconnect', uuid], stdout=subprocess.PIPE)
  else:
    process = subprocess.Popen(['bluetoothctl', 'connect', uuid], stdout=subprocess.PIPE)
  line = process.stdout.readline()

  # read until connected/disconnected
  while line != b'':
    # determine if Device uuid Connected: 
    # or S/successful was in the line
    if ((b"Device" in line 
        and bytes(uuid, "utf-8") in line 
        and b"Connected" in line)
        or (b"uccessful" in line)):
      break
    line = process.stdout.readline()
  
  # stop the process (sometimes it continues showing status)
  process.terminate()
  # update eww
  os.system('eww -c . update BT_IN_PROGRESS=false')

def toggle_power():
  dev_info = get_info()
  if dev_info["Powered"] == "yes":
    os.system('bluetoothctl power off')
  else:
    os.system('bluetoothctl power on')

def toggle_scan():
  dev_info = get_info()
  # if already scanning, don't start again
  if dev_info["Discovering"] == "yes":
    return
  # if not powered on, power on (required for scanning)
  if dev_info["Powered"] == "no":
    os.system('bluetoothctl power on')
  
  # scan for a few seconds
  os.system('eww -c . update BT_SCAN_ON=true')
  process = subprocess.Popen(['bluetoothctl', 'scan', 'on'])
  time.sleep(SCAN_SECONDS)
  process.terminate()
  os.system('eww -c . update BT_SCAN_ON=false')


if len(sys.argv) < 2:
  exit(1)


if sys.argv[1] == '--list-available':
  print_devices()

if sys.argv[1] == '--toggle-power':
  toggle_power()

if sys.argv[1] == '--toggle-scan':
  toggle_scan()

if sys.argv[1] == '--on':
  if len(sys.argv) < 3:
    exit(1)
  connect(sys.argv[2])
