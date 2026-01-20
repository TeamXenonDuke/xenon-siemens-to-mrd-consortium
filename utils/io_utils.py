"""Import and export util functions."""

import os
import sys
import logging

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
            + glob.glob(os.path.join(path, "**h_radial***.dat"))
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

def auto_select_gx_protocol(twix_obj: mapvbvd._attrdict.AttrDict) -> str:
    """Automatically select the GX protocol type based on the length of alTR.

    Uses the number of alTR entries to determine which reconstruction protocol to apply:
    - 7: KUMC protocol
        - check if single (single_echo_2) or 3 echo (multi_echo_2, gas_2 + dis_3)
    - 5: multi-echo with LHC 2 echoes (multi_echo, gas_2 + dis_2)
    - 1: single-echo protocol
    - Otherwise: raise error for manual selection
    """
    number_of_alTR = twix_utils.get_alTR(twix_obj);
    if number_of_alTR == 0:
        raise ValueError("Cannot automatically select GX protocol. Require manual selection")
    elif number_of_alTR == 7:
        echo_number = int(twix_obj.hdr.Phoenix[("alTR","4")])
        if echo_number == 1:
            return "single_echo_2"
        else:
            return "multi_echo_2"
    elif number_of_alTR == 5:
        return "multi_echo"
    elif number_of_alTR == 1:
        return "single_echo"
    else:
        raise ValueError(f"Unrecognized length of alTR: {number_of_alTR}. Cannot automatically select GX protocol. Require manual selection")

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
        constants.IOFields.SET_LABELS: data_dict[
            constants.IOFields.SET_LABELS
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
        constants.IOFields.XE_CENTER_FREQUENCY: twix_utils.get_center_freq(twix_obj),
        constants.IOFields.XE_DISSOLVED_OFFSET_FREQUENCY: twix_utils.get_excitation_freq(
            twix_obj
        ),
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
        constants.IOFields.PREP_PULSES: twix_utils.get_prep_pulses(twix_obj),
        constants.IOFields.PATIENT_BIRTHDAY: twix_utils.get_patient_birthday(twix_obj),
        constants.IOFields.PATIENT_HEIGHT: twix_utils.get_patient_height(twix_obj),
        constants.IOFields.PATIENT_SEX: twix_utils.get_patient_sex(twix_obj),
        constants.IOFields.PATIENT_WEIGHT: twix_utils.get_patient_weight(twix_obj),
    }


