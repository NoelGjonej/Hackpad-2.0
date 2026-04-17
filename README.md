# PCB Design

<img width="559" height="633" alt="image" src="https://github.com/user-attachments/assets/64dc467b-8703-41a9-a4d8-bcf424c18249" />

# Case Design

<img width="1191" height="690" alt="image" src="https://github.com/user-attachments/assets/8e54510b-2540-4599-8d92-5e13ac198888" />

# XIAO Macropad — KMK Firmware
## Seeeduino XIAO · 6 Keys · EC11E Rotary Encoder · SSD1306 128x32 OLED

---

## Why KMK instead of QMK?

KMK runs on **CircuitPython** — there is no compiling, no toolchain, no flashing.
You just copy files onto the XIAO like a USB drive. Much easier for the XIAO.

---

## Key Layout

```
[ PREV  ] [ PLAY  ] [ NEXT  ]
[ COPY  ] [ PASTE ] [ SNIP  ]
                              Encoder CW  → Volume Up
                              Encoder CCW → Volume Down
                              Encoder Click → Mute / Unmute
```

| Key | Action |
|-----|--------|
| Top-left  | ⏮ Previous Track |
| Top-mid   | ▶ Play / Pause |
| Top-right | ⏭ Next Track |
| Bot-left  | Ctrl+C — Copy |
| Bot-mid   | Ctrl+V — Paste |
| Bot-right | Win+Shift+S — Snipping Tool |
| Encoder CW | 🔊 Volume Up |
| Encoder CCW | 🔉 Volume Down |
| Encoder click | 🔇 Mute / Unmute toggle |

---

## Wiring

### Key Matrix (2 rows × 3 cols, COL2ROW diodes)

```
         COL0(D0)   COL1(D1)   COL2(D2)
ROW0(D3)   PREV       PLAY       NEXT
ROW1(D4)   COPY       PASTE      SNIP
```

Add a 1N4148 diode per switch — cathode (black band) toward the ROW pin.

### EC11E Encoder

| EC11E pin | XIAO pin | Function       |
|-----------|----------|----------------|
| CLK (A)   | D7       | Rotation A     |
| DT  (B)   | D8       | Rotation B     |
| SW        | D6       | Click = Mute   |
| GND       | GND      | Ground         |

Add 10kΩ pull-up resistors on CLK and DT to 3.3V if you get jitter.

### SSD1306 OLED (I2C, 128×32)

| OLED pin | XIAO pin      |
|----------|---------------|
| SDA      | D9  (SDA)     |
| SCL      | D10 (SCL)     |
| VCC      | 3.3V          |
| GND      | GND           |

Default I2C address is 0x3C. If your OLED doesn't appear, try 0x3D in code.py.

---

## Setup Instructions

### Step 1 — Install CircuitPython on the XIAO

1. Download the CircuitPython UF2 for Seeeduino XIAO from:
   https://circuitpython.org/board/seeeduino_xiao/
   (download the latest stable .uf2 file)

2. Double-tap the RST pin on the XIAO — a drive called **XIAO-BOOT** appears on your PC.

3. Drag and drop the `.uf2` file onto that drive.
   The XIAO reboots and a new drive called **CIRCUITPY** appears.

### Step 2 — Install CircuitPython libraries

Download the CircuitPython Library Bundle from:
https://circuitpython.org/libraries

Unzip it. From the `lib/` folder inside, copy these folders/files
into the `lib/` folder on your **CIRCUITPY** drive:

```
adafruit_displayio_ssd1306.mpy
adafruit_display_text/
adafruit_imageload/
kmk/                          ← get this from https://github.com/KMKfw/kmk_firmware
```

To get KMK, download the zip from https://github.com/KMKfw/kmk_firmware
and copy the `kmk/` folder onto CIRCUITPY/lib/.

### Step 3 — Copy your code

Copy these two files from this folder onto the root of **CIRCUITPY**:

```
boot.py   → CIRCUITPY/boot.py
code.py   → CIRCUITPY/code.py
```

Your CIRCUITPY drive should look like:
```
CIRCUITPY/
├── boot.py
├── code.py
└── lib/
    ├── kmk/
    ├── adafruit_displayio_ssd1306.mpy
    ├── adafruit_display_text/
    └── adafruit_imageload/
```

### Step 4 — Done

The XIAO reboots automatically when you save files. Your macropad is ready.
No compiling, no flashing tools needed.

---

## Making changes

To change a key, open `code.py` in any text editor, edit the `keyboard.keymap` list,
and save. The XIAO reboots and picks up the change in a few seconds.

Common keycodes:
```python
KC.LCTL(KC.Z)     # Ctrl+Z  (undo)
KC.LCTL(KC.S)     # Ctrl+S  (save)
KC.LGUI(KC.L)     # Win+L   (lock screen)
KC.PSCR           # Print Screen
KC.TAB, KC.ESC, KC.ENT, KC.BSPC
KC.F1 ... KC.F12
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| CIRCUITPY drive doesn't appear | Double-tap RST faster (within ~500ms) |
| Keys not working | Check diode direction — cathode (black band) toward row pin |
| Encoder jittery | Add 10kΩ pull-ups on CLK and DT to 3.3V |
| OLED blank | Check SDA/SCL wiring; try changing 0x3C to 0x3D in code.py |
| Error on boot | Connect to XIAO via serial (PuTTY / Thonny) to read the error message |

### Reading error messages (very useful for debugging)

Install **Thonny** (free Python IDE): https://thonny.org
Connect to the XIAO's serial port — it shows any Python errors live,
which makes debugging very easy.

---
