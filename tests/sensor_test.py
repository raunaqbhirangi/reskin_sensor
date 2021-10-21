from reskin_sensor import ReSkinBase

if __name__ == '__main__':
    test_sensor = ReSkinBase(
        num_mags=5,
        port='/dev/ttyACM0',
        burst_mode=True,
        device_id=1
    )

    # Get 5 samples from sensor
    test_samples = test_sensor.get_data(num_samples=5)

    print('Columns: ', ', '.join(['T{0}, Bx{0}, By{0}, Bz{0}'.format(ind) for ind in range(test_sensor.num_mags)]))
    for sid, sample in enumerate(test_samples):
        print('Sample {}: '.format(sid+1) + str(['{:.2f}'.format(d) for d in sample.data]))