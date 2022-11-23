# Pixels4Nibbles
is an r/place clone that incentivizes people to donate food to food drives. 

## Hardware requirements
This project utilizes a Raspberry Pi, a display, and a mouse placed in a public location. The Raspberry Pi should be equipped with a [HC-SR04 ultrasonic distance sensor](https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/), which is to be attached to a food acceptance container. 

## Software requirements
All software requirements are included by default in the [Raspberry Pi OS](https://www.raspberrypi.com/software/}. 

## How it works
When a person donates food, they place the food item in a chute with an ultrasonic sensor that sees the food item pass by. The program responds to this donation by rewarding the user with a number of pixels which they are allowed to place on a shared pixel art board. 

## Credits
* [r/place](https://www.reddit.com/r/place/) for the inspiration and color palette
* This project would not be possible were it not for open-source projects such as Python and TKinter

This project was created for the Skyline High School Technology Student Association's 2022 community service project.

### Licensed under the MIT License
