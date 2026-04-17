# boot.py — runs once at power-on before code.py
# Enables the keyboard USB HID interface

import usb_hid
usb_hid.enable(usb_hid.Device.KEYBOARD)
