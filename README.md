# Reskin Sensor Library
This is a python library to interface with [ReSkin](https://openreview.net/forum?id=87_OJU4sw3V) sensors. We provide two classes for interfacing with [ReSkin](https://openreview.net/forum?id=87_OJU4sw3V). The `ReSkinBase` class is good for standalone data collection: it blocks code execution while data is being collected. The `ReSkinProcess` class can be used for non-blocking background data collection. Data can be buffered in the background while you run the rest of your code.  

## Installation

This package can be installed using pip:
```
pip install reskin_sensor
```
Alternatively,
1. Clone this repository using 
```
$ git clone https://github.com/raunaqbhirangi/reskin_sensor.git --recursive
```
2. Install this package using
```
$ pip install -e .
```
## Usage

1. Connect the 5X board to the microcontroller. 

2. Connect the microcontroller (we recommend the Adafruit Trinket M0 or the Adafruit QT PY) to the computer using a suitable USB cable

3. Use the [Arduino IDE](https://www.arduino.cc/en/software) to upload code to a microcontroller. The code as well as upload instructions can be found in the [arduino](./arduino) folder.
If you get a `can't open device "<port-name>": Permission denied` error, modify permissions to allow read and write on that port. On Linux, this would look like 
```
$ sudo chmod a+rw <port-name>
```

4. Run test code on the computer
```
$ python tests/sensor_proc_test.py -p <port-name>
```
## Credits
This package is maintained by [Raunaq Bhirangi](https://www.cs.cmu.edu/~rbhirang/). We would also like to cite the [pyForceDAQ](https://github.com/lindemann09/pyForceDAQ) library which was used as a reference in structuring this package.
