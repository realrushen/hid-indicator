## X-Keys HID Indicator

This program displays the buttons on the XK-24 keyboard in the graphical
interface and highlights the keyboard buttons in red or blue at the user's
command.

## Dependencies

1. Python 3.9
2. hidapi 0.13.1
3. PyQt5 5.15.9

## Installation

1. Clone repository `` git clone https://github.com/realrushen/hid-indicator``
2. Create Python Virtual Environment ``python -m venv venv``
3. Install dependencies ``pip install -r requirements.txt``

## Usage:

In order for /dev entries for X-Keys products to be readable by non-root
users, a udev rule will need to be placed in /etc/udev/rules.d . A sample
udev rule file is located in the udev folder. Simply copy this file to
/etc/udev/rules.d using:
```
    sudo cp udev/90-xkeys.rules /etc/udev/rules.d/
```
from this folder.