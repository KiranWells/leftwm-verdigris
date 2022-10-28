#!/usr/bin/env python

'''
A helper script to process information about volume controls

It's goals are:
- provide a list of available volume controls
  - print that list in .yuck format
- similar controls to pavucontrol
'''

import os
import sys
import re

SCAN_SECONDS = 6

CONTROL_YUCK_TEMPLATE = '''
(centerbox :orientation "h" :class "{classname}"
    (box :class "label" :halign "start"
            "{name}")
            (box "")
    (box :space-evenly false :halign "end" (scale :min 0
            :max 101
            :orientation "h"
            :active true
            :value {value}
            :width 80
            :onchange "{onchange}")
    (box :halign "end" (button :onclick "{onclick}" 
            :timeout "1s" 
            :width 30
                (icon :shift -5 "{status}")))
            )
    )
'''

# process device data into list of ["Device", uuid, name]
def get_amixer():
  text = os.popen('amixer scontrols').read()
  data = []
  for line in text.split('\n'):
    control = {
        'name': '',
        'value': '',
        'enabled': False,
        'input': False,
        'onclick': '',
        'onchange': '',
    }
    ma = re.match(".*'([^']+)'.*", line)
    # print(line, ma.groups())
    if not ma:
        continue
    control['name'] = ma.groups()[0]
    more_text = os.popen(f'amixer -D pulse sget {control["name"]}').read()
    ma = re.match(f".* (\w+) \d+ \[(\d+).\] \[(on|off)\]", more_text, re.M | re.DOTALL)
    # print(control, more_text, ma)
    if not ma:
        continue
    control['value'] = ma.groups()[1]
    control['enabled'] = ma.groups()[2] == 'on'
    control['input'] = ma.groups()[0] == 'Capture'
    control['onclick'] = f'amixer -D pulse sset {control["name"]} toggle'
    control['onchange'] = f'amixer -D pulse sset {control["name"]} {{}}%'
    data.append(control)

  return data

def get_pactl():
  text = os.popen('pactl list sink-inputs').read()
  text = text.split('Sink Input')
  data = []
  data = []
  for sink in text:
    info = {}
    sink_id = -1
    for line in sink.split('\n'):
        if len(line) < 2:
            continue
        # print(line)
        if line.strip()[0] == '#':
            sink_id = int(line[2:])
            # print(sink_id)
        line = line.strip().split(': ')
        if len(line) == 1:
            line = line[0].split(' = ')
        if len(line) < 2:
            continue
        # reconstruct later splits
        line[1] = ': '.join(line[1:])
        info[line[0]] = line[1]

    if len(info) == 0:
        continue
    # print(info)   

    value = re.match('.* (\d+)%.*', info['Volume']) 

    control = {
        'name': info['application.process.binary'].replace('"', ''),
        'value': value.groups()[0] if value is not None else 0,
        'enabled': info['Mute'] == 'no',
        'input': False,
        'onclick': f'pactl set-sink-input-mute {sink_id} toggle',
        'onchange': f'pactl set-sink-input-volume {sink_id} `echo {{}} | grep -Po \'^[0-9]+\'`%',
    }
    # print(control)
    data.append(control)
  text = os.popen('pactl list sources').read()
  text = text.split('Source #')
  for sink in text:
    if len(sink) < 2:
        continue
    sink_id = int(sink.split('\n')[0])
    info = {}
    for line in sink.split('\n'):
        if len(line) < 2:
            continue
        # print(line)
        # print(sink_id)
        line = line.strip().split(': ')
        if len(line) == 1:
            line = line[0].split(' = ')
        if len(line) < 2:
            continue
        # reconstruct later splits
        line[1] = ': '.join(line[1:])
        info[line[0]] = line[1]

    if len(info) == 0:
        continue
    if info['device.class'] == '"monitor"':
        continue
    # print(json.dumps(info, indent=2))

    value = re.match('.* (\d+)%.*', info['Volume']) 

    name = info[info['Active Port']]

    control = {
        'name': name[:name.index('(')],
        'value': value.groups()[0] if value is not None else 0,
        'enabled': info['Mute'] == 'no',
        'input': True,
        'onclick': f'pactl set-source-mute {sink_id} toggle',
        'onchange': f'pactl set-source-volume {sink_id} `echo {{}} | grep -Po \'^[0-9]+\'`%'
    }
    # print(control)
    data.append(control)

  return data

# print a list of devices in yuck
def print_list():
  print('(box :orientation "v"')

  data = get_amixer()
  data.extend(get_pactl())
  inputs = [c for c in data if c['input']]
  outputs = [c for c in data if not c['input']]
  print("""(box :class "title"
            "Outputs")""")
  for control in outputs:
    make_template(control)
  print("""(box :class "title"
            "Inputs")""")
  for control in inputs:
    make_template(control)

  print(')')

def make_template(control):
    print(CONTROL_YUCK_TEMPLATE.format(
        name=control['name'], 
        value=control['value'], 
        status="" if control['enabled'] else "", 
        onclick=control['onclick'],
        classname='input' if control['input'] else 'output',
        onchange=control['onchange']
        ))

if len(sys.argv) < 2:
  exit(1)


if sys.argv[1] == '--list':
  print_list()
