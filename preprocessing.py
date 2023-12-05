"""Preprocessing util functions."""

import sys

sys.path.append("..")
from typing import Any, Dict, Tuple

import numpy as np

from utils import constants, recon_utils, signal_utils, spect_utils, traj_utils


def remove_contamination(dict_dyn: Dict[str, Any], dict_dis: Dict[str, Any]) -> Dict:
    """Remove gas contamination from data."""
    _, fit_obj = spect_utils.calculate_static_spectroscopy(
        fid=dict_dyn[constants.IOFields.FIDS_DIS],
        sample_time=dict_dyn[constants.IOFields.SAMPLE_TIME],
        tr=dict_dyn[constants.IOFields.TR],
        center_freq=dict_dyn[constants.IOFields.XE_CENTER_FREQUENCY],
        rf_excitation=dict_dyn[constants.IOFields.XE_DISSOLVED_OFFSET_FREQUENCY],
    )

    dict_dis[constants.IOFields.FIDS_DIS] = signal_utils.remove_gasphase_contamination(
        data_dissolved=dict_dis[constants.IOFields.FIDS_DIS],
        data_gas=dict_dis[constants.IOFields.FIDS_DIS],
        sample_time=dict_dyn[constants.IOFields.SAMPLE_TIME],
        freq_gas_acq_diss=fit_obj.freq[2],
        phase_gas_acq_diss=fit_obj.phase[2],
        area_gas_acq_diss=fit_obj.area[2],
        fa_gas=0.5,
    )
    return dict_dis


def prepare_data_and_traj(
    data_dict: Dict[str, Any], generate_traj: bool = True
) -> Tuple[np.ndarray, ...]:
    """Prepare data and trajectory data reconstruction.

    Uses a trajectory generated from the metadata in the twix file if generate_traj is
    True. Otherwise, it uses a manually imported trajectory. Then, it removes noise.

    Args:
        data_dict: dictionary containing data and metadata extracted from the twix file.
        Optionally also contains trajectories.
        generate_traj: bool flag to generate trajectory from metadata in twix file.

    Returns:
        traj (np.array): trajectory of shape (n_projections, n_points, 3)
    """

    if generate_traj:
        traj_x, traj_y, traj_z = traj_utils.generate_trajectory(
            sample_time=data_dict[constants.IOFields.SAMPLE_TIME],
            ramp_time=data_dict[constants.IOFields.RAMP_TIME],
            n_frames=data_dict[constants.IOFields.N_FRAMES],
            n_points=data_dict[constants.IOFields.FIDS].shape[1],
            del_x=data_dict[constants.IOFields.GRAD_DELAY_X],
            del_y=data_dict[constants.IOFields.GRAD_DELAY_Y],
            del_z=data_dict[constants.IOFields.GRAD_DELAY_Z],
        )
    else:
        raise ValueError("Manual trajectory import not implemented yet.")
    traj = np.stack([traj_x, traj_y, traj_z], axis=-1)
    return traj


def prepare_traj_interleaved(
    data_dict: Dict[str, Any], generate_traj: bool = True
) -> Tuple[np.ndarray, ...]:
    """Prepare data and trajectory for interleaved data reconstruction.

    Uses a trajectory generated from the metadata in the twix file if generate_traj is
    True. Otherwise, it uses a manually imported trajectory.

    Args:
        data_dict: dictionary containing data and metadata extracted from the twix file.
                    Optionally also contains trajectories.
        generate_traj: bool flag to generate trajectory from metadata in twix file.

    Returns:
        traj (np.array): interleaved gas and dissolved-phase trajectories
                        of shape (2*n_projections, n_points, 3)
    """

    if generate_traj:
        traj_x, traj_y, traj_z = traj_utils.generate_trajectory(
            sample_time=data_dict[constants.IOFields.SAMPLE_TIME],
            ramp_time=data_dict[constants.IOFields.RAMP_TIME],
            n_frames=data_dict[constants.IOFields.N_FRAMES],
            n_points=data_dict[constants.IOFields.FIDS_DIS].shape[1],
            del_x=data_dict[constants.IOFields.GRAD_DELAY_X],
            del_y=data_dict[constants.IOFields.GRAD_DELAY_Y],
            del_z=data_dict[constants.IOFields.GRAD_DELAY_Z],
        )
    else:
        traj = data_dict[constants.IOFields.TRAJ]
        traj_x = traj[:, :, 0]
        traj_y = traj[:, :, 1]
        traj_z = traj[:, :, 2]

    # stack trajectory
    traj_dis = np.stack([traj_x, traj_y, traj_z], axis=-1)
    traj_gas = np.copy(traj_dis)

    # interleave gas and dissolved trajectories
    traj = np.zeros((traj_dis.shape[0] * 2, traj_dis.shape[1], traj_dis.shape[2]))
    for i in range(traj_dis.shape[0]):
        traj[2 * i, :, :] = traj_gas[i, :, :]
        traj[2 * i + 1, :, :] = traj_dis[i, :, :]

    return traj


def normalize_data(data: np.ndarray, normalization: np.ndarray) -> np.ndarray:
    """Normalize data by a given normalization array.

    Args:
        data: data FIDs of shape (n_projections, n_points)
        normalization: normalization array of shape (n_projections,)
    """
    return np.divide(data, np.expand_dims(normalization, -1))


def truncate_data_and_traj(
    data: np.ndarray,
    traj: np.ndarray,
    n_skip_start: int = 200,
    n_skip_end: int = 0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Truncate data and trajectory to a specified number of points.

    Args:
        data_dis: data FIDs of shape (n_projections, n_points)
        traj_dis: trajectory of shape (n_projections, n_points, 3)
        n_skip_start: number of projections to skip at the start.
        n_skip_end: number of projections to skip at the end of the trajectory.

    Returns:
        A tuple of data and trajectory arrays with beginning and end projections
        removed.
    """
    shape_data = data.shape
    shape_traj = traj.shape
    return (
        data[n_skip_start : shape_data[0] - (n_skip_end)],
        traj[n_skip_start : shape_traj[0] - (n_skip_end)],
    )


def remove_noisy_projections(
    data: np.ndarray, traj: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Remove noisy projections from data and trajectory.

    Returns:
        Tuple of data, trajectory with noisy projections removed
    """
    # remove noisy radial projections
    indices = recon_utils.get_noisy_projections(
        data=data,
    )
    data, traj = recon_utils.apply_indices_mask(
        data=data,
        traj=traj,
        indices=np.array(indices),
    )
    return data, traj
