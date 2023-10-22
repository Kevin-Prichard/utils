#!/usr/bin/env python3

import re
from subprocess import Popen, PIPE, run
import sys
from typing import List

DEVICE_ID_RX = re.compile(r".*id=(\d+)")

def get_devices():
    devs = []
    result = run(['xinput', 'list', '--long'], capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            "Could not obtain list of devices via xinput; running under X11?")
    return result.stdout.decode('UTF-8').split('\n')


def get_touchpad_id(name, devs):
    for row in devs:
        if name in row:
            match = DEVICE_ID_RX.match(row)
            if match and (dev_id := match.groups(1)):
                return dev_id[0]


def get_button_states(dev_id):
    result = run(['xinput', 'get-button-map', dev_id], capture_output=True)
    return result.stdout.decode('UTF-8').split('\n')[0].split(r" ")


def toggle_touchpad_buttons(touchpad_name,
                            toggleable_button_positions: List):
    devices = get_devices()
    touchpad_id = get_touchpad_id(touchpad_name, devices)
    button_states = get_button_states(touchpad_id)
    new_toggleable_states = []
    on_or_off = 0
    for pos in toggleable_button_positions:
        if int(button_states[pos]) == 0:
            new_toggleable_states.append(1 + pos)
            on_or_off += 1
        else:
            new_toggleable_states.append(0)
            on_or_off += -1
    new_button_states = (str(val) for val in new_toggleable_states +
                      button_states[len(toggleable_button_positions):])
    run(
        ['xinput', 'set-button-map', touchpad_id, *new_button_states],
        capture_output=True,
    )
    print(f"Bottom button row turned {'off' if on_or_off < 0 else 'on'}")


if __name__ == "__main__":
    try:
        touchpad_name = sys.argv[1]
    except:
        touchpad_name = "Elan Touchpad"

    if len(sys.argv) > 2:
        toggle_buttons = [int(val) for val in sys.argv[2:]]
    else:
        toggle_buttons = [0, 1, 2]

    toggle_touchpad_buttons(
        touchpad_name=touchpad_name,
        toggleable_button_positions=toggle_buttons,
    )
