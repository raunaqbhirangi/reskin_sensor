from collections import deque
import time

import argparse
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

from reskin_sensor import ReSkinProcess


def plot_heatmap(data, num_mags):
    data_dim = data.shape[-1]

    data_mask = np.zeros((data_dim,), dtype=bool)
    data_mask[2:-1] = True

    # Filter temperature if required
    if data_dim == 4 * num_mags + 3:
        data_mask[2:-1:4] = False

    fig, axs = plt.subplots(2, 1, figsize=(8, 16))

    filt_data = data[..., data_mask]
    times = data[..., 0] - data[0, 0]
    axs[0].plot(times, filt_data)
    axs[0].set_xlabel("Time, in s")
    pc = axs[1].pcolormesh(filt_data.T)

    xticks = np.arange(0, data.shape[0], max(1, data.shape[0] // 10))
    axs[1].set_xlabel("Time, in s")
    axs[1].set_xticks(xticks)
    axs[1].set_xticklabels(["{:.2f}".format(times[i]) for i in xticks])
    axs[1].set_yticks(np.linspace(0.5, num_mags * 3 - 0.5, num_mags * 3))

    ylabels = []
    for m in range(num_mags):
        ylabels.extend(["Bx{}".format(m), "By{}".format(m), "Bz{}".format(m)])
    axs[1].set_yticklabels(ylabels)

    fig.colorbar(pc)
    plt.show()


def update_data(ax, sensor, init_time, baseline, ln, xdata, ydata, i):
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
    # fmt: off
    parser = argparse.ArgumentParser(description="Visualize ReSkin data as a heatmap")
    parser.add_argument("--stream", action="store_true", help="Flag to stream live data")
    parser.add_argument("-nm", "--num-mags", type=int, required=True, help="Number of magnetometers")
    parser.add_argument("-p", "--port", type=str, default="/dev/ttyACM0", help="ReSkin post; ignored if not streaming")
    parser.add_argument("-ws", "--window-size", type=int, default=1000, help="Number of samples visualized at a time")
    parser.add_argument("--lims", type=float, nargs=2, default=[-300., 300.], help="Colorbar limits for streaming")

    parser.add_argument("-dp", "--data-path", type=str, help="Path for loading data")
    args = parser.parse_args()
    # fmt: on

    num_samples = args.window_size
    num_mags = args.num_mags

    if args.stream:
        reskin = ReSkinProcess(
            num_mags=args.num_mags,
            port=args.port,
            temp_filtered=True,
            reskin_data_struct=False,
        )
        reskin.start()
        time.sleep(1.0)
        init_data = np.array(reskin.get_data(num_samples))
        baseline = np.mean(init_data[..., 2:-1], axis=0, keepdims=True)
        init_time = init_data[0, 0]

        reskin.start_buffering()

        fig, ax = plt.subplots()
        xdata, ydata = deque(maxlen=num_samples), deque(maxlen=num_samples)

        xdata.extend(list(init_data[..., 0]) - init_time)
        ydata.extend(list(init_data[..., 2:-1] - baseline))

        ln = ax.pcolormesh(np.array(ydata).T, vmin=args.lims[0], vmax=args.lims[1])
        ax.set_xticks(np.arange(0, num_samples, max(1, num_samples // 10)))
        ax.set_yticks(np.linspace(0.5, num_mags * 3 - 0.5, num_mags * 3))
        ylabels = []
        for m in range(num_mags):
            ylabels.extend(["Bx{}".format(m), "By{}".format(m), "Bz{}".format(m)])
        ax.set_yticklabels(ylabels)
        ax.set_xlabel("Time, in s")
        cbar = fig.colorbar(ln)

        ani = FuncAnimation(
            fig,
            lambda i: update_data(ax, reskin, init_time, baseline, ln, xdata, ydata, i),
            blit=False,
        )
        plt.show()

    else:
        data_path = args.data_path

        # Load data
        with open(data_path, "rb") as f:
            data = np.load(f)

        data_dim = data.shape[-1]

        data_mask = np.zeros((data_dim,), dtype=bool)
        data_mask[2:-1] = True

        # Filter temperature if required
        if data_dim == 4 * num_mags + 3:
            data_mask[2:-1:4] = False

        with open(data_path, "rb") as f:
            data = np.load(f)
            # test_data = data["task"][..., data_mask]
        plot_heatmap(data, num_mags)
