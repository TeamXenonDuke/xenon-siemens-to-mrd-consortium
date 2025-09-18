"""MRD util functions."""
import logging
import sys
from typing import Any, Dict

import ismrmrd
import numpy as np

sys.path.append("..")
from utils import constants


def write_ismrmrd_header(data_dict: Dict[str, Any], scan_type: str):
    """Write ismrmrdHeader according to 129Xe consortium specifications.

    Args:
        data_dict (dict): dictionary of scan data and header variables
        scan_type (str): type of scan (calibration, dixon, or proton)

    Specifications can be found at:
        https://docs.google.com/spreadsheets/d/1SeG4K4VgA1DUrTBhSjgeSqu3UCGiCWaLG3wqHg6hBh8/edit?usp=sharing

    NOTE: this header generally describes variables that don't change between FID acquisitions
    """

    # initialize ismrmrd header
    ismrmrd_header = ismrmrd.xsd.ismrmrdHeader()

    # write universal header variables
    _write_scan_date(ismrmrd_header, data_dict[constants.IOFields.SCAN_DATE])
    _write_subject_id(ismrmrd_header, data_dict[constants.IOFields.SUBJECT_ID])
    _write_system_vendor(ismrmrd_header, data_dict[constants.IOFields.SYSTEM_VENDOR])
    _write_institution(ismrmrd_header, data_dict[constants.IOFields.INSTITUTION])
    _write_field_strength(ismrmrd_header, data_dict[constants.IOFields.FIELD_STRENGTH])
    _write_te(ismrmrd_header, data_dict[constants.IOFields.TE])
    _write_fov(ismrmrd_header, data_dict[constants.IOFields.FOV])

    # write scan-specific header variables
    if scan_type == "calibration":
        _write_ramp_time(ismrmrd_header, data_dict[constants.IOFields.RAMP_TIME])
        _write_tr(
            ismrmrd_header,
            [
                data_dict[constants.IOFields.TR_GAS],
                data_dict[constants.IOFields.TR_DIS],
            ],
        )
        _write_flip_angle(
            ismrmrd_header,
            [
                data_dict[constants.IOFields.FA_GAS],
                data_dict[constants.IOFields.FA_DIS],
            ],
        )
        _write_freq_center(
            ismrmrd_header, data_dict[constants.IOFields.XE_CENTER_FREQUENCY]
        )
        _write_freq_excitation(
            ismrmrd_header, data_dict[constants.IOFields.XE_DISSOLVED_OFFSET_FREQUENCY]
        )
    elif scan_type == "proton":
        _write_ramp_time(ismrmrd_header, data_dict[constants.IOFields.RAMP_TIME])
        _write_matrix_size(ismrmrd_header, data_dict[constants.IOFields.N_POINTS])
        _write_tr(
            ismrmrd_header,
            [data_dict[constants.IOFields.TR_PROTON]],
        )
        _write_flip_angle(
            ismrmrd_header,
            [data_dict[constants.IOFields.FA_PROTON]],
        )
        _write_orientation(ismrmrd_header, data_dict[constants.IOFields.ORIENTATION])
    elif scan_type == "dixon":
        _write_ramp_time(ismrmrd_header, data_dict[constants.IOFields.RAMP_TIME])
        _write_matrix_size(ismrmrd_header, data_dict[constants.IOFields.N_POINTS])
        _write_tr(
            ismrmrd_header,
            [
                data_dict[constants.IOFields.TR_GAS],
                data_dict[constants.IOFields.TR_DIS],
            ],
        )
        _write_flip_angle(
            ismrmrd_header,
            [
                data_dict[constants.IOFields.FA_GAS],
                data_dict[constants.IOFields.FA_DIS],
            ],
        )
        _write_orientation(ismrmrd_header, data_dict[constants.IOFields.ORIENTATION])
        _write_freq_center(
            ismrmrd_header, data_dict[constants.IOFields.XE_CENTER_FREQUENCY]
        )
        _write_freq_excitation(
            ismrmrd_header, data_dict[constants.IOFields.XE_DISSOLVED_OFFSET_FREQUENCY]
        )

    return ismrmrd_header


