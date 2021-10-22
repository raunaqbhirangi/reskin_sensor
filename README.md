# Reskin Sensor Library
This is a python library to interface with [ReSkin](https://openreview.net/forum?id=87_OJU4sw3V) sensors.

## Installation

1. Clone this repository using 
```
$ git clone https://github.com/raunaqbhirangi/reskin_sensor.git
```
2. Install dependencies from `requirements.txt`
```
$ pip install -r requirements.txt
```

3. Install this package using
```
$ pip install -e .
```
## Usage

1. Connect the 5X board to the microcontroller. 

2. Connect the microcontroller (we recommend the Adafruit Trinket M0 or the Adafruit QT PY) to the computer using a suitable USB cable

3. Use the [Arduino IDE](https://www.arduino.cc/en/software) to upload code to a microcontroller.
If you get a `can't open device "<port-name>": Permission denied` error, modify permissions to allow read and write on that port. On Linux, you would look like `sudo chmod a+rw <port-name>`

4. Run test code on the computer
```
$ python tests/sensor_proc_test.py -p <port-name>
```