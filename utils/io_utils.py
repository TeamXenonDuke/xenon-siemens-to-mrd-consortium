"""Import and export util functions."""

import os
import sys

sys.path.append("..")
import csv
import glob
import shutil
from typing import Any, Dict, List, Optional, Tuple

import ismrmrd
import mapvbvd
import nibabel as nib
import numpy as np
import pandas as pd
import scipy.io as sio
from ml_collections import config_dict

from utils import constants, mrd_utils, twix_utils


def import_np(path: str) -> np.ndarray:
    """Import npy file to np.ndarray.

    Args:
        path: str file path of npy file
    Returns:
        np.ndarray loaded from npy file
    """
    return np.load(path)


def import_nii(path: str) -> np.ndarray:
    """Import image as np.ndarray.

    Args:
        path: str file path of nifti file
    Returns:
        np.ndarray loaded from nifti file
    """
    return nib.load(path).get_fdata()


def import_mat(path: str) -> Dict[str, Any]:
    """Import  matlab file as dictionary.

    Args:
        path: str file path of matlab file
    Returns:
        dictionary loaded from matlab file
    """
    return sio.loadmat(path)


def import_matstruct_to_dict(struct: np.ndarray) -> Dict[str, Any]:
    """Import matlab  as dictionary.

    Args:
        path: str file path of matlab file
    Returns:
        dictionary loaded from matlab file
    """
    out_dict = {}
    for field in struct.dtype.names:
        value = struct[field].flatten()[0]
        if isinstance(value[0], str):
            # strings
            out_dict[field] = str(value[0])
        elif len(value) == 1:
            # numbers
            out_dict[field] = value[0][0]
        else:
            # arrays
            out_dict[field] = np.asarray(value)
    return out_dict


def get_dyn_twix_files(path: str) -> str:
    """Get list of dynamic spectroscopy twix files.

    Args:
        path: str directory path of twix files
    Returns:
        str file path of twix file
    """
    try:
        return (
            glob.glob(os.path.join(path, "**cali**.dat"))
            + glob.glob(os.path.join(path, "**dynamic**.dat"))
            + glob.glob(os.path.join(path, "**Dynamic**.dat"))
            + glob.glob(os.path.join(path, "**dyn**.dat"))
        )[0]
    except:
        raise ValueError("Can't find twix file in path.")


def get_dis_twix_files(path: str) -> str:
    """Get list of gas exchange twix files.

    Args:
        path: str directory path of twix files
    Returns:
        str file path of twix file
    """
    try:
        return (
            glob.glob(os.path.join(path, "**dixon***.dat"))
            + glob.glob(os.path.join(path, "**Dixon***.dat"))
        )[0]
    except:
        raise ValueError("Can't find twix file in path.")


def get_ute_twix_files(path: str) -> str:
    """Get list of UTE twix files.

    Args:
        path: str directory path of twix files
    Returns:
        str file path of twix file
    """
    try:
        return (
            glob.glob(os.path.join(path, "**1H***.dat"))
            + glob.glob(os.path.join(path, "**BHUTE***.dat"))
            + glob.glob(os.path.join(path, "**ute***.dat"))
        )[0]
    except:
        raise ValueError("Can't find twix file in path.")


def get_dyn_mrd_files(path: str) -> str:
    """Get list of dynamic spectroscopy MRD files.

    Args:
        path: str directory path of MRD files
    Returns:
        str file path of MRD file
    """
    try:
        return (
            glob.glob(os.path.join(path, "**Calibration***.h5"))
            + glob.glob(os.path.join(path, "**calibration***.h5"))
        )[0]
    except:
        raise ValueError("Can't find MRD file in path.")


def get_dis_mrd_files(path: str) -> str:
    """Get list of gas exchange MRD files.

    Args:
        path: str directory path of MRD files
    Returns:
        str file path of MRD file
    """
    try:
        return (
            glob.glob(os.path.join(path, "**Gas***.h5"))
            + glob.glob(os.path.join(path, "**dixon***.h5"))
        )[0]
    except:
        raise ValueError("Can't find MRD file in path.")


