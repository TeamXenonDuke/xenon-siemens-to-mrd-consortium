"""Spectroscopy util functions."""
import math
import sys

sys.path.append("..")
from typing import Any, Optional, Tuple

import numpy as np


def get_breathhold_indices(
    t: np.ndarray, start_time: int, end_time: int
) -> Tuple[int, int]:
    """Get the start and stop index based on the start and stop time.

    Find the index in the time array corresponding to the start time and the end time.
    If the start index is not found, return 0.
    If the stop index is not found return the last index of the array.

    Args:
        t (np.ndarray): array of time points each FID is collected in units of seconds.
        start_time (int): start time (in seconds) of window to analyze t.
        end_time (int): stop time (in seconds) of window to analyze t.

    Returns:
        Tuple of the indices corresponding to the start time and stop time.
    """

    def round_up(x: float, decimals: int = 0) -> float:
        """Round number to the nearest decimal place.

        Args:
            x: floating point number to be rounded up.
            decimals: number of decimal places to round by.

        Returns:
            rounded up value of x.
        """
        return math.ceil(x * 10**decimals) / 10**decimals

    start_ind = np.argwhere(np.array([round_up(x, 2) for x in t]) == start_time)
    end_ind = np.argwhere(np.array([round_up(x, 2) for x in t]) == end_time)

    if np.size(start_ind) == 0:
        start_ind = [0]
    if np.size(end_ind) == 0:
        end_ind = [np.size(t)]
    return (
        int(start_ind[int(np.floor(np.size(start_ind) / 2))]),
        int(end_ind[int(np.floor(np.size(end_ind) / 2))]),
    )


def get_frequency_guess(
    data: Optional[np.ndarray], center_freq: float, rf_excitation: int
):
    """Get the three-peak initial frequency guess.

    This can be modified in the future to include automated peak finding.

    Args:
        data (np.ndarray): FID data of shape (n_points, 1) or (n_points, ).
        center_freq (float): center frequency in MHz.
        rf_excitation (int): excitation frequency in ppm.

    Returns: 3-element array of initial frequency guesses corresponding to the RBC,
        membrane, and gas frequencys in MHz
    """
    if rf_excitation == 208:
        return np.array([10, -21.7, -208.4]) * center_freq
    elif rf_excitation == 218:
        return np.array([0, -21.7, -218.0]) * center_freq
    else:
        raise ValueError("Invalid excitation frequency {}".format(rf_excitation))


def get_area_guess(data: Optional[np.ndarray], center_freq: float, rf_excitation: int):
    """Get the three-peak initial area guess.

    This can be modified in the future to include automated peak finding.

    Args:
        data (np.ndarray): FID data of shape (n_points, 1) or (n_points, ).
        center_freq (float): center frequency in MHz.
        rf_excitation (int): excitation frequency in ppm.

    Returns: 3-element array of initial area guesses corresponding to the RBC,
        membrane, and gas frequencys in MHz
    """
    if rf_excitation == 208:
        return np.array([1, 1, 1])
    elif rf_excitation == 218:
        return np.array([1, 1, 1])
    else:
        raise ValueError("Invalid excitation frequency {}".format(rf_excitation))
