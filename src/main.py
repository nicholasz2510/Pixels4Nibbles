import tkinter as tk
import math
import threading
import RPi.GPIO as GPIO
import time

PX_PER_FOOD = 8
VERT_RES = 64
HORZ_RES = 96

color_palette = ["#FFFFFF", "#E4E4E4", "#888888", "#222222", "#FFA7D1", "#E50000", "#E59500", "#A06A42", "#E5D900",
                 "#94E044", "#02BE01", "#00D3DD", "#0083C7", "#0000EA", "#CF6EE4", "#820080"]
color_buttons = []
curr_color = 0

pixels_remaining = 0

window = tk.Tk()
window.attributes('-fullscreen', True)
window.title("Food for Pixels")

height = window.winfo_screenheight()
screen_width = window.winfo_screenwidth()
canvas_width = height * (HORZ_RES / VERT_RES)
palette_height = screen_width - canvas_width
palette_width = screen_width - canvas_width
px_size = height / VERT_RES
window.config(cursor="none")

palette_canvas = tk.Canvas(bd=0, highlightthickness=0, height=palette_height,
                           width=palette_width)
palette_canvas.place(x=canvas_width, y=0)
palette_button_margin = 3
palette_button_size = (palette_width / 4) - (2 * palette_button_margin)
curr_x = palette_button_margin
curr_y = palette_button_margin
for color in color_palette:
    color_buttons.append(
        palette_canvas.create_rectangle(curr_x, curr_y, curr_x + palette_button_size, curr_y + palette_button_size,
                                        outline="", fill=color, width=5))
    curr_x = (curr_x + (palette_width / 4)) % palette_width
    if curr_x == palette_button_margin:
        curr_y = (curr_y + (palette_width / 4)) % palette_width

palette_canvas.itemconfig(color_buttons[0], outline="black")


def choose_color(event):
    if not pixels_remaining:
        return
    global curr_color
    curr_color = (math.floor(event.y / (palette_width / 4)) * 4) + math.floor(event.x / (palette_width / 4))
    window.config(cursor="dot " + color_palette[curr_color])
    for color_i in range(len(color_palette)):
        if color_i == curr_color:
            palette_canvas.itemconfig(color_buttons[color_i], outline="black")
        else:
            palette_canvas.itemconfig(color_buttons[color_i], outline="")


palette_canvas.bind("<Button-1>", choose_color)

count_frame = tk.Frame(window, bd=0, highlightthickness=0, height=height - palette_height, width=palette_width)
count_frame.place(x=canvas_width, y=palette_height)
tk.Label(count_frame, text="Pixels remaining: ", font="Helvetica 18").place(x=palette_width / 2, y=550, anchor="center")
count_label = tk.Label(count_frame, text=pixels_remaining, font='Helvetica 96')
count_label.place(x=palette_width / 2, y=650, anchor="center")

drawing_canvas = tk.Canvas(bd=0, highlightthickness=0, height=height, width=canvas_width, bg="white")
drawing_canvas.place(x=0, y=0)

selection_outline = None


def decrement_pixels_remaining():
    global pixels_remaining
    pixels_remaining -= 1
    count_label["text"] = pixels_remaining
    if not pixels_remaining:
        window.config(cursor="none")
        global selection_outline
        drawing_canvas.delete(selection_outline)


def increment_pixels_remaining():
    global pixels_remaining
    if not pixels_remaining:
        window.config(cursor="dot " + color_palette[curr_color])
    pixels_remaining += PX_PER_FOOD
    count_label["text"] = pixels_remaining


def get_outline_px(x, y):
    x0 = math.floor(x / px_size) * px_size
    y0 = math.floor(y / px_size) * px_size
    return x0, y0, x0 + px_size, y0 + px_size


def redraw_outline(box):
    global selection_outline
    drawing_canvas.delete(selection_outline)
    selection_outline = drawing_canvas.create_rectangle(box[0], box[1], box[2], box[3], outline="#000000")


def moved(event):
    if not pixels_remaining:
        return
    box = get_outline_px(event.x, event.y)
    redraw_outline(box)


def draw(event):
    if not pixels_remaining:
        return
    box = get_outline_px(event.x, event.y)
    drawing_canvas.create_rectangle(box[0], box[1], box[2], box[3], outline="", fill=color_palette[curr_color])
    redraw_outline(box)
    decrement_pixels_remaining()


def sensed(_event):
    increment_pixels_remaining()


drawing_canvas.bind("<Motion>", moved)
drawing_canvas.bind("<Button-1>", draw)

# window.bind("<space>", sensed)  # mock with space bar for sensor detecting food


GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


def distance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    TimeElapsed = StopTime - StartTime
    return (TimeElapsed * 34300) / 2  # multiply with speed of sound (34300 cm/s), divide by 2 (there and back)


def run_tk():
    while True:
        dist = distance()
        print("Measured Distance = %.1f cm" % dist)
        time.sleep(0.05)


thread = threading.Thread(target=run_tk)
thread.daemon = True
thread.start()

window.mainloop()