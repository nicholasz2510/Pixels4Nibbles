# Pixels4Nibbles
is an r/place clone that incentivizes people to donate food to food drives. 

fun fact: [`get_timelapse.py`](https://github.com/nicholasz2510/Pixels4Nibbles/blob/main/src/get_timelapse.py) was completely written by ChatGPT. humans are obsolete.

## How it works
When a person donates food, they place the food item in a chute equipped with an ultrasonic sensor that sees the food item pass by. The program responds to this donation by rewarding the user with a number of pixels which they are then allowed to place on a shared pixel art board. 

To obtain a timelapse of the full history of your pixel art board, you may run `get_timelapse.py`. The finished product will appear in `src` as `output.mp4`. 

## Hardware requirements
This project utilizes a Raspberry Pi, a display, and a mouse placed in a public location. The Raspberry Pi should be equipped with a [HC-SR04 ultrasonic distance sensor](https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/), which is to be attached to a food acceptance container. 

## Software requirements
All software requirements are included by default in the [Raspberry Pi OS](https://www.raspberrypi.com/software/). 

## Credits
* [r/place](https://www.reddit.com/r/place/) for the inspiration and color palette
* This project would not be possible were it not for open-source projects such as Python and Tkinter

Pixels4Nibbles was created by [Nick Zhang](https://github.com/nicholasz2510) for the Skyline High School Technology Student Association's 2022 community service project.

### Licensed under the MIT License