def read_dis_twix(path: str, multi_echo_flag: str = "single_echo") -> Dict[str, Any]:
    """Read dixon disssolved phase imaging twix file.

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
    
    # read gx data
    if multi_echo_flag == "multi_echo_2":
        data_dict = twix_utils.get_gx_data_multi_echo_2(twix_obj=twix_obj)
    elif multi_echo_flag == "multi_echo":
        data_dict = twix_utils.get_gx_data_multi_echo(twix_obj=twix_obj)
    elif "single_echo" in multi_echo_flag:
        data_dict = twix_utils.get_gx_data(twix_obj=twix_obj,multi_echo_flag=multi_echo_flag)
    else:
        raise ValueError("Could not read gas exchange data.")
    filename = os.path.basename(path)

    return {
        constants.IOFields.CONTRAST_LABELS: data_dict[
            constants.IOFields.CONTRAST_LABELS
        ],
        constants.IOFields.SET_LABELS: data_dict[
            constants.IOFields.SET_LABELS
        ],
        
        constants.IOFields.BONUS_SPECTRA_LABELS: data_dict[
            constants.IOFields.BONUS_SPECTRA_LABELS
        ],
        constants.IOFields.SAMPLE_TIME: twix_utils.get_dwell_time(twix_obj),
        constants.IOFields.SAMPLE_TIME_BONUS_SPECTRA: twix_utils.get_dwell_time_bonus_spectra(twix_obj,multi_echo_flag),
        constants.IOFields.FA_DIS: twix_utils.get_flipangle_dissolved(twix_obj,multi_echo_flag),
        constants.IOFields.FA_GAS: twix_utils.get_flipangle_gas(twix_obj,multi_echo_flag),
        constants.IOFields.FIELD_STRENGTH: twix_utils.get_field_strength(twix_obj),
        constants.IOFields.FIDS: data_dict[constants.IOFields.FIDS],
        constants.IOFields.FIDS_DIS: data_dict[constants.IOFields.FIDS_DIS],
        constants.IOFields.FIDS_GAS: data_dict[constants.IOFields.FIDS_GAS],
        constants.IOFields.FOV: twix_utils.get_FOV(twix_obj),
        constants.IOFields.XE_CENTER_FREQUENCY: twix_utils.get_center_freq(twix_obj),
        constants.IOFields.XE_DISSOLVED_OFFSET_FREQUENCY: twix_utils.get_excitation_freq(
            twix_obj
        ),
        constants.IOFields.INSTITUTION: twix_utils.get_institution(twix_obj),
        constants.IOFields.N_FRAMES: data_dict[constants.IOFields.N_FRAMES],
        constants.IOFields.N_POINTS: twix_utils.get_gas_exchange_npoints(twix_obj), 
        constants.IOFields.N_POINTS_BONUS_SPECTRA :twix_utils.get_bonus_spectra_npoints(twix_obj,multi_echo_flag),
        constants.IOFields.ORIENTATION: twix_utils.get_orientation(twix_obj),
        constants.IOFields.PROTOCOL_NAME: twix_utils.get_protocol_name(twix_obj),
        constants.IOFields.RAMP_TIME: twix_utils.get_ramp_time(twix_obj),
        constants.IOFields.REMOVEOS: twix_utils.get_flag_removeOS(twix_obj),
        constants.IOFields.SCAN_DATE: twix_utils.get_scan_date(twix_obj),
        constants.IOFields.SYSTEM_VENDOR: twix_utils.get_system_vendor(twix_obj),
        constants.IOFields.SOFTWARE_VERSION: twix_utils.get_software_version(twix_obj),
        constants.IOFields.TE: twix_utils.get_TE(twix_obj,multi_echo_flag),
        constants.IOFields.TR_GAS: twix_utils.get_TR_dissolved(twix_obj),
        constants.IOFields.TR_DIS: twix_utils.get_TR_dissolved(twix_obj),
        constants.IOFields.BANDWIDTH: twix_utils.get_bandwidth(
            twix_obj, data_dict, filename
        ),
        constants.IOFields.NUMBER_OF_ECHO: data_dict[constants.IOFields.NUMBER_OF_ECHO],
        constants.IOFields.PREP_PULSES: twix_utils.get_prep_pulses(twix_obj),
        constants.IOFields.PATIENT_BIRTHDAY: twix_utils.get_patient_birthday(twix_obj),
        constants.IOFields.PATIENT_HEIGHT: twix_utils.get_patient_height(twix_obj),
        constants.IOFields.PATIENT_SEX: twix_utils.get_patient_sex(twix_obj),
        constants.IOFields.PATIENT_WEIGHT: twix_utils.get_patient_weight(twix_obj),
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
        constants.IOFields.XE_CENTER_FREQUENCY: twix_utils.get_center_freq(twix_obj),
        constants.IOFields.XE_DISSOLVED_OFFSET_FREQUENCY: twix_utils.get_excitation_freq(
            twix_obj
        ),
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
        constants.IOFields.PREP_PULSES: twix_utils.get_prep_pulses(twix_obj),
        constants.IOFields.PATIENT_BIRTHDAY: twix_utils.get_patient_birthday(twix_obj),
        constants.IOFields.PATIENT_HEIGHT: twix_utils.get_patient_height(twix_obj),
        constants.IOFields.PATIENT_SEX: twix_utils.get_patient_sex(twix_obj),
        constants.IOFields.PATIENT_WEIGHT: twix_utils.get_patient_weight(twix_obj),
    }


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


def move_files(source_paths: list, destination_path: str) -> None:
    """Move files to a new directory.

    If target directory does not exist, it is created.
    Args:
        source_paths (list): list of paths of files to move
        destination_path (str): path to move files to
    """
    # if target directory doesn't exist, create it
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
    # move files to target directory
    for path in source_paths:
        fname = os.path.basename(path)
        if os.path.isfile(path):
            shutil.move(path, os.path.join(destination_path, fname))


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
