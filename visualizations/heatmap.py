from collections import deque
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

def update_data(sensor, fig, ax, xdata, ydata, frame):
    sensor.pause_buffering()
    buf = sensor.get_buffer()
    sensor.start_buffering()
    times = buf[:,0]
    data = buf[:,2:-1]
    ydata.extend(list(data))
    ax.plot(ydata)



if __name__ == '__main__':
    # TODO: Add option for streaming data
    streaming = True
    data_path = 'data/data_1.npz'

    data_mask = np.zeros((11,), dtype=bool)
    data_mask[2:-1] = True
    data_mask[2:-1:4] = False
    
    reskin = ReSkinBase(num_mags=2, port='/dev/ttyACM0', temp_filtered=True, reskin_data_struct=False)
    print(reskin.get_data(10))
    exit()

    if streaming:
        reskin = ReSkinProcess(num_mags=2, port='/dev/ttyACM0', temp_filtered=True, reskin_data_struct=False)
        reskin.start()
        reskin.start_buffering()

        fig, ax = plt.subplots()
        xdata, ydata = deque(maxlen=1000), deque(maxlen=1000)
        ln, = plt.plot([], [], 'ro')

        ani = FuncAnimation(fig, lambda i: update_data(reskin, fig, ax, xdata, ydata, i), init_func=init, blit=True)
        plt.show()

    else:
        with open(data_path, 'rb') as f:
            data = np.load(f)
            test_data = data['task'][...,data_mask]
            plot_heatmap(test_data, data['task'][...,0])