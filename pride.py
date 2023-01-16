"""
pride.py:
---------------------------

Display a wavey pride flag.

Buttons:
* A = Stop/Start animation
* B = Change flag type
* C = Step through animation

---------------------------

MIT License

Copyright (c) 2022 Douglas Bouttell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from picographics import PicoGraphics, DISPLAY_TUFTY_2040, PEN_P4
from pimoroni import Button
from machine import ADC, Pin
import gc
import time
import math
import qrcode

# Turn on the LUX diode and start reading the analogue value.
# We use this for screen brightness
lux_pwr = Pin(27, Pin.OUT)
lux_pwr.value(1)
lux = ADC(26)

# Initialize the screen. We are using the 4 bit colour mode
# since we can and 3:3:2 RGB was causing memory to run out :(
display = PicoGraphics(DISPLAY_TUFTY_2040, pen_type=PEN_P4)
WIDTH, HEIGHT = display.get_bounds()
display.set_font("bitmap6")
display.set_backlight(1.0)

# Buttons!
button_a = Button(7, invert=False)
button_b = Button(8, invert=False)
button_c = Button(9, invert=False)
button_up = Button(22, invert=False)
button_down = Button(6, invert=False)

# How many columns we want to split the flag into.
COLS = 12 
COL_WIDTH = WIDTH // COLS

# We want two cycles of the sin wave so a nice constant.
FOUR_PI = 12.566 

# Make it so that it moves less towards the "flag pole"
WEIGHTS = [0.0] + [min(1.0, (i / COLS) + 0.2) for i in range(COLS)]

# The flags we have
FLAGS = ["pan", "pride"]

def load_config(file_name = "config.json"):
    with open(file_name, "r") as f:
        import json
        config = json.load(f)

    if 'default_flag' in config:
        try:
            flag = FLAGS.index(config['default_flag'])
        except ValueError:
            flag = 0
    else:
        flag = 0
            
    title = config['title'] if 'title' in config else "Lorem"
    subtitle = config['subtitle'] if 'subtitle' in config else "Ipsum edit"
    
    code = qrcode.QRCode()
    code.set_text(config['qrcode'] if 'qrcode' in config else "https://example.com")
    
    return (flag, title, subtitle, code)

def frange(start, stop, step):
    x = start
    yield x
    while True:
        x += step
        yield x
        if x > stop:
            yield stop
            break
        
def draw_flag(tick: float, color_list: list[list[int]], height_per_strip: int):
    offset = tick / 200
    col_offsets = [
        int(15 * weight * (math.sin(offset + x)))
        for x, weight in zip(frange(0, FOUR_PI, FOUR_PI / (COLS + 1)), WEIGHTS)
    ]
    
    for row, colors in enumerate(color_list):
        for col in range(COLS):        
            p0 = (col * COL_WIDTH, (row * height_per_strip) + col_offsets[col] + 30)
            p1 = (p0[0] + COL_WIDTH, (row * height_per_strip) + col_offsets[col + 1] + 30)
            p2 = (p1[0], p1[1] + height_per_strip)
            p3 = (p0[0], p0[1] + height_per_strip)
            m = p0[1] - p1[1]
            if m < -2:
                display.set_pen(colors[1])
            else:  
                display.set_pen(colors[0])
                
            display.polygon([p0, p1, p2, p3])
            
def text_centered(text: str, x: int, y: int, scale: int = 1, shadow: int = 5):
    """
    Place some text with a "shadow"
    """
    display.set_font("bitmap8")
    text_width = display.measure_text(text, scale, 1)
    text_x, text_y = x - (text_width // 2), y - ( (8 * scale) // 2 )
    display.set_pen(0)
    display.text(text, text_x + shadow, text_y + shadow, scale = scale, spacing = 1)
    display.set_pen(1)
    display.text(text, text_x, text_y, scale = scale, spacing = 1)
    
def swap_pallette(mode):
    """
    Set up the pallette for the the flag and the light/dark
    pairs for the strips.
    """
    if mode == "pan":
        # pansexual pride flag
        display.set_palette([
            (0, 0, 0),       # 0 Black
            (255, 255, 255), # 1 White
            (226, 28, 208),  # 2 Magenta
            (181, 44, 169),  # 3 Magenta shade
            (255, 245, 39),  # 4 Yellow
            (218, 211, 58),  # 5 Yellow shade
            (42, 195, 255),  # 6 Cyan
            (55, 169, 214)   # 7 Cyan shade
        ])
        colors = [
            [2, 3], # Magenta
            [4, 5], # Yellow
            [6, 7]  # Cyan
        ]
        
    elif mode == "pride":
        # traditional pride flag
        display.set_palette([
            (0, 0, 0),       # 0 Black
            (255, 255, 255), # 1 White
            (234, 53, 53),   # 2 Red
            (202, 21, 21),   # 3 Red shade
            (234, 158, 53),  # 4 Orange
            (202, 127, 21),  # 5 Orange shade
            (234, 209, 53),  # 6 Yellow
            (202, 178, 21),  # 7 Yellow shade
            (53, 234, 56),   # 8 Green
            (21, 202, 25),   # 9 Green shade
            (24, 69, 166),   # 10 Blue
            (26, 61, 137),   # 11 Blue shade
            (115, 31, 179),  # 12 Purple 
            (98, 37, 144)    # 13 Purple shade
        ])
        colors = [
            [2, 3],   # Red
            [4, 5],   # Orange
            [6, 7],   # Yellow
            [8, 9],   # Green
            [10, 11], # Blue
            [12, 13]  # Purple
        ]
        
    # Return the list of colors and the height of a strip
    return (colors, 180 // len(colors))

def qr_code(code: QRCode, fg, bg, width: int = 200):
    w, h = code.get_size()
    dot_size = width // w
    # Place in the center of the screen
    left = (WIDTH // 2) - ((dot_size * w) // 2)
    top = (HEIGHT // 2) - ((dot_size * h) // 2)
    
    display.set_pen(fg)
    display.rectangle(left, top, dot_size * w, dot_size * h)
    display.set_pen(bg)
    for x in range(w):
        for y in range(h):
            if code.get_module(x, y):
                display.rectangle(left + x * dot_size, top + y * dot_size, dot_size, dot_size)

flag, name, subtitle, qr = load_config()
mode = "run"
prev = time.ticks_ms() - 1

strip_colors, strip_height = swap_pallette(FLAGS[flag])
show_fps = False
show_qr = False

gc.collect()
while True: # Main loop
    now = time.ticks_ms()
        
    if mode == "run":
        if button_a.read():
            mode = "pause"
            
    elif mode == "pause":
        if button_a.read():
            mode = "run"
        
    if button_up.read():
        flag  = flag + 1 if flag != len(FLAGS) - 1 else 0
        strip_colors, strip_height = swap_pallette(FLAGS[flag])
        
    if button_down.read():
        flag  = flag - 1 if flag != 0 else len(FLAGS) - 1 
        strip_colors, strip_height = swap_pallette(FLAGS[flag])
        
    if button_b.read():
        show_qr = not show_qr
        
    if button_c.read():
        show_fps = not show_fps
    
    if mode == "run":
        tick = time.ticks_ms()
        
    display.set_pen(0)
    display.clear()
    draw_flag(tick, strip_colors, strip_height)
    
    if show_qr:
        qr_code(qr, 1, 0)
    else:
        text_centered(name, WIDTH // 2, (HEIGHT // 2) - 10, 10)
        text_centered(subtitle, WIDTH // 2, (HEIGHT // 2) + 40, 3, 2)

    if show_fps:
        fps = 1000 // (now - prev)
        display.set_font("bitmap6")
        display.set_pen(1)
        display.text(str(fps) + " fps", 0, 0)
            
    prev = now
    display.update()
    
    light = min(0.5, lux.read_u16() / 7000)
    display.set_backlight(0.5 + light)

