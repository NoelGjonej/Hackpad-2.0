import board
import busio
import digitalio
import rotaryio
import usb_hid
import time

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.modules.encoder import EncoderHandler
from kmk.extensions.media_keys import MediaKeys

# ── OLED (SSD1306 128x32 via I2C) ────────────────────────────────────────────
import displayio
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label
import adafruit_imageload

displayio.release_displays()

i2c = busio.I2C(scl=board.SCL, sda=board.SDA)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

# ── Volume state ──────────────────────────────────────────────────────────────
vol_level  = 50    # local display counter 0–100
is_muted   = False

# ── Build the OLED UI ─────────────────────────────────────────────────────────
splash = displayio.Group()
display.show(splash)

# Line 0 — title
title_label = label.Label(terminalio.FONT, text="  XIAO Macropad ", x=0, y=4, color=0xFFFFFF)
splash.append(title_label)

# Line 1 — vol or mute text
vol_label = label.Label(terminalio.FONT, text=" VOL:  50%       ", x=0, y=14, color=0xFFFFFF)
splash.append(vol_label)

# Line 2 — bar background (dark rectangle)
bar_bg = displayio.Bitmap(128, 7, 2)
bar_bg_palette = displayio.Palette(2)
bar_bg_palette[0] = 0x000000
bar_bg_palette[1] = 0x444444
for x in range(128):
    for y in range(7):
        bar_bg[x, y] = 1
bar_bg_sprite = displayio.TileGrid(bar_bg, pixel_shader=bar_bg_palette, x=0, y=22)
splash.append(bar_bg_sprite)

# Line 2 — bar fill (white, width changes with volume)
bar_fill = displayio.Bitmap(128, 7, 2)
bar_fill_palette = displayio.Palette(2)
bar_fill_palette[0] = 0x000000
bar_fill_palette[1] = 0xFFFFFF
bar_fill_sprite = displayio.TileGrid(bar_fill, pixel_shader=bar_fill_palette, x=0, y=22)
splash.append(bar_fill_sprite)

def update_bar(percent):
    """Fill the bar bitmap proportionally to percent (0–100)."""
    filled_px = int((percent / 100) * 128)
    for x in range(128):
        for y in range(7):
            bar_fill[x, y] = 1 if x < filled_px else 0

def update_oled():
    """Refresh all OLED elements from current state."""
    global vol_level, is_muted
    if is_muted:
        vol_label.text = "   >> MUTED <<   "
        update_bar(0)
    else:
        vol_label.text = " VOL: {:3d}%       ".format(vol_level)
        update_bar(vol_level)

update_oled()

# ── Keyboard setup ────────────────────────────────────────────────────────────
keyboard = KMKKeyboard()
keyboard.extensions.append(MediaKeys())

# Matrix pins — 2 rows x 3 cols
keyboard.col_pins = (board.D0, board.D1, board.D2)
keyboard.row_pins = (board.D3, board.D4)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

# ── Encoder ───────────────────────────────────────────────────────────────────
encoder_handler = EncoderHandler()
encoder_handler.pins = ((board.D7, board.D8, board.D6, False),)
# D7 = CLK (A), D8 = DT (B), D6 = push button, False = not inverted
keyboard.modules.append(encoder_handler)

# ── Snipping Tool macro (Win+Shift+S) ─────────────────────────────────────────
SNIP = KC.LGUI(KC.LSFT(KC.S))

# ── Mute toggle key (encoder click) ───────────────────────────────────────────
# We use a custom key that also flips our OLED state
def mute_press(key, keyboard, *args):
    global is_muted
    is_muted = not is_muted
    update_oled()
    # Also send the real OS mute keycode
    keyboard.tap_key(KC.MUTE)

ENC_MUTE = KC.make_key(on_press=mute_press)

# ── Keymap ────────────────────────────────────────────────────────────────────
#
#   [ PREV ] [ PLAY ] [ NEXT ]
#   [ COPY ] [PASTE ] [ SNIP ]
#                               Encoder: CW=Vol Up | CCW=Vol Down | Click=Mute
#
keyboard.keymap = [
    [
        KC.MPRV,   KC.MPLY,   KC.MNXT,   # Row 0: Prev | Play/Pause | Next
        KC.LCTL(KC.C), KC.LCTL(KC.V), SNIP,  # Row 1: Copy | Paste | Snip
    ]
]

# ── Encoder map ───────────────────────────────────────────────────────────────
# Format: ((CW_key, CCW_key, click_key), ...)  per layer
encoder_handler.map = [
    ((KC.VOLU, KC.VOLD, ENC_MUTE),),  # Layer 0
]

# ── Encoder vol tracking hook ─────────────────────────────────────────────────
# Wrap the encoder handler to also update our display counter
_orig_encoder = encoder_handler.during_bootup

def _on_encoder(key, keyboard, *args):
    global vol_level, is_muted
    if key == KC.VOLU:
        if vol_level < 100:
            vol_level += 1
        if is_muted:               # turning up while muted = unmute
            is_muted = False
    elif key == KC.VOLD:
        if vol_level > 0:
            vol_level -= 1
    update_oled()

# Patch volume keys to also update OLED
KC.VOLU.before_press_handler(_on_encoder)
KC.VOLD.before_press_handler(_on_encoder)

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    keyboard.go()