def get_mat_file(path: str) -> str:
    """Get list of mat file of reconstructed images.

    Args:
        path: str directory path of mat file.
    Returns:
        str file path of mat file
    """
    try:
        return (glob.glob(os.path.join(path, "**.mat")))[0]
    except:
        raise ValueError("Can't find mat file in path.")


def read_dyn_twix(path: str) -> Dict[str, Any]:
    """Read dynamic spectroscopy twix file.

    Args:
        path: str file path of twix file
    Returns:
        dictionary containing data and metadata extracted from the twix file.
    """
    try:
        twix_obj = mapvbvd.mapVBVD(path)
    except:
        raise ValueError("Invalid twix file.")
    twix_obj.image.squeeze = True
    twix_obj.image.flagIgnoreSeg = True
    twix_obj.image.flagRemoveOS = False

    data_dict = twix_utils.get_dyn_data(twix_obj)

    return {
        constants.IOFields.CONTRAST_LABELS: data_dict[
            constants.IOFields.CONTRAST_LABELS
        ],
        constants.IOFields.BONUS_SPECTRA_LABELS: data_dict[
            constants.IOFields.BONUS_SPECTRA_LABELS
        ],
        constants.IOFields.SAMPLE_TIME: twix_utils.get_dwell_time(twix_obj),
        constants.IOFields.FA_DIS: twix_utils.get_flipangle_dissolved(twix_obj),
        constants.IOFields.FA_GAS: twix_utils.get_flipangle_gas(twix_obj),
        constants.IOFields.FIELD_STRENGTH: twix_utils.get_field_strength(twix_obj),
        constants.IOFields.FIDS: data_dict[constants.IOFields.FIDS],
        constants.IOFields.FOV: twix_utils.get_FOV(twix_obj),
        constants.IOFields.FREQ_CENTER: twix_utils.get_center_freq(twix_obj),
        constants.IOFields.FREQ_EXCITATION: twix_utils.get_excitation_freq(twix_obj),
        constants.IOFields.INSTITUTION: twix_utils.get_institution(twix_obj),
        constants.IOFields.N_FRAMES: data_dict[constants.IOFields.N_FRAMES],
        constants.IOFields.N_POINTS: data_dict[constants.IOFields.FIDS].shape[1],
        constants.IOFields.ORIENTATION: twix_utils.get_orientation(twix_obj),
        constants.IOFields.PROTOCOL_NAME: twix_utils.get_protocol_name(twix_obj),
        constants.IOFields.REMOVEOS: twix_utils.get_flag_removeOS(twix_obj),
        constants.IOFields.SCAN_DATE: twix_utils.get_scan_date(twix_obj),
        constants.IOFields.SYSTEM_VENDOR: twix_utils.get_system_vendor(twix_obj),
        constants.IOFields.SOFTWARE_VERSION: twix_utils.get_software_version(twix_obj),
        constants.IOFields.TE: twix_utils.get_TE(twix_obj),
        constants.IOFields.TR_GAS: twix_utils.get_TR_dissolved(twix_obj),
        constants.IOFields.TR_DIS: twix_utils.get_TR_dissolved(twix_obj),
    }


