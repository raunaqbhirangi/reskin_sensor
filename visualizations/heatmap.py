from collections import deque
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

from reskin_sensor import ReSkinProcess
from reskin_sensor.sensor import ReSkinBase

def plot_heatmap(data, times):
    _, axs = plt.subplots(2,1, figsize = (5,5))

    axs[0].plot(data)

    axs[1].pcolormesh(data.T)
    axs[1].set_aspect(20)
    plt.show()

def init():
    ax.set_xlim(0, 2*np.pi)
    ax.set_ylim(-1, 1)
    return ln,

def update(frame):
    xdata.append(frame)
    ydata.append(np.sin(frame))
    ln.set_data(xdata, ydata)
    return ln,

def update_data(sensor, baseline, ln, ydata, i):
    sensor.pause_buffering()
    buf = np.array(sensor.get_buffer())
    sensor.start_buffering()
    # times = buf[:,0]
    data = buf[:,2:-1] - baseline
    ydata.extend(list(data))
    
    ln.set_array(np.array(ydata).T)
    return ln,



if __name__ == '__main__':
    # TODO: Add option for streaming data
    streaming = True
    data_path = 'data/data_1.npz'

    data_mask = np.zeros((11,), dtype=bool)
    data_mask[2:-1] = True
    data_mask[2:-1:4] = False
    num_samples = 1000

    if streaming:
        reskin = ReSkinProcess(num_mags=2, port='/dev/ttyACM0', temp_filtered=True, reskin_data_struct=False)
        reskin.start()
        time.sleep(2.)
        init_data = np.array(reskin.get_data(num_samples))
        baseline = np.mean(init_data[..., 2:-1], axis=0, keepdims=True)

        reskin.start_buffering()

        fig, ax = plt.subplots()
        xdata, ydata = [i for i in range(num_samples)], deque(maxlen=num_samples)
        ydata.extend(list(init_data[...,2:-1] - baseline))

        ln = ax.pcolormesh(np.array(ydata).T)

        ani = FuncAnimation(fig, lambda i: update_data(reskin, baseline, ln, ydata, i), blit=True)
        plt.show()

    else:
        with open(data_path, 'rb') as f:
            data = np.load(f)
            test_data = data['task'][...,data_mask]
            plot_heatmap(test_data, data['task'][...,0])