def write_acquisition_data(path: str, data_dict: Dict[str, Any]):
    """Write data from each FID acquisition according to 129Xe consortium specifications.

    Args:
        path (str): path of ismrmrd file
        data_dict (dict): dictionary of scan data and header variables

    Specifications can be found at:
        https://docs.google.com/spreadsheets/d/1SeG4K4VgA1DUrTBhSjgeSqu3UCGiCWaLG3wqHg6hBh8/edit?usp=sharing

    """

    # initialize ismrmrd data set object
    ismrmrd_data_set = ismrmrd.Dataset(path, "dataset", create_if_needed=True)

    # write to acquisition and acquisition header for each FID acquisition
    for acquisition_num in range(data_dict[constants.IOFields.FIDS].shape[0]):
        # initialize acquisition object and acquisition header
        acquisition = ismrmrd.Acquisition()
        acquisition_header = ismrmrd.AcquisitionHeader()

        # write acquisition header
        acquisition_header.number_of_samples = data_dict[constants.IOFields.N_POINTS]
        acquisition_header.active_channels = 1
        acquisition_header.trajectory_dimensions = 3
        acquisition_header.sample_time_us = data_dict[constants.IOFields.SAMPLE_TIME]
        acquisition_header.idx.contrast = int(
            data_dict[constants.IOFields.CONTRAST_LABELS][acquisition_num]
        )
        constrast_labels = int(
            data_dict[constants.IOFields.CONTRAST_LABELS][acquisition_num]
        )
        acquisition_header.idx.contrast = constrast_labels
        if (constrast_labels>0):
            acquisition_header.idx.set = int(data_dict[constants.IOFields.SET_LABELS][acquisition_num])
        acquisition_header.measurement_uid = int(
            data_dict[constants.IOFields.BONUS_SPECTRA_LABELS][acquisition_num]
        )

        # set acquisition shape and hard code required acquisition fields
        acquisition.resize(data_dict[constants.IOFields.N_POINTS], 1)
        acquisition.version = 1
        acquisition.available_channels = 1
        acquisition.center_sample = 0
        acquisition.read_dir[0] = 1.0
        acquisition.phase_dir[1] = 1.0
        acquisition.slice_dir[2] = 1.0

        # set acquisition header
        acquisition.setHead(acquisition_header)

        # write acquisition FID data
        acquisition.data[:] = data_dict[constants.IOFields.FIDS][acquisition_num, :]

        # write acquisition trajectory data
        if constants.IOFields.TRAJ in data_dict:
            if acquisition_num < data_dict[constants.IOFields.TRAJ].shape[0]:
                acquisition.traj[:] = data_dict[constants.IOFields.TRAJ][
                    acquisition_num, :, :
                ]

        # append aquisition to ismrmrd data object
        ismrmrd_data_set.append_acquisition(acquisition)

    return ismrmrd_data_set



def _write_scan_date(
    ismrmrd_header: ismrmrd.xsd.ismrmrdschema.ismrmrd.ismrmrdHeader, scan_date: str
):
    """Write AcquisitionHeaderscan date to ismrmrdHeader.

    Args:
        ismrmrd_header (ismrmrdHeader): ismrmrdHeader
        scan_date (str): scan date in 'YYYY-MM_DD' format
    """
    if type(ismrmrd_header.studyInformation) == type(None):
        ismrmrd_header.studyInformation = ismrmrd.xsd.studyInformationType()

    ismrmrd_header.studyInformation.studyDate = scan_date


def _write_subject_id(
    ismrmrd_header: ismrmrd.xsd.ismrmrdschema.ismrmrd.ismrmrdHeader, subject_id: str
):
    """Write subejct ID to ismrmrdHeader.

    Args:
        ismrmrd_header (ismrmrdHeader): ismrmrdHeader
        subject_id (str): subject ID
    """
    if type(ismrmrd_header.subjectInformation) == type(None):
        ismrmrd_header.subjectInformation = ismrmrd.xsd.subjectInformationType()

    ismrmrd_header.subjectInformation.patientID = subject_id


def _write_system_vendor(
    ismrmrd_header: ismrmrd.xsd.ismrmrdschema.ismrmrd.ismrmrdHeader, system_vendor: str
):
    """Write system vendor to ismrmrdHeader.

    Args:
        ismrmrd_header (ismrmrdHeader): ismrmrdHeader
        system_vendor (str): MRI system vendor
    """
    if type(ismrmrd_header.acquisitionSystemInformation) == type(None):
        ismrmrd_header.acquisitionSystemInformation = (
            ismrmrd.xsd.acquisitionSystemInformationType()
        )

    ismrmrd_header.acquisitionSystemInformation.systemVendor = system_vendor


