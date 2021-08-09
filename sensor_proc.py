import atexit
from multiprocessing import Process, Event, Pipe

from sensor import ReSkinBase, ReSkinSettings

class SensorProcess(Process):
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
    """
    def __init__(self,sensor_settings):
        """
        Parameters
        ----------
        sensor : type[ReSkinBase]
            Sensor object derived from ReSkinBase
        """
        super(SensorProcess, self).__init__()
        # self.sensor = ReSkinBase(
        #     num_mags=sensor_settings.num_mags,
        #     port=sensor_settings.port,
        #     baudrate=sensor_settings.baudrate,
        #     burst_mode=sensor_settings.burst_mode,
        #     device_id=sensor_settings.device_id)

        self._pipe_in, self._pipe_out = Pipe()
        self._sample_cnt = 0
        
        self._event_is_streaming = Event()
        self._event_quit_request = Event()
        self.sensor_settings = sensor_settings
        atexit.register(self.join)
        pass

    # Create a property for the last reading
    # @property
    # def last_reading

    def start_streaming(self):
        self._event_is_streaming.set()

    def pause_streaming(self):
        self._event_is_streaming.clear()

    def join(self, timeout=None):
        """
        Clean up before exiting
        """
        self._event_quit_request.set()
        # self.sensor.close()
        super(SensorProcess, self).join(timeout)
    
    def run(self):
        """
        This loop runs until it's asked to quit.
        """
        buffer = []
        # Initialize sensor
        
        self.sensor = ReSkinBase(
            num_mags=self.sensor_settings.num_mags,
            port=self.sensor_settings.port,
            baudrate=self.sensor_settings.baudrate,
            burst_mode=self.sensor_settings.burst_mode,
            device_id=self.sensor_settings.device_id)
        
        # self.sensor._initialize()
        is_streaming = False

        while not self._event_quit_request.is_set():
            if self._event_is_streaming.is_set():
                if not is_streaming:
                    is_streaming = True
                    # Any logging or stuff you want to do when polling has
                    # just started should go here
                
                d = self.sensor.get_data()

                # self._last_reading = d
                self._sample_cnt += 1

                buffer.append(d)
                self._buffer_size = len(buffer)

            else:
                if is_streaming:
                    is_streaming = False

                pass

if __name__ == '__main__':
    test_settings = ReSkinSettings(
        num_mags=5,
        port="COM32",
        baudrate=115200,
        burst_mode=True,
        device_id=1
    )
    # test_sensor = ReSkinBase(5, port="COM32", baudrate=115200)
    test_proc = SensorProcess(test_settings)
    test_proc.start()
    while True:
        input('aaaa')