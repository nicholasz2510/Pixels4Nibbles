import tkinter as tk
import math
import pickle
import os
import threading
import time
import configparser
import RPi.GPIO as GPIO
from pygame import mixer

os.system("cls" if os.name == "nt" else "clear")

config = configparser.ConfigParser()
config.read("config.ini")
user_config = config["Pixels4Nibbles"]
PX_PER_FOOD = int(user_config["PxPerFood"])
VERT_RES = int(user_config["VertRes"])
HORZ_RES = int(user_config["HorzRes"])
SENSOR_TIMING = float(user_config["SensorTiming"])
ITEM_COOLDOWN = float(user_config["ItemCooldown"])
CALIBRATION_IDLE_TIME = float(user_config["CalibrationIdleTime"])

color_palette = ["#FFFFFF", "#E4E4E4", "#888888", "#222222", "#FFA7D1", "#E50000", "#E59500", "#A06A42", "#E5D900",
                 "#94E044", "#02BE01", "#00D3DD", "#0083C7", "#0000EA", "#CF6EE4", "#820080"]
color_buttons = []
curr_color = 0

pixels_remaining = 0

board_state = [[color_palette[curr_color] for col in range(HORZ_RES)] for row in range(VERT_RES)]

should_recalibrate_sensor = input("Recalibrate sensor? (y/n) ").strip().lower()[0] == "y"
if not os.path.exists("history/history.pkl") or input("Reset history? (y/n) ").strip().lower()[0] == "y":
    open("history/history.pkl", "w").close()
else:
    with open("history/history.pkl", "rb") as f:
        try:
            while True:
                board_state = pickle.load(f)
        except EOFError:
            pass


def update_history():
    with open("history/history.pkl", "ab+") as pf:
        pickle.dump(board_state, pf)


mixer.init()
kaching_sound = mixer.Sound("assets/cash-register-sound.ogg")
click_sound = mixer.Sound("assets/click.ogg")

window = tk.Tk()
window.attributes("-fullscreen", True)
window.title("Pixels4Nibbles")

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
count_label = tk.Label(count_frame, text=pixels_remaining, font="Helvetica 96")
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


def get_cell_coord(x, y):
    coord_x = math.floor(x / px_size)
    coord_y = math.floor(y / px_size)
    return coord_x, coord_y


def get_outline_px(cell_x, cell_y):
    x0, y0 = cell_x * px_size, cell_y * px_size
    return x0, y0, x0 + px_size, y0 + px_size


def redraw_outline(cell_x, cell_y):
    global selection_outline
    drawing_canvas.delete(selection_outline)
    box = get_outline_px(cell_x, cell_y)
    selection_outline = drawing_canvas.create_rectangle(box[0], box[1], box[2], box[3], outline="#000000")


def moved(event):
    if not pixels_remaining:
        return
    cell_coord = get_cell_coord(event.x, event.y)
    redraw_outline(cell_coord[0], cell_coord[1])


def draw(cell_x, cell_y):
    box = get_outline_px(cell_x, cell_y)
    drawing_canvas.create_rectangle(box[0], box[1], box[2], box[3], outline="", fill=color_palette[curr_color])


def user_draw(event):
    if not pixels_remaining:
        return
    cell_coord = get_cell_coord(event.x, event.y)
    if board_state[cell_coord[1]][cell_coord[0]] == color_palette[curr_color]:
        return
    draw(cell_coord[0], cell_coord[1])
    click_sound.play()
    board_state[cell_coord[1]][cell_coord[0]] = color_palette[curr_color]
    update_history()
    redraw_outline(cell_coord[0], cell_coord[1])
    decrement_pixels_remaining()


def sensed(_event):
    increment_pixels_remaining()
    kaching_sound.play()


def sensor_activate():
    window.event_generate("<<sensed>>", when="tail")


drawing_canvas.bind("<Motion>", moved)
drawing_canvas.bind("<Button-1>", user_draw)

window.bind("<<sensed>>", sensed)
window.bind("<space>", sensed)  # mock with space bar for sensor detecting food

for row in range(HORZ_RES):
    for col in range(VERT_RES):
        curr_color = color_palette.index(board_state[col][row])
        draw(row, col)
curr_color = 0

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

calibration_config = config["Calibration"]


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


def run_sensor():
    dist_threshold = float(calibration_config["Threshold"])
    if should_recalibrate_sensor:
        print("Measuring distance without items... ")
        sum_dists = 0
        for i in range(int(CALIBRATION_IDLE_TIME / SENSOR_TIMING)):
            sum_dists += distance()
            time.sleep(SENSOR_TIMING)
        avg_dist = sum_dists / int(CALIBRATION_IDLE_TIME / SENSOR_TIMING)
        print("Average Measured Distance: %.1f cm" % avg_dist)

        result = None
        dists = []

        def calibrating_threshold():
            while result is None:
                dists.append(distance())
                time.sleep(SENSOR_TIMING)

        calibrate_thread = threading.Thread(target=calibrating_threshold)
        calibrate_thread.start()
        result = input("Please insert a calibration item. Once you are done, press [Enter] ")
        dist_threshold = min(dists) + ((avg_dist - min(dists)) / 2)
        print("Threshold: %.1f cm" % dist_threshold)
        calibration_config["Threshold"] = str(dist_threshold)

        with open("config.ini", "w") as cf:
            config.write(cf)

    while True:
        dist = distance()
        if dist < dist_threshold:
            sensor_activate()
            time.sleep(ITEM_COOLDOWN - SENSOR_TIMING)
        time.sleep(SENSOR_TIMING)


thread = threading.Thread(target=run_sensor)
thread.daemon = True
thread.start()

window.mainloop()