def _write_institution(
    ismrmrd_header: ismrmrd.xsd.ismrmrdschema.ismrmrd.ismrmrdHeader, institution: str
):
    """Write institution to ismrmrdHeader.

    Args:
        ismrmrd_header (ismrmrdHeader): ismrmrdHeader
        institution (str): institution where scan was done
    """
    if type(ismrmrd_header.acquisitionSystemInformation) == type(None):
        ismrmrd_header.acquisitionSystemInformation = (
            ismrmrd.xsd.acquisitionSystemInformationType()
        )

    ismrmrd_header.acquisitionSystemInformation.institutionName = institution


def _write_field_strength(
    ismrmrd_header: ismrmrd.xsd.ismrmrdschema.ismrmrd.ismrmrdHeader,
    field_strength: float,
):
    """Write magnetic field strength to ismrmrdHeader.

    Args:
        ismrmrd_header (ismrmrdHeader): ismrmrdHeader
        field_strength (float): field strength of scanner in Tesla
    """
    if type(ismrmrd_header.acquisitionSystemInformation) == type(None):
        ismrmrd_header.acquisitionSystemInformation = (
            ismrmrd.xsd.acquisitionSystemInformationType()
        )

    ismrmrd_header.acquisitionSystemInformation.systemFieldStrength_T = field_strength


def _write_te(
    ismrmrd_header: ismrmrd.xsd.ismrmrdschema.ismrmrd.ismrmrdHeader,
    te: float,
):
    """Write echo time to ismrmrdHeader.

    Args:
        ismrmrd_header (ismrmrdHeader): ismrmrdHeader
        te (float): echo time in ms
    """
    if type(ismrmrd_header.sequenceParameters) == type(None):
        ismrmrd_header.sequenceParameters = ismrmrd.xsd.sequenceParametersType()

    ismrmrd_header.sequenceParameters.TE = te


def _write_ramp_time(
    ismrmrd_header: ismrmrd.xsd.ismrmrdschema.ismrmrd.ismrmrdHeader,
    ramp_time: int,
):
    """Write ramp time to ismrmrdHeader.

    Args:
        ismrmrd_header (ismrmrdHeader): ismrmrdHeader
        ramp_time (int): ramp time in us
    """

    # check a random field to see if encoding attribute was properly initialized
    if not hasattr(ismrmrd_header.encoding, "trajectoryDescription"):
        ismrmrd_header.encoding = ismrmrd.xsd.encodingType()

    if type(ismrmrd_header.encoding.trajectoryDescription) == type(None):
        ismrmrd_header.encoding.trajectoryDescription = (
            ismrmrd.xsd.trajectoryDescriptionType()
        )

    ramp_time_obj = ismrmrd.xsd.userParameterLongType(constants.IOFields.RAMP_TIME)
    ramp_time_obj.value = ramp_time
    ismrmrd_header.encoding.trajectoryDescription.userParameterLong.insert(
        0, ramp_time_obj
    )


def _write_matrix_size(
    ismrmrd_header: ismrmrd.xsd.ismrmrdschema.ismrmrd.ismrmrdHeader,
    matrix_size: int,
):
    """Write matrix size to ismrmrdHeader.

    Args:
        ismrmrd_header (ismrmrdHeader): ismrmrdHeader
        matrix_size (int): matrix size in z direction for now
    """

    # check a random field to see if encoding attribute was properly initialized
    if not hasattr(ismrmrd_header.encoding, "trajectoryDescription"):
        ismrmrd_header.encoding = ismrmrd.xsd.encodingType()

    if type(ismrmrd_header.encoding.reconSpace) == type(None):
        ismrmrd_header.encoding.reconSpace = ismrmrd.xsd.encodingSpaceType()

    matrix_size_obj = ismrmrd.xsd.matrixSizeType()
    matrix_size_obj.z = matrix_size
    ismrmrd_header.encoding.reconSpace.matrixSize = matrix_size_obj


