import os
import sys
import time
import collections

import numpy as np
import serial
import struct

ReSkinSettings = collections.namedtuple('ReSkinSettings',
    'num_mags port baudrate burst_mode device_id')

ReSkinData = collections.namedtuple('ReSkinData',
    'time, acq_delay, data, dev_id')

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
    def __init__(self, num_mags:int = 1, port: str = None, baudrate: int = 115200, 
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
            Sensor ID; mostly useful when using multiple sensors simultaneously
        """
        super(ReSkinBase, self).__init__(port=port, baudrate=baudrate)
        
        self.num_mags = num_mags
        self.port = port
        self.baudrate = baudrate
        self.burst_mode = burst_mode
        self.device_id = device_id
        
        self._msg_floats = 4*num_mags
        self._msg_length = 4*self._msg_floats + 2

        self._initialize()

    def _initialize(self):
        """
        Opens the serial port for communication with sensor
        """
        self.flush()
        print("Initializing sensor...")
        try:
            self.get_sample()
            print('Initialization successful')
        except:
            print('Initialization failed. Please disconnect and reconnect sensor.')

    def get_data(self, num_samples):
        """
        Collects requisite number of samples from the sensor

        Parameters
        ----------
        num_samples: int
            Number of samples of data to be collected.
        """
        data = []
        for _ in range(num_samples):
            t, acqd, sample = self.get_sample()
            data.append(ReSkinData(
                time=t,
                acq_delay=acqd,
                data=sample,
                dev_id=self.device_id
            ))
        
        return data

    def get_sample(self, num_samples=1):
        """
        Collects requisite bytes of data from the serial communication
        channel
        
        """
        # Just to make sure we're not reading in gibberish. Filling up the input
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
        
        while True:
            if self.in_waiting > self._msg_length:
                collect_start = time.time()
                if self.burst_mode:
                    zero_bytes = self.read(self._msg_length)
                    if zero_bytes[-2:] != b'\r\n':
                        zero_bytes = self.read_until(b'\r\n')
                        continue
                    decoded_zero_bytes = struct.unpack(
                        '@{}fcc'.format(self._msg_floats), zero_bytes)[:self._msg_floats]
                    
                else:
                    zero_bytes = self.readline()
                    decoded_zero_bytes = zero_bytes.decode('utf-8')
                    decoded_zero_bytes = decoded_zero_bytes.strip()
                    decoded_zero_bytes = [float(x) for x in decoded_zero_bytes.split()]
                
                acq_delay = time.time() - collect_start
                return collect_start, acq_delay, decoded_zero_bytes

            else:
                # Need checks to timeout if required
                pass
        
# if __name__ == '__main__':
#     test = ReSkinBase(5, port="COM32", baudrate=115200)