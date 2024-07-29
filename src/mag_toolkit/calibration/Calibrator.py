from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

import numpy as np

from src.mag_toolkit.calibration import MatlabWrapper
from src.mag_toolkit.calibration.calibrationFormat import (
    CalibrationFormat,
    OffsetCollection,
    SingleCalibration,
    Unit,
)


class CalibratorType(str, Enum):
    SPINAXIS = ("SpinAxisCalibrator",)
    SPINPLANE = "SpinPlaneCalibrator"


class Calibrator(ABC):
    def generateOffsets(self, data) -> OffsetCollection:
        """Generates a set of offsets."""
        (timestamps, x_offsets, y_offsets, z_offsets) = self.runCalibration(data)

        offsetCollection = OffsetCollection(X=x_offsets, Y=y_offsets, Z=z_offsets)

        sensor_name = "MAGO"

        singleCalibration = SingleCalibration(
            timestamps=timestamps,
            offsets=offsetCollection,
            units=Unit.NT,
            instrument=sensor_name,
            creation_timestamp=datetime.now(),
            method=str(self.name),
        )
        return singleCalibration

    def generateCalibration(self, data) -> CalibrationFormat:
        singleCalibration = self.generateOffsets(data)
        calibration = CalibrationFormat(
            valid_start=singleCalibration.timestamps[0],
            valid_end=singleCalibration.timestamps[-1],
            calibrations=[singleCalibration],
        )
        return calibration

    @abstractmethod
    def runCalibration(self, data):
        """Calibration that generates offsets and timestamps."""


class SpinAxisCalibrator(Calibrator):
    def __init__(self):
        self.name = CalibratorType.SPINAXIS

    def runCalibration(self, data):
        (timestamps, z_offsets) = MatlabWrapper.simulateSpinAxisCalibration(data)

        return (
            timestamps,
            np.zeros(len(z_offsets)),
            np.zeros(len(z_offsets)),
            z_offsets,
        )


class SpinPlaneCalibrator(Calibrator):
    def __init__(self):
        self.name = CalibratorType.SPINPLANE

    def runCalibration(self, data):
        (timestamps, x_offsets, y_offsets) = (
            MatlabWrapper.simulateSpinPlaneCalibration()
        )

        return (timestamps, x_offsets, y_offsets, np.zeros(len(x_offsets)))
