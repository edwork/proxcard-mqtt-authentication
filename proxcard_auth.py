#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQTT Proxcard Authentication
###
Meant to be used with an RFIDeas PcProx Scanner or similar.
Sends an MQTT message to your broker upon scanning
and comparing to a defined list.
###
Setup: Fill in variables under the configuration section
See following for more information:
https://github.com/edwork/proxcard-mqtt-authentication
"""

import sys
import re
import time
import signal
import yaml
import paho.mqtt.publish
from evdev import InputDevice, list_devices, categorize, ecodes

__author__ = "Edwork"
__license__ = "GPL3"
__version__ = "1.0"

# Map Codes to ASCII
SCANCODES = {
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3',
    5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP',
    15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O',
    25: u'P', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G',
    35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'Z',
    45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT',
    56: u'LALT', 100: u'RALT'
}

# Settings - Change These
MQTT_HOST = '172.21.3.45'
MQTT_PORT = 1883
MQTT_USER = 'noobuser'
MQTT_PASSWORD = 'lamepass'
MQTT_CLIENT_ID = 'badge-scanner-01'
MQTT_TOPIC_PREFIX = 'echo/badge-scan'

# Static Variables
KEY_ENTER = 'KEY_ENTER'
DEVICE_NAME = 'RFIDeas USB Keyboard'
UUID = ''
ACCESS_RESULT = ''
ON_RFID = 0
AUTH_INFO = {
    'username':MQTT_USER,
    'password':MQTT_PASSWORD
}

# Import Roster of Users
ROSTER = yaml.load(open('roster.yaml'))

def get_scanner_device():
    """Map to a Hardware RFID Scanner"""
    devices = map(InputDevice, list_devices())
    device = None
    for dev in devices:
        if dev.name == DEVICE_NAME:
            device = dev
            break
    return device

def read_input(device):
    """Read Input from scanned badge"""
    rfid = ''
    for event in device.read_loop():
        data = categorize(event)
        if event.type == ecodes.EV_KEY and data.keystate == data.key_down:
            if data.keycode == KEY_ENTER:
                break
            rfid += SCANCODES[data.scancode]
    return rfid

def init(dev):
    """Initialize the Found Device"""
    if str(dev) == 'None':
        print('Device not found')
        sys.exit(1)
    try:
        device = InputDevice(dev.fn)
        device.grab()
    except Exception:
        print('Unable to grab input device')
        sys.exit(1)
    return device

def publish_message(access_result):
    """Send MQTT Message"""
    paho.mqtt.publish.single(
        MQTT_TOPIC_PREFIX,
        access_result,
        hostname=MQTT_HOST,
        client_id=MQTT_CLIENT_ID,
        auth=AUTH_INFO,
        port=MQTT_PORT
    )

def cleanup(device):
    """Unbind the Device"""
    device.ungrab()

def sigterm_handler(_signo, _stack_frame):
    """Terminate Cleanly"""
    print("received signal {}, exiting...".format(_signo))
    cleanup(_stack_frame)
    sys.exit(0)

def main():
    """Main Program"""
    signal.signal(signal.SIGTERM, sigterm_handler)
    device = init(get_scanner_device())
    print('Found device: ' + DEVICE_NAME + '. Ready!')
    while True:
        try:
            rfid = read_input(device)
            rfid_numonly = (re.search(r"(?<=\;)[^\]]+", rfid)).group(0)
            print('RFID card read, value: ' + rfid_numonly)
            if rfid_numonly in ROSTER:
                print('Access Granted!')
                publish_message('access_granted')
            else:
                print('Access Denied!')
                publish_message('access_denied')
        except ValueError:
            time.sleep(0.1)
        except Exception:
            cleanup(device)
            sys.exit(1)

if __name__ == "__main__":
    main()
