# Getting Started with Arduino for ReSkin

First, install Arduino IDE and the relevant board packages in order to upload code to your microcontroller.
  
We tested the following on [Trinket M0](https://www.adafruit.com/product/3500) and [QT Py](https://www.adafruit.com/product/4600) from Adafruit. 
  They have excellent tutorials for setting up these boards with your Arduino IDE. Follow [this one for the Trinket M0](https://learn.adafruit.com/adafruit-trinket-m0-circuitpython-arduino/arduino-ide-setup) and [this one for the QT Py](https://learn.adafruit.com/adafruit-qt-py/arduino-ide-setup). 
    
## Parts
    
We generally recommend the QT Py as it has an on-board Qwiic/STEMMA connector and USB-C connector, and does not require any soldering. Parts list for these two boards is as follows:
    
### Trinket M0
 - [Qwiic/STEMMA to breadboard cable](https://www.adafruit.com/product/4209)
 - micro-USB to USB-A cable
 - ReSkin circuit board
 
### Qt Py
 - [Qwiic/STEMMA cable](https://www.adafruit.com/product/4401)
 - USB-C to USB-A cable
 - ReSkin circuit board
 
## Installing Arduino Library (submodule)

The library for the magnetometers is included as a submodule of this repo. Install the submodule
```
git submodule update --init
```
Move this library into your local libraries folder for your Arduino installation.

## Finding your port (Linux)

Use the port in the tests/ as input to the -p argument. One of the simplest methods is to list all connected USB devices
```
lsusb
```
Then, connect your microcontroller and rerun the command. The new device between the two lists is your port.

