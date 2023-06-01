from collections import deque
import time

import argparse
import matplotlib.pyplot as plt
import numpy as np

from reskin_sensor import ReSkinProcess

if __name__ == "__main__":
    # fmt: off
    parser = argparse.ArgumentParser(description="Visualize ReSkin data as a heatmap")
    parser.add_argument("-nm", "--num-mags", type=int, required=True, help="Number of magnetometers")
    parser.add_argument("-p", "--port", type=str, default="/dev/ttyACM0", help="ReSkin post; ignored if not streaming")
    parser.add_argument("-ws", "--window-size", type=int, default=1000, help="Number of samples visualized at a time")

    args = parser.parse_args()
    # fmt: on

    num_samples = args.window_size
    num_mags = args.num_mags

    sensor_stream = ReSkinProcess(
        num_mags=args.num_mags,
        port=args.port,
        temp_filtered=True,
        reskin_data_struct=False,
        clean_spikes=True
    )
    sensor_stream.start()
    time.sleep(0.1)

    # Buffer data for two seconds and return buffer
    if sensor_stream.is_alive():
        sensor_stream.start_buffering()
        buffer_start = time.time()
        time.sleep(2.0)

        sensor_stream.pause_buffering()
        buffered_data = sensor_stream.get_buffer()
        data = np.stack(buffered_data)[:, 2:-1] 
        print(data.shape)
        print(np.amax(np.abs(data)))
        fig, axs = plt.subplots(num_mags, 3)
        for row in range(num_mags):
            for col in range(3):
                axs[row, col].plot(data[:,row * 3 + col])
                axs[row,col].set_ylim([-10000,10000])
        plt.show()

        sensor_stream.pause_streaming()

        sensor_stream.join()