def _write_fov(
    ismrmrd_header: ismrmrd.xsd.ismrmrdschema.ismrmrd.ismrmrdHeader,
    fov: float,
):
    """Write field of view to ismrmrdHeader.

    Args:
        ismrmrd_header (ismrmrdHeader): ismrmrdHeader
        fov (float): field of view in x, y, and z directions in mm

    NOTE: for now, function requires only one input and assumes same fov in all directions
    """

    # check a random field to see if encoding attribute was properly initialized
    if not hasattr(ismrmrd_header.encoding, "trajectoryDescription"):
        ismrmrd_header.encoding = ismrmrd.xsd.encodingType()

    if type(ismrmrd_header.encoding.reconSpace) == type(None):
        ismrmrd_header.encoding.reconSpace = ismrmrd.xsd.encodingSpaceType()

    fov_obj = ismrmrd.xsd.fieldOfViewMm()
    fov_obj.x = fov
    fov_obj.y = fov
    fov_obj.z = fov
    ismrmrd_header.encoding.reconSpace.fieldOfView_mm = fov_obj


def _write_tr(
    ismrmrd_header: ismrmrd.xsd.ismrmrdschema.ismrmrd.ismrmrdHeader,
    tr: list,
):
    """Write TR values to ismrmrdHeader.

    Args:
        ismrmrd_header (ismrmrdHeader): ismrmrdHeader
        tr (list): list of TR values in ms, written in order of array
    """

    if type(ismrmrd_header.sequenceParameters) == type(None):
        ismrmrd_header.sequenceParameters = ismrmrd.xsd.sequenceParametersType()

    ismrmrd_header.sequenceParameters.TR = tr


def _write_flip_angle(
    ismrmrd_header: ismrmrd.xsd.ismrmrdschema.ismrmrd.ismrmrdHeader,
    flip_angle: list,
):
    """Write flip angle values to ismrmrdHeader.

    Args:
        ismrmrd_header (ismrmrdHeader): ismrmrdHeader
        flip_angle (list): list of flip angles in degrees, written in order of array
    """

    if type(ismrmrd_header.sequenceParameters) == type(None):
        ismrmrd_header.sequenceParameters = ismrmrd.xsd.sequenceParametersType()

    ismrmrd_header.sequenceParameters.flipAngle_deg = flip_angle


def _write_freq_center(
    ismrmrd_header: ismrmrd.xsd.ismrmrdschema.ismrmrd.ismrmrdHeader,
    freq_center: int,
):
    """Write 129Xe center frequency to ismrmrdHeader.

    Args:
        ismrmrd_header (ismrmrdHeader): ismrmrdHeader
        freq_center (int): center frequency of 129Xe in the gas phase in Hz
    """
    if type(ismrmrd_header.userParameters) == type(None):
        ismrmrd_header.userParameters = ismrmrd.xsd.userParametersType()

    freq_center_obj = ismrmrd.xsd.userParameterLongType(
        constants.IOFields.XE_CENTER_FREQUENCY
    )
    freq_center_obj.value = freq_center
    ismrmrd_header.userParameters.userParameterLong.insert(0, freq_center_obj)


def _write_freq_excitation(
    ismrmrd_header: ismrmrd.xsd.ismrmrdschema.ismrmrd.ismrmrdHeader,
    freq_excitation: int,
):
    """Write dissolved phase frequency offset to ismrmrdHeader.

    Args:
        ismrmrd_header (ismrmrdHeader): ismrmrdHeader
        freq_excitation (int): dissolved phase frequency minus center frequency, in Hz
    """
    if type(ismrmrd_header.userParameters) == type(None):
        ismrmrd_header.userParameters = ismrmrd.xsd.userParametersType()

    freq_excitation_obj = ismrmrd.xsd.userParameterLongType(
        constants.IOFields.XE_DISSOLVED_OFFSET_FREQUENCY
    )
    freq_excitation_obj.value = freq_excitation
    ismrmrd_header.userParameters.userParameterLong.insert(1, freq_excitation_obj)


def _write_orientation(
    ismrmrd_header: ismrmrd.xsd.ismrmrdschema.ismrmrd.ismrmrdHeader,
    orientation: str,
):
    """Write orientation to ismrmrdHeader.

    Args:
        ismrmrd_header (ismrmrdHeader): ismrmrdHeader
        orientation (str): orientation of reconstructed image
    """
    if type(ismrmrd_header.userParameters) == type(None):
        ismrmrd_header.userParameters = ismrmrd.xsd.userParametersType()

    orientation_obj = ismrmrd.xsd.userParameterStringType(
        constants.IOFields.ORIENTATION
    )
    orientation_obj.value = orientation
    ismrmrd_header.userParameters.userParameterString.insert(0, orientation_obj)
