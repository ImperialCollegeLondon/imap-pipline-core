from datetime import datetime


def simulateSpinAxisCalibration(xarray):
    timestamps = [datetime(2022, 3, 3)]
    offsets = [3.256]

    return (timestamps, offsets)


def simulateSpinPlaneCalibration(xarray):
    timestamps = [datetime(2022, 3, 3)]
    offsets_x = [3.256]
    offsets_y = [2.76]

    return (timestamps, offsets_x, offsets_y)
