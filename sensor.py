import os
import sys
import time
import collections

import numpy as np
import serial
import struct

from sensor_types import ReSkinData

ReSkinSettings = collections.namedtuple('ReSkinSettings',
    'num_mags port baudrate burst_mode device_id')

class ReSkinBase(serial.Serial):
    """
    Base class for a ReSkin sensor.

    Attributes
    ----------

    Methods
    -------
    get_data(num_samples)
        Collects num_samples samples from sensor
    """
    def __init__(self, num_mags:int = 1, port: str = None, baudrate: int = 9600, 
        burst_mode:bool = True, device_id=-1) -> None:
        """
        Parameters
        ----------
        num_mags: int
            Number of magnetometers connected to the sensor
        port : str
            System port that the sensor is connected to
        baudrate: int
            Baudrate at which data is transmitted by sensor
        burst_mode: bool
            Flag for whether sensor is using burst mode
        device_id: int
            Sensor ID
        """
        super(ReSkinBase, self).__init__(port=port, baudrate=baudrate)
        
        self.num_mags = num_mags
        self.port = port
        self.baudrate = baudrate
        self.burst_mode = burst_mode
        self.device_id = device_id
        
        self._msg_floats = 4*num_mags
        self._msg_length = 4*self._msg_floats + 2

    def _initialize(self):
        """
        Opens the serial port for communication with sensor
        """
        self.flush()
        print("Initializing sensor")
        test_data = self.get_data(1)
        print('got 1 datapoint')
        print(' '.join('{:.2f}'.format(x) for x in test_data[0].data))
        return

    def get_data(self, num_samples=1):
        """
        Collects requisite bytes of data from the serial communication
        channel

        Parameters
        ----------
        num_samples: int
            Number of samples of data to be collected.
        """
        # Hack to make sure we're not reading in gibberish. Filling up the input
        # buffer causes serial read to give out stale data. Resetting input buffer
        # can occasionally result gibberish coming in. Must ensure that that does
        # not happen
        
        if self.in_waiting > 4000:
            self.reset_input_buffer()
            while True:
                # if self.in_waiting >=115:
                if self.in_waiting >self._msg_length:
                    if self.read(self._msg_length)[-2:] == b'\r\n':
                        break
                    self.reset_input_buffer()
        
        data = []

        while len(data) < num_samples:
            if self.in_waiting > self._msg_length:
                collect_start = time.time()
                if self.burst_mode:
                    zero_bytes = self.read(self._msg_length)
                    if zero_bytes[-2:] != b'\r\n':
                        zero_bytes = self.read_until(b'\r\n')
                        continue
                    # print(zero_bytes[-2:] == b'\r\n')
                    decoded_zero_bytes = struct.unpack(
                        '@{}fcc'.format(self._msg_floats), zero_bytes)[:self._msg_floats]
                    
                else:
                    zero_bytes = self.readline()
                    decoded_zero_bytes = zero_bytes.decode('utf-8')
                    decoded_zero_bytes = decoded_zero_bytes.strip()
                    decoded_zero_bytes = [float(x) for x in decoded_zero_bytes.split()]
                
                new_data = ReSkinData(time=collect_start,
                    acquisition_delay=time.time() - collect_start,
                    device_id=self.device_id, data=decoded_zero_bytes)
                data += [new_data]
            
            else:
                # Need checks to timeout if required
                pass
        
        return data

if __name__ == '__main__':
    test = ReSkinBase(5, port="COM32", baudrate=115200)