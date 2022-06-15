import atexit
import ctypes as ct
import sys
from multiprocessing import Process, Event, Pipe, Value, Array

import numpy as np
import serial

from .sensor import ReSkinBase, ReSkinData, ReSkinDummy


class ReSkinProcess(Process):
    """
    Process to keep ReSkin datastream running in the background.

    Attributes
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
    temp_filtered: bool
        Flag indicating if temperature readings should be filtered from
        the output
    allow_dummy_sensor: bool
        Flag to instantiate a dummy sensor if a real sensor with the specified
        configurations is unavailable
    chunk_size : int
        Quantum of data piped from buffer at one time.

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

    def __init__(
        self,
        num_mags: int = 1,
        port: str = None,
        baudrate: int = 115200,
        burst_mode: bool = True,
        device_id: int = -1,
        temp_filtered: bool = False,
        reskin_data_struct: bool = True,
        allow_dummy_sensor: bool = False,
        chunk_size: int = 10000,
    ):
        """Initializes a ReSkinProcess object."""
        super(ReSkinProcess, self).__init__()
        self.num_mags = num_mags
        self.port = port
        self.baudrate = baudrate
        self.burst_mode = burst_mode
        self.device_id = device_id
        self.temp_filtered = temp_filtered
        self.reskin_data_struct = reskin_data_struct
        self.allow_dummy_sensor = allow_dummy_sensor

        self._pipe_in, self._pipe_out = Pipe()
        self._sample_cnt = Value(ct.c_uint64)
        self._buffer_size = Value(ct.c_uint64)

        self._last_time = Value(ct.c_double)
        self._last_delay = Value(ct.c_double)
        self._last_reading = Array(ct.c_float, self.num_mags * 4)

        self._chunk_size = chunk_size

        self._event_is_streaming = Event()
        self._event_quit_request = Event()
        self._event_sending_data = Event()

        self._event_is_buffering = Event()

        atexit.register(self.join)

    @property
    def last_reading(self):
        if self.reskin_data_struct:
            return ReSkinData(
                time=self._last_time.value,
                acq_delay=self._last_delay.value,
                data=self._last_reading[:],
                dev_id=self.device_id,
            )
        else:
            return np.concatenate(
                (
                    [self._last_time.value],
                    [self._last_delay.value],
                    self._last_reading[:],
                    [self.device_id],
                )
            )
        # return self._last_reading

    @property
    def sample_cnt(self):
        return self._sample_cnt.value

    def start_streaming(self):
        """Start streaming data from ReSkin sensor"""
        if not self._event_quit_request.is_set():
            self._event_is_streaming.set()
            print("Started streaming")

    def start_buffering(self, overwrite: bool = False):
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
                print("Warning: Overwriting non-empty buffer")
                self.get_buffer()
            self._event_is_buffering.set()
        else:
            # Warn that data is already buffering
            print("Warning: Data is already buffering")

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
        if num_samples <= 0:
            return samples
        last_cnt = self._sample_cnt.value
        samples = [self.last_reading]
        while len(samples) < num_samples:
            if not self._event_is_streaming.is_set():
                print("Please start streaming first.")
                return []
            # print(self._sample_cnt.value)
            if last_cnt == self._sample_cnt.value:
                continue
            last_cnt = self._sample_cnt.value
            samples.append(self.last_reading)

        return samples

    def get_buffer(self, timeout: float = 1.0, pause_if_buffering: bool = False):
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
                print(
                    "Cannot get buffer while data is buffering. Set "
                    "pause_if_buffering=True to pause buffering and "
                    "retrieve buffer"
                )
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
                num_mags=self.num_mags,
                port=self.port,
                baudrate=self.baudrate,
                burst_mode=self.burst_mode,
                device_id=self.device_id,
                temp_filtered=self.temp_filtered,
                reskin_data_struct=True,
            )
            # self.sensor._initialize()
            self.start_streaming()
        except (serial.serialutil.SerialException, AttributeError) as e:
            print("ERROR: ", e)
            if self.allow_dummy_sensor:
                print("Using dummy sensor")
                self.sensor = ReSkinDummy(
                    num_mags=self.num_mags,
                    port=self.port,
                    baudrate=self.baudrate,
                    burst_mode=self.burst_mode,
                    device_id=self.device_id,
                    temp_filtered=self.temp_filtered,
                    reskin_data_struct=True,
                )
                self.start_streaming()
            else:
                sys.exit(-1)

        is_streaming = False
        while not self._event_quit_request.is_set():
            if self._event_is_streaming.is_set():
                if not is_streaming:
                    is_streaming = True
                    # Any logging or stuff you want to do when streaming has
                    # just started should go here
                (
                    self._last_time.value,
                    self._last_delay.value,
                    self._last_reading[:],
                ) = self.sensor.get_sample()

                self._sample_cnt.value += 1

                if self._event_is_buffering.is_set():
                    buffer.append(self.last_reading)
                    self._buffer_size.value = len(buffer)
                elif self._buffer_size.value > 0:
                    self._event_sending_data.set()
                    chk = self._chunk_size
                    while len(buffer) > 0:
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
                    while len(buffer) > 0:
                        if chk > len(buffer):
                            chk = len(buffer)
                        self._pipe_out.send(buffer[0:chk])
                        buffer[0:chk] = []
                        self._buffer_size.value = len(buffer)

        self.pause_streaming()