def read_dis_twix(path: str) -> Dict[str, Any]:
    """Read 1-point dixon disssolved phase imaging twix file.

    Args:
        path: str file path of twix file
    Returns:
        dictionary containing data and metadata extracted from the twix file.
    """
    try:
        twix_obj = mapvbvd.mapVBVD(path)
    except:
        raise ValueError("Invalid twix file.")
    twix_obj.image.squeeze = True
    twix_obj.image.flagIgnoreSeg = True
    twix_obj.image.flagRemoveOS = False

    data_dict = twix_utils.get_gx_data(twix_obj=twix_obj)
    filename = os.path.basename(path)

    return {
        constants.IOFields.CONTRAST_LABELS: data_dict[
            constants.IOFields.CONTRAST_LABELS
        ],
        constants.IOFields.BONUS_SPECTRA_LABELS: data_dict[
            constants.IOFields.BONUS_SPECTRA_LABELS
        ],
        constants.IOFields.SAMPLE_TIME: twix_utils.get_dwell_time(twix_obj),
        constants.IOFields.FA_DIS: twix_utils.get_flipangle_dissolved(twix_obj),
        constants.IOFields.FA_GAS: twix_utils.get_flipangle_gas(twix_obj),
        constants.IOFields.FIELD_STRENGTH: twix_utils.get_field_strength(twix_obj),
        constants.IOFields.FIDS: data_dict[constants.IOFields.FIDS],
        constants.IOFields.FIDS_DIS: data_dict[constants.IOFields.FIDS_DIS],
        constants.IOFields.FIDS_GAS: data_dict[constants.IOFields.FIDS_GAS],
        constants.IOFields.FOV: twix_utils.get_FOV(twix_obj),
        constants.IOFields.FREQ_CENTER: twix_utils.get_center_freq(twix_obj),
        constants.IOFields.FREQ_EXCITATION: twix_utils.get_excitation_freq(twix_obj),
        constants.IOFields.GRAD_DELAY_X: data_dict[constants.IOFields.GRAD_DELAY_X],
        constants.IOFields.GRAD_DELAY_Y: data_dict[constants.IOFields.GRAD_DELAY_Y],
        constants.IOFields.GRAD_DELAY_Z: data_dict[constants.IOFields.GRAD_DELAY_Z],
        constants.IOFields.INSTITUTION: twix_utils.get_institution(twix_obj),
        constants.IOFields.N_FRAMES: data_dict[constants.IOFields.N_FRAMES],
        constants.IOFields.N_POINTS: data_dict[constants.IOFields.FIDS].shape[1],
        constants.IOFields.ORIENTATION: twix_utils.get_orientation(twix_obj),
        constants.IOFields.PROTOCOL_NAME: twix_utils.get_protocol_name(twix_obj),
        constants.IOFields.RAMP_TIME: twix_utils.get_ramp_time(twix_obj),
        constants.IOFields.REMOVEOS: twix_utils.get_flag_removeOS(twix_obj),
        constants.IOFields.SCAN_DATE: twix_utils.get_scan_date(twix_obj),
        constants.IOFields.SYSTEM_VENDOR: twix_utils.get_system_vendor(twix_obj),
        constants.IOFields.SOFTWARE_VERSION: twix_utils.get_software_version(twix_obj),
        constants.IOFields.TE: twix_utils.get_TE(twix_obj),
        constants.IOFields.TR_GAS: twix_utils.get_TR_dissolved(twix_obj),
        constants.IOFields.TR_DIS: twix_utils.get_TR_dissolved(twix_obj),
        constants.IOFields.BANDWIDTH: twix_utils.get_bandwidth(
            twix_obj, data_dict, filename
        ),
    }


