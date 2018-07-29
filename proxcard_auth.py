#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################
__author__ = "Edwork"
__license__ = "GPL3"
__version__ = "1.0"

### RPI-MQTT-JSON-Multisensor
#
# Setup: Fill in variables under the configuration section 
# See following for more information: https://github.com/edwork/proxcard-mqtt-authentication
#
########################################################

import sys
import signal
import time
import re
import paho.mqtt.publish as publish
from evdev import InputDevice, list_devices, categorize, ecodes

SCANCODES = {
    # Scancode: ASCIICode
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
}

""" User Variables/Settings """
MQTT_HOST = '127.0.0.1'
MQTT_PORT = 1883
MQTT_USER = 'mqtt_user'
MQTT_PASSWORD = 'mqtt_pass'
MQTT_CLIENT_ID = 'badge-scanner-01'
MQTT_TOPIC_PREFIX = 'home/badge-scan'

""" Static Variables - Don't Change """
KEY_ENTER = 'KEY_ENTER'
DEVICE_NAME = 'RFIDeas USB Keyboard'
UUID = ''

auth_info = {
  'username':MQTT_USER,
  'password':MQTT_PASSWORD
}

ON_RFID = 0


def get_default_payload(rfid):
    return {'uuid': UUID, 'rfid': rfid}


def get_scanner_device():
    devices = map(InputDevice, list_devices())
    device = None
    for dev in devices:
        if dev.name == DEVICE_NAME:
            device = dev
            break
    return device


def read_input(device):
    rfid = ''
    for event in device.read_loop():
        data = categorize(event)
        if event.type == ecodes.EV_KEY and data.keystate == data.key_down:
            if data.keycode == KEY_ENTER:
                break
            rfid += SCANCODES[data.scancode]
    return rfid


def init(dev):
    if str(dev) == 'None':
        print "Device not found"
        sys.exit(1)

    try:
        device = InputDevice(dev.fn)
        device.grab()
    except:
        print "Unable to grab input device"
        sys.exit(1)

    return device


def cleanup(device):
    device.ungrab()


def sigterm_handler(_signo, _stack_frame):
    """
    When sysvinit sends the SIGTERM signal,
    cleanup before exiting.
    kill PID
    """
    print("[" + get_now() + "] received signal {}, exiting...".format(_signo))
    cleanup()
    sys.exit(0)

def publish_granted():
    granted_message = 'access_granted'
    publish.single(MQTT_TOPIC_PREFIX,
                   granted_message,
                   hostname = MQTT_HOST,
                   client_id = MQTT_CLIENT_ID,
                   auth = auth_info,
                   port = MQTT_PORT
                  )

def publish_denied():
    denied_message = 'access_denied'
    publish.single(MQTT_TOPIC_PREFIX,
                   denied_message,
                   hostname = MQTT_HOST,
                   client_id = MQTT_CLIENT_ID,
                   auth = auth_info,
                   port = MQTT_PORT
                  )

def publish_badgeid(scanned_badge):
    publish.single(MQTT_TOPIC_PREFIX + '/badgeid',
                   scanned_badge,
                   hostname = MQTT_HOST,
                   client_id = MQTT_CLIENT_ID,
                   auth = auth_info,
                   port = MQTT_PORT
                  )

static_roster = [
                '111111', """ /// User 1 /// """
                '222222', """ /// User 2 /// """
                '333333', """ /// User 3 """
                'dummy'   """ /// Dummy entry as there is a list bug /// """
                ]


if __name__ == "__main__":
    #Register for SIGTERMs
    signal.signal(signal.SIGTERM, sigterm_handler)

    device_name = get_scanner_device()
    device = init(device_name)

    print 'Found device: %s' % DEVICE_NAME

    while True:
        try:
            rfid = read_input(device)
            rfid_numonly = (re.search(r"(?<=\;)[^\]]+", rfid)).group(0)
            print 'RFID card read, value: %s' %rfid_numonly
            if rfid_numonly in static_roster :
                print('Access Granted!')
                publish_granted()
            else :
                print('Access Denied!')
                publish_denied()
        except ValueError:
            time.sleep(0.1)
        except Exception, e:
            print e
            cleanup(device)
            sys.exit(1)
