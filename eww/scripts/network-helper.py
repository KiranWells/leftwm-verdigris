#!/usr/bin/env python

'''
A helper script to process information about connected networks
and the like to allow for a more helpful and responsive network
widget.

It's goals are:
- provide a periodically updating list of networks
  - needs to keep a cache of the network list, updated every few minutes
- provide a status signal for connecting to networks
- printing a stream of .yuck for saved and available networks
- connecting to networks and updating eww's status during that
- printing the status of the network
'''

import os
import sys
from datetime import datetime
import re

HOME = os.environ["HOME"]
UPDATE_MINUTES = 5
NETCACHE = f'{HOME}/.cache/minimal-theme-networks'
SSID = os.popen('iwgetid -r').read().strip()

NETWORK_YUCK_TEMPLATE = '''
(button 
  :onclick "./scripts/network-helper.py --on {0}" 
  :timeout "100s"
  :class {{ "{0}" != "{2}" ? "popup-option": "popup-option selected" }} 
  (box 
    :space-evenly false
    (box :valign "end" "{0}") 
    (box :hexpand true :halign "end" :class "popup-strength" "{1}")))
'''

# manage network cache
def get_and_update_cache():
  # read cache
  text = ''
  with open(f"{HOME}/.cache/minimal-theme-networks", 'r') as file:
    text = file.read()
  data = [re.sub(r'\\:', ';', line).split(':') for line in text.split('\n')]

  # update cache
  modified_time = datetime.fromtimestamp(os.stat(NETCACHE).st_mtime)
  age = datetime.now() - modified_time
  if (age.seconds > UPDATE_MINUTES*60):
    # spawn and forget
    os.system(f'nmcli -t device wifi list > {NETCACHE} & disown')

  return data

def get_saved_networks():
  saved_list = os.popen('nmcli -t connection show').read()
  # get just the connection names
  saved_list = [re.sub(r'\\:', ';', line).split(':')[0] for line in saved_list.split('\n') if len(line) > 1 and 'wireless' in line]
  return saved_list

def print_available_networks():
  data = get_and_update_cache()
  # filter networks by selected network or average connection strength
  data = [line for line in data if len(line) >= 7 and (line[0] == '*' or line[7][1] == '▄')]

  names = set()

  # print yuck data
  print('(box :orientation "v"')
  for line in data:
    name = line[2]
    if name in names:
      continue
    names.add(name)
    strength = line[7].replace('_', '▁')
    print(NETWORK_YUCK_TEMPLATE.format(name, strength, SSID))
  print(')')

def print_saved_networks():
  saved_list = get_saved_networks()
  data = get_and_update_cache()
  # filter networks by selected network or average connection strength
  data = [line for line in data if len(line) >= 7 and (line[0] == '*' or line[7][1] == '▄')]

  names = [line[2] for line in data]

  print('(box :orientation "v"')
  for name in saved_list:
    strength = '▁▁▁▁'
    if name in names:
      index = names.index(name)
      strength = data[index][7].replace('_', '▁')
    print(NETWORK_YUCK_TEMPLATE.format(name, strength, SSID))
  print(')')

# manage connections with progress
def connect(network):
  saved_list = get_saved_networks()
  os.system('eww -c . update NET_IN_PROGRESS=true')
  if network in saved_list:
    os.system(f'nmcli con up {network}')
  else:
    os.system(f'nmcli dev wifi con up {network}')
  os.system('eww -c . update NET_IN_PROGRESS=false')

def print_status():
  status = os.popen('cat /sys/class/net/wlan0/operstate').read().strip()
  if status == "up":
    print('直')
  else:
    print('睊')

def fix_network():
  os.system('systemctl restart NetworkManager')

if len(sys.argv) < 2:
  exit(1)

if sys.argv[1] == '--list-available':
  print_available_networks()

if sys.argv[1] == '--list-saved':
  print_saved_networks()

if sys.argv[1] == '--status':
  print_status()

if sys.argv[1] == '--fix':
  fix_network()

if sys.argv[1] == '--on':
  if len(sys.argv) < 3:
    exit(1)
  connect(sys.argv[2])
