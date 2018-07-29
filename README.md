
## Description

Many people are issued Proxcards at work and already carry them the majority of the time when entering or leaving their homes. This program will allow you to use your existing card interface with your home automation system (like HomeAssistant).

This script allows you to define a list of 'authorized' proxcards and fire an MQTT message to your broker with the scan result (access granted/denied + ID number).

The Proxcard Scanner used is a [RFIDeas pcProx 125 kHz][rfid] which basically simulates keyboard input. This is best coupled with a Raspberry Pi or nearby Linux box.

The python script uses [evdev][evdev] to read the input and compare it against the defined array of badges and [paho-mqtt][paho-mqtt] to interface with any MQTT capable system.


## Documentation

Once you plug the RFID reader to the Pi's USB, if you run the `lsusb` command it should be listed there:

```
Bus 001 Device 002: ID 0424:9514 Standard Microsystems Corp. 
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp. 
Bus 001 Device 004: ID 0bda:8176 Realtek Semiconductor Corp. RTL8188CUS 802.11n WLAN Adapter
Bus 001 Device 005: ID 0c27:3bfa RFIDeas, Inc pcProx Card Reader
```

Once your device is recognized, you can run the script:

```bash
$ python proxcard_auth.py
```

## Config

```ini

MQTT_HOST = '127.0.0.1'
MQTT_PORT = 1883
MQTT_USER = 'mqtt_user'
MQTT_PASSWORD = 'mqtt_pass'
MQTT_CLIENT_ID = 'badge-scanner-01'
MQTT_TOPIC_PREFIX = 'home/badge-scan'

...

static_roster = [
                '111111', """ /// User 1 /// """
                '222222', """ /// User 2 /// """
                '333333', """ /// User 3 """
                'dummy'   """ /// Dummy entry as there is a list bug /// """
                ]

```
## Requirements



[rfid]: https://www.rfideas.com/support/product-support/pcprox-125-khz-enroll
[evdev]: https://github.com/gvalkov/python-evdev
[paho-mqtt]: https://www.eclipse.org/paho/clients/python/docs/
