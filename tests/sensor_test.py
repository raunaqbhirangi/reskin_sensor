import argparse
from reskin_sensor import ReSkinBase

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test code to query ReSkin for a fixed number of data samples"
    )
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        help="port to which the microcontroller is connected",
        required=True,
    )
    parser.add_argument(
        "-b",
        "--baudrate",
        type=str,
        help="baudrate at which the microcontroller is streaming data",
        default=115200,
    )
    parser.add_argument(
        "-n",
        "--num_mags",
        type=int,
        help="number of magentometers on the sensor board",
        default=5,
    )
    args = parser.parse_args()

    test_sensor = ReSkinBase(
        num_mags=args.num_mags,
        port=args.port,
        baudrate=args.baudrate,
        burst_mode=True,
        device_id=1,
    )

    # Get 5 samples from sensor
    test_samples = test_sensor.get_data(num_samples=5)

    print(
        "Columns: ",
        ", \t".join(
            [
                "T{0}, \tBx{0}, \tBy{0}, \tBz{0}".format(ind)
                for ind in range(test_sensor.num_mags)
            ]
        ),
    )
    for sid, sample in enumerate(test_samples):
        print(
            "Sample {}: ".format(sid + 1)
            + str(["{:.2f}".format(d) for d in sample.data])
        )
