import atexit
import sys
import ctypes as ct
from multiprocessing import Process, Event, Pipe, Value, Array

import serial

from .sensor import ReSkinBase, ReSkinSettings, ReSkinData

class ReSkinProcess(Process):
    """
    ReSkin Sensor process. Keeps datastream running in the background. 
    
    Attributes
    ----------
    sensor : ReSkinSettings
        SensorSettings object
    _pipe_in, _pipe_out : Pipe
        Two ends of a pipe for communicating with the sensor
    _sample_cnt : int
        ID samples and keep count to ensure unique samples are passed to querying 
        process
    
    Methods
    -------
    start_streaming():
        Start streaming data from ReSkin sensor
    start_buffering(overwrite=False):
        Start buffering ReSkin data. Call is ignored if already buffering
    pause_buffering():
        Stop buffering ReSkin data
    pause_streaming():
        Stop streaming data from ReSkin sensor
    get_data(num_samples=5):
        Return a specified number of samples from the ReSkin Sensor
    get_buffer(timeout=1.0, pause_if_buffering=False):
        Return the recorded buffer
    """

    def __init__(self,sensor_settings:ReSkinSettings, 
        chunk_size:int=10000):
        """
        Parameters
        ----------
        sensor_settings : ReSkinSettings
            Named tuple containing settings for ReSkin sensor
        
        chunk_size : int
            Quantum of data piped from buffer at one time.
        """
        super(ReSkinProcess, self).__init__()
        self.device_id = sensor_settings.device_id

        self._pipe_in, self._pipe_out = Pipe()
        self._sample_cnt = Value(ct.c_uint64)
        self._buffer_size = Value(ct.c_uint64)
        
        self._last_time = Value(ct.c_double)
        self._last_delay = Value(ct.c_double)
        self._last_reading = Array(ct.c_float, sensor_settings.num_mags * 4)

        self.sensor_settings = sensor_settings

        self._chunk_size = chunk_size

        self._event_is_streaming = Event()
        self._event_quit_request = Event()
        self._event_sending_data = Event()

        self._event_is_buffering = Event()

        atexit.register(self.join)
        
    
    @property
    def last_reading(self):
        return ReSkinData(
            time = self._last_time.value,
            acq_delay=self._last_delay.value,
            data = self._last_reading[:],
            dev_id=self.device_id)
        # return self._last_reading
    
    @property
    def sample_cnt(self):
        return self._sample_cnt.value

    def start_streaming(self):
        """Start streaming data from ReSkin sensor"""
        if not self._event_quit_request.is_set():
            self._event_is_streaming.set()
            print('Started streaming')

    def start_buffering(self, overwrite:bool=False):
        """
        Start buffering ReSkin data. Call is ignored if already buffering

        Parameters
        ----------
        overwrite : bool
            Existing buffer is overwritten if true; appended if false. Ignored
            if data is already buffering
        """

        if not self._event_is_buffering.is_set():
            if overwrite:
                # Warn that buffer is about to be overwritten
                print('Warning: Overwriting non-empty buffer')
                self.get_buffer()
            self._event_is_buffering.set()
        else:
            # Warn that data is already buffering
            print('Warning: Data is already buffering')

    def pause_buffering(self):
        """Stop buffering ReSkin data"""
        self._event_is_buffering.clear()

    def pause_streaming(self):
        """Stop streaming data from ReSkin sensor"""
        self._event_is_streaming.clear()

    def get_data(self, num_samples=5):
        """
        Return a specified number of samples from the ReSkin Sensor
        
        Parameters
        ----------
        num_samples : int
            Number of samples required
        """
        # Only sends samples if streaming is on. Sends empty list otherwise.

        samples = []
        if num_samples <=0:
            return samples
        last_cnt = self._sample_cnt.value
        samples = [self.last_reading]
        while len(samples) < num_samples:
            if not self._event_is_streaming.is_set():
                print('Please start streaming first.')
                return []
            # print(self._sample_cnt.value)
            if last_cnt == self._sample_cnt.value:
                continue
            last_cnt = self._sample_cnt.value
            samples.append(self.last_reading)
        
        return samples

    def get_buffer(self, timeout:float=1.0, pause_if_buffering:bool=False):
        """
        Return the recorded buffer
        
        Parameters
        ----------
        timeout : int
            Time to wait for data to start getting piped.
        
        pause_if_buffering : bool
            Pauses buffering if still running, and then collects and returns buffer
        """
        # Check if buffering is paused
        if self._event_is_buffering.is_set():
            if not pause_if_buffering:
                print('Cannot get buffer while data is buffering. Set pause_if_buffering=True to pause buffering and retrieve buffer')
                return
            else:
                self._event_is_buffering.clear()
        rtn = []
        if self._event_sending_data.is_set() or self._buffer_size.value > 0:
            self._event_sending_data.wait(timeout=timeout)
            while self._pipe_in.poll() or self._buffer_size.value > 0:
                rtn.extend(self._pipe_in.recv())
            self._event_sending_data.clear()
        
        return rtn

    def join(self, timeout=None):
        """Clean up before exiting"""
        self._event_quit_request.set()
        self.pause_buffering()
        self.pause_streaming()

        super(ReSkinProcess, self).join(timeout)
    
    def run(self):
        """This loop runs until it's asked to quit."""
        buffer = []
        # Initialize sensor
        try:
            self.sensor = ReSkinBase(
                num_mags=self.sensor_settings.num_mags,
                port=self.sensor_settings.port,
                baudrate=self.sensor_settings.baudrate,
                burst_mode=self.sensor_settings.burst_mode,
                device_id=self.sensor_settings.device_id)
            # self.sensor._initialize()
            self.start_streaming()
        except serial.serialutil.SerialException as e:
            self._event_quit_request.set()
            print('ERROR: ', e)
            sys.exit(1)

        is_streaming = False
        while not self._event_quit_request.is_set():
            if self._event_is_streaming.is_set():
                if not is_streaming:
                    is_streaming = True
                    # Any logging or stuff you want to do when streaming has
                    # just started should go here
                self._last_time.value, self._last_delay.value, \
                    self._last_reading[:] = self.sensor.get_sample()

                self._sample_cnt.value += 1

                if self._event_is_buffering.is_set():
                    buffer.append(self.last_reading)
                    self._buffer_size.value = len(buffer)
                elif self._buffer_size.value > 0:
                    self._event_sending_data.set()
                    chk = self._chunk_size
                    while len(buffer)>0:
                        if chk > len(buffer):
                            chk = len(buffer)
                        self._pipe_out.send(buffer[0:chk])
                        buffer[0:chk] = []
                        self._buffer_size.value = len(buffer)
                    
            else:
                if is_streaming:
                    is_streaming = False
                    # Logging when streaming just stopped

                if self._buffer_size.value > 0:
                    self._event_sending_data.set()
                    chk = self._chunk_size
                    while len(buffer)>0:
                        if chk > len(buffer):
                            chk = len(buffer)
                        self._pipe_out.send(buffer[0:chk])
                        buffer[0:chk] = []
                        self._buffer_size.value = len(buffer)
        
        self.pause_streaming()

if __name__ == '__main__':
    test_settings = ReSkinSettings(
        num_mags=5,
        port="COM32",
        baudrate=115200,
        burst_mode=True,
        device_id=1
    )
    # test_sensor = ReSkinBase(5, port="COM32", baudrate=115200)
    test_proc = ReSkinProcess(test_settings, pipe_buffer_on_pause=True)
    test_proc.start()
    

    test_proc.start_streaming()
    test_proc.start_buffering()
    import time
    time.sleep(2.0)
    test_proc.pause_buffering()

    print(len(test_proc.get_buffer()))
    # print(test_proc.get_samples(100))
    test_proc.pause_streaming()
    
    # buf = test_proc.get_buffer()
    # print('Buffer length: ', len(buf))
    # print('Sample buffer element (last one): ', buf[-1])
    # print('Last reading: ', test_proc.last_reading)
    
    while True:
        input('')