import argparse
import time

from reskin_sensor import ReSkinProcess, ReSkinSettings, sensor

if __name__ == '__main__':
    test_settings = ReSkinSettings(
        num_mags=5,
        port="/dev/ttyACM0",
        baudrate=115200,
        burst_mode=True,
        device_id=1
    )

    # Create sensor stream
    sensor_stream = ReSkinProcess(test_settings)
    
    # Start sensor stream
    sensor_stream.start()

    # Buffer data for two seconds and return buffer

    sensor_stream.start_buffering()
    buffer_start = time.time()
    time.sleep(2.0)
    
    # sensor_stream.pause_buffering()
    buffer_stop = time.time()
    
    # Get buffered data
    buffered_data = sensor_stream.get_buffer()
    
    if buffered_data is not None:
        print('Time elapsed: {}, Number of datapoints: {}'.format(
            buffer_stop - buffer_start, len(buffered_data)))

    # Pause sensor stream
    sensor_stream.pause_streaming()

    sensor_stream.join()
    