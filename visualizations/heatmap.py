from collections import deque
import time

import argparse
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import FormatStrFormatter
import numpy as np

from reskin_sensor import ReSkinProcess
from reskin_sensor.sensor import ReSkinBase


def plot_heatmap(data, times):
    _, axs = plt.subplots(2, 1, figsize=(5, 5))

    axs[0].plot(data)

    axs[1].pcolormesh(data.T)
    # axs[1].set_aspect(20)
    plt.show()


def update_data(ax, cbar, sensor, init_time, baseline, ln, xdata, ydata, i):
    sensor.pause_buffering()
    buf = np.array(sensor.get_buffer())
    sensor.start_buffering()
    times = buf[:, 0] - init_time
    data = buf[:, 2:-1] - baseline

    xdata.extend(list(times))
    ydata.extend(list(data))

    ln.set_array(np.array(ydata).T)

    xticks = np.arange(0, len(xdata), max(1, len(xdata) // 10))
    xlabels = ["{:.2f}".format(xdata[i]) for i in xticks]

    ax.set_xticklabels(xlabels)

    return (ln,)


if __name__ == "__main__":
    # TODO: Add option for streaming data
    streaming = False
    data_path = "data/data_1.npz"

    data_mask = np.zeros((11,), dtype=bool)
    data_mask[2:-1] = True
    data_mask[2:-1:4] = False
    num_samples = 1000
    num_mags = 2

    if streaming:
        reskin = ReSkinProcess(
            num_mags=num_mags,
            port="/dev/ttyACM0",
            temp_filtered=True,
            reskin_data_struct=False,
        )
        reskin.start()
        time.sleep(2.0)
        init_data = np.array(reskin.get_data(num_samples))
        baseline = np.mean(init_data[..., 2:-1], axis=0, keepdims=True)
        init_time = init_data[0, 0]

        reskin.start_buffering()

        fig, ax = plt.subplots()
        xdata, ydata = deque(maxlen=num_samples), deque(maxlen=num_samples)

        xdata.extend(list(init_data[..., 0]) - init_time)
        ydata.extend(list(init_data[..., 2:-1] - baseline))

        ln = ax.pcolormesh(np.array(ydata).T, vmin=-300.0, vmax=300.0)
        ax.set_xticks(np.arange(0, num_samples, max(1, num_samples // 10)))
        ax.set_yticks(np.linspace(0.5, num_mags * 3 - 0.5, num_mags * 3))
        ylabels = []
        for m in range(num_mags):
            ylabels.extend(["Bx{}".format(m), "By{}".format(m), "Bz{}".format(m)])
        ax.set_yticklabels(ylabels)
        cbar = fig.colorbar(ln)
        # cbar = plt.colorbar(ln, cax=ax)
        ani = FuncAnimation(
            fig,
            lambda i: update_data(
                ax, cbar, reskin, init_time, baseline, ln, xdata, ydata, i
            ),
            blit=False,
        )
        plt.show()

    else:
        with open(data_path, "rb") as f:
            data = np.load(f)
            test_data = data["task"][..., data_mask]
            plot_heatmap(test_data, data["task"][..., 0])