def read_ute_twix(path: str) -> Dict[str, Any]:
    """Read proton ute imaging twix file.

    Args:
        path: str file path of twix file
    Returns:
        dictionary containing data and metadata extracted from the twix file.
    """
    try:
        twix_obj = mapvbvd.mapVBVD(path)
    except:
        raise ValueError("Invalid twix file.")
    try:
        twix_obj.image.squeeze = True
    except:
        # this is old data, need to get the 2nd element
        twix_obj = twix_obj[1]
    try:
        twix_obj.image.squeeze = True
        twix_obj.image.flagIgnoreSeg = True
        twix_obj.image.flagRemoveOS = False
    except:
        raise ValueError("Cannot get data from twix object.")

    data_dict = twix_utils.get_ute_data(twix_obj=twix_obj)

    return {
        constants.IOFields.CONTRAST_LABELS: data_dict[
            constants.IOFields.CONTRAST_LABELS
        ],
        constants.IOFields.BONUS_SPECTRA_LABELS: data_dict[
            constants.IOFields.BONUS_SPECTRA_LABELS
        ],
        constants.IOFields.SAMPLE_TIME: twix_utils.get_dwell_time(twix_obj),
        constants.IOFields.FA_PROTON: twix_utils.get_flipangle_proton(twix_obj),
        constants.IOFields.FIELD_STRENGTH: twix_utils.get_field_strength(twix_obj),
        constants.IOFields.FIDS: data_dict[constants.IOFields.FIDS],
        constants.IOFields.FOV: twix_utils.get_FOV(twix_obj),
        constants.IOFields.FREQ_CENTER: twix_utils.get_center_freq(twix_obj),
        constants.IOFields.FREQ_EXCITATION: twix_utils.get_excitation_freq(twix_obj),
        constants.IOFields.GRAD_DELAY_X: data_dict[constants.IOFields.GRAD_DELAY_X],
        constants.IOFields.GRAD_DELAY_Y: data_dict[constants.IOFields.GRAD_DELAY_Y],
        constants.IOFields.GRAD_DELAY_Z: data_dict[constants.IOFields.GRAD_DELAY_Z],
        constants.IOFields.INSTITUTION: twix_utils.get_institution(twix_obj),
        constants.IOFields.N_FRAMES: data_dict[constants.IOFields.N_FRAMES],
        constants.IOFields.N_POINTS: data_dict[constants.IOFields.FIDS].shape[1],
        constants.IOFields.ORIENTATION: twix_utils.get_orientation(twix_obj),
        constants.IOFields.PROTOCOL_NAME: twix_utils.get_protocol_name(twix_obj),
        constants.IOFields.RAMP_TIME: twix_utils.get_ramp_time(twix_obj),
        constants.IOFields.REMOVEOS: twix_utils.get_flag_removeOS(twix_obj),
        constants.IOFields.SCAN_DATE: twix_utils.get_scan_date(twix_obj),
        constants.IOFields.SYSTEM_VENDOR: twix_utils.get_system_vendor(twix_obj),
        constants.IOFields.SOFTWARE_VERSION: twix_utils.get_software_version(twix_obj),
        constants.IOFields.TE: twix_utils.get_TE(twix_obj),
        constants.IOFields.TR_PROTON: twix_utils.get_TR(twix_obj),
    }


def export_subject_mat(subject: object, path: str):
    """Export select subject instance variables to mat file.

    Args:
        subject: subject instance
        path: str file path of mat file
    """
    sio.savemat(path, vars(subject))


def export_np(arr: np.ndarray, path: str):
    """Export numpy array to npy file.

    Args:
        arr: np.ndarray array to be exported
        path: str file path of npy file
    """
    np.save(path, arr)


def write_mrd_file(path: str, data_dict: Dict[str, Any], scan_type: str):
    """Write MRD file according to consortium specifications.

    Args:
        path (str): path of mrd file
        data_dict (dict): dictionary of FID acquisition and header data
        scan_type (str): calibration, proton, or dixon
    """
    # remove file if it exists
    if os.path.exists(path):
        os.remove(path)

    # write ismrmrd acquisition data
    ismrmrd_data_set = mrd_utils.write_acquisition_data(path, data_dict)

    # write ismrmrd header
    ismrmrd_header = mrd_utils.write_ismrmrd_header(data_dict, scan_type)
    ismrmrd_data_set.write_xml_header(ismrmrd.xsd.ToXML(ismrmrd_header))

    # close ismrmrd data file
    ismrmrd_data_set.close()


def export_subject_csv(dict_stats: Dict[str, Any], path: str, overwrite=False):
    """Export statistics to running csv file.

    Uses the csv.DictWriter class to write a csv file. First, checks if the csv
    file exists and the header has been written. If not, writes the header. Then,
    writes to a new file or new row of data in existing file.

    Args:
        dict_stats (dict): dictionary containing statistics to be exported
        path (str): file path of csv file
        overwrite (bool): if True, overwrite existing csv file
    """
    header = dict_stats.keys()
    if overwrite or (not os.path.exists(path)):
        with open(path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            writer.writerow(dict_stats)
    else:
        with open(path, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writerow(dict_stats)


def export_config_to_json(config: config_dict, path: str) -> None:
    """
    Save a dictionary to a JSON file.

    Args:
    - data (ml_collections.ConfigDict): The config dictionary to save.
    - path (str): The name of the file to save the dictionary to.

    Returns:
    - None
    """
    with open(path, "w") as f:
        f.write(config.to_json_best_effort(indent=4))
