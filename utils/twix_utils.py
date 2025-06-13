"""Twix file util functions."""

import logging
import sys

sys.path.append("..")
import datetime
from typing import Any, Dict

import mapvbvd
import numpy as np

from utils import constants


def get_scan_date(twix_obj: mapvbvd._attrdict.AttrDict) -> str:
    """Get the scan date in MM-DD-YYYY format.

    Args:
        twix_obj: twix object returned from mapVBVD function
    Returns:
        scan date string in MM-DD-YYYY format
    """
    try:
        tReferenceImage0 = str(twix_obj.hdr.MeasYaps[("tReferenceImage0",)]).strip('"')
        scan_date = tReferenceImage0.split(".")[-1][:8]
    except:
        SeriesLOID = twix_obj.hdr.Config[("SeriesLOID")]
        scan_date = SeriesLOID.split(".")[-4][:8]
    return scan_date[:4] + "-" + scan_date[4:6] + "-" + scan_date[6:]


def get_system_vendor(twix_obj: mapvbvd._attrdict.AttrDict) -> str:
    """Get system vendor.

    Args:
        twix_obj: twix object returned from mapVBVD function
    Returns:
        system_vendor: vendor of MRI scanner
    """
    return twix_obj.hdr.Dicom.Manufacturer


def get_institution(twix_obj: mapvbvd._attrdict.AttrDict) -> str:
    """Get institution.

    Args:
        twix_obj: twix object returned from mapVBVD function
    Returns:
        institution: institution where subject was scanned
    """
    return twix_obj.hdr.Dicom.InstitutionName


def get_dwell_time(twix_obj: mapvbvd._attrdict.AttrDict) -> float:
    """Get the dwell time in us.

    Args:
        twix_obj: twix object returned from mapVBVD function
    Returns:
        dwell time in us
    """
    try:
        return float(twix_obj.hdr.Phoenix[("sRXSPEC", "alDwellTime", "0")]) * 1e-3
    except:
        pass
    try:
        return float(twix_obj.hdr.Meas.alDwellTime.split(" ")[0]) * 1e-3
    except:
        pass
    raise ValueError("Could not find dwell time from twix object")


def get_TR(twix_obj: mapvbvd._attrdict.AttrDict) -> float:
    """Get the TR in ms.

    Args:
        twix_obj: twix object returned from mapVBVD function
    Returns:
        TR in  ms
    """
    try:
        return float(twix_obj.hdr.Config.TR.split(" ")[0]) * 1e-3
    except:
        pass

    try:
        return float(twix_obj.hdr.Phoenix[("alTR", "0")]) * 1e-3
    except:
        pass

    raise ValueError("Could not find TR from twix object")


def get_TR_dissolved(twix_obj: mapvbvd._attrdict.AttrDict) -> float:
    """Get the TR in seconds for dissolved phase.

    The dissolved phase TR is defined to be the time between two consecutive dissolved
    phase-FIDS. This is different from the TR in the twix header as the twix header
    provides the TR for two consecutive FIDS. Here, we assume an interleaved sequence.

    Args:
        twix_obj: twix object returned from mapVBVD function
    Returns:
        TR in seconds
    """
    try:
        return float(twix_obj.hdr.Config.TR) * 1e-3
    except:
        pass
    try:
        return float(twix_obj.hdr.Config.TR.split(" ")[0]) * 1e-3
    except:
        pass

    raise ValueError("Could not find TR from twix object")


def get_center_freq(twix_obj: mapvbvd._attrdict.AttrDict) -> float:
    """Get the center frequency in MHz.

    See: https://mriquestions.com/center-frequency.html for definition of center freq.

    Args:
        twix_obj: twix object returned from mapVBVD function.
    Returns:
        center frequency in Hz.
    """
    try:
        return int(twix_obj.hdr.Dicom["lFrequency"])
    except:
        pass

    try:
        return twix_obj.hdr.Meas.lFrequency
    except:
        pass

    raise ValueError("Could not find center frequency (MHz) from twix object")


def get_excitation_freq(twix_obj: mapvbvd._attrdict.AttrDict) -> float:
    """Get the excitation frequency in Hz.

    Args:
        twix_obj: twix object returned from mapVBVD function.
    Returns:
        rf excitation frequency in Hz
    """

    try:
        return twix_obj.hdr.Phoenix["sWipMemBlock", "alFree", "4"]
    except:
        try:
            return twix_obj.hdr.MeasYaps[("sWiPMemBlock", "adFree", "8")]
        except:
            ValueError("Could not get excitation frequency from twix object.")


def get_field_strength(twix_obj: mapvbvd._attrdict.AttrDict) -> float:
    """Get the magnetic field strength in Tesla.

    Args:
        twix_obj: twix object returned from mapVBVD function.
    Returns:
        magnetic field strength in Tesla.
    """
    try:
        field_strength = twix_obj.hdr.Dicom.flMagneticFieldStrength
    except:
        logging.warning("Could not find magnetic field strength, using 3T.")
        field_strength = 3.0
    return field_strength


def get_ramp_time(twix_obj: mapvbvd._attrdict.AttrDict) -> float:
    """Get the ramp time in micro-seconds.

    See: https://mriquestions.com/gradient-specifications.html

    Args:
        twix_obj: twix object returned from mapVBVD function.
    Returns:
        ramp time in us
    """
    ramp_time = 0.0
    scan_date = get_scan_date(twix_obj=twix_obj)
    YYYY, MM, DD = scan_date.split("-")
    scan_datetime = datetime.datetime(int(YYYY), int(MM), int(DD))

    try:
        ramp_time = float(twix_obj.hdr.Meas.RORampTime)
        if scan_datetime > datetime.datetime(2018, 9, 21):
            return ramp_time
    except:
        pass

    try:
        ramp_time = float(twix_obj["hdr"]["Meas"]["alRegridRampupTime"].split()[0])
    except:
        pass

    return max(100, ramp_time) if ramp_time < 100 else ramp_time


def get_flag_removeOS(twix_obj: mapvbvd._attrdict.AttrDict) -> bool:
    """Get the flag to remove oversampling.

    Returns false by default.

    Args:
        twix_obj: twix object returned from mapVBVD function.
    Returns:
        flag to remove oversampling
    """
    try:
        return twix_obj.image.flagRemoveOS
    except:
        return False


def get_software_version(twix_obj: mapvbvd._attrdict.AttrDict) -> str:
    """Get the software version.

    Args:
        twix_obj: twix object returned from mapVBVD function.
    Returns:
        software version
    """
    try:
        return twix_obj.hdr.Dicom.SoftwareVersions
    except:
        pass

    return "unknown"


def get_FOV(twix_obj: mapvbvd._attrdict.AttrDict) -> float:
    """Get the FOV in mm.

    Args:
        twix_obj: twix object returned from mapVBVD function.
    Returns:
        FOV in cm. 40cm if not found.
    """
    try:
        return float(twix_obj.hdr.Config.ReadFoV)
    except:
        pass
    logging.warning("Could not find FOV from twix object. Returning 400mm.")
    return 400.0


def get_TE(twix_obj: mapvbvd._attrdict.AttrDict, multi_echo_flag: str = "single_echo") -> float:
    """Get the te in ms.

    Args:
        twix_obj: twix object returned from mapVBVD function.
        multi_echo_flag: multi-echo flag from config file
    Returns:
        te in ms
    """
    if multi_echo_flag == "multi_echo_2":
        return [
            twix_obj.hdr.Phoenix[("alTE", "8")] * 1e-3, twix_obj.hdr.Phoenix[("alTE", "9")] * 1e-3,
            twix_obj.hdr.Phoenix[("alTE","10")] * 1e-3
            ]
    elif multi_echo_flag == "multi_echo":
        return [twix_obj.hdr.Phoenix[("alTE", "0")] * 1e-3, twix_obj.hdr.Phoenix[("alTE", "1")] * 1e-3]
    elif multi_echo_flag == "single_echo":
        return twix_obj.hdr.Phoenix[("alTE", "0")] * 1e-3
    else:
        raise ValueError("Unable to find TE in twix object.")


def get_flipangle_dissolved(twix_obj: mapvbvd._attrdict.AttrDict, multi_echo_flag: str = "single_echo") -> float:
    """Get the dissolved phase flip angle in degrees.

    Args:
        twix_obj: twix object returned from mapVBVD function.
        multi_echo_flag: multi-echo flag from config file
    Returns:
        flip angle in degrees
    """
    if multi_echo_flag == "multi_echo_2" or multi_echo_flag == "multi_echo":
        try:
            return float(twix_obj.hdr.MeasYaps[("adFlipAngleDegree", "2")])
        except:
            raise ValueError("Unable to find dissolved-phase flip angle in twix object.")

    elif multi_echo_flag == "single_echo":
        try:
            return float(twix_obj.hdr.MeasYaps[("adFlipAngleDegree", "1")])
        except:
            raise ValueError("Unable to find dissolved-phase flip angle in twix object.")
        
    else:
        raise ValueError("Unable to find dissolved-phase flip angle in twix object.")


def get_flipangle_gas(twix_obj: mapvbvd._attrdict.AttrDict) -> float:
    """Get the gas phase flip angle in degrees.

    Args:
        twix_obj: twix object returned from mapVBVD function.
    Returns:
        flip angle in degrees. Returns 0.5 degrees if not found.
    """
    try:
        return float(twix_obj.hdr.Meas["adFlipAngleDegree"].split(" ")[0])
    except:
        pass
    try:
        assert float(twix_obj.hdr.MeasYaps[("adFlipAngleDegree", "0")]) < 10.0
        return float(twix_obj.hdr.MeasYaps[("adFlipAngleDegree", "0")])
    except:
        pass
    try:
        return float(twix_obj.hdr.MeasYaps[("sWipMemBlock", "adFree", "5")])
    except:
        pass
    try:
        return float(twix_obj.hdr.MeasYaps[("sWiPMemBlock", "adFree", "5")])
    except:
        pass
    logging.info("Returning default flip angle of 0.5 degrees.")
    return 0.5


def get_flipangle_proton(twix_obj: mapvbvd._attrdict.AttrDict) -> float:
    """Get the gas phase flip angle in degrees.

    Args:
        twix_obj: twix object returned from mapVBVD function.
    Returns:
        flip angle in degrees. Returns 5 degrees if not found.
    """
    try:
        return float(twix_obj.hdr.Meas["adFlipAngleDegree"].split(" ")[0])
    except:
        pass
    try:
        assert float(twix_obj.hdr.MeasYaps[("adFlipAngleDegree", "0")]) < 10.0
        return float(twix_obj.hdr.MeasYaps[("adFlipAngleDegree", "0")])
    except:
        pass
    try:
        return float(twix_obj.hdr.MeasYaps[("sWipMemBlock", "adFree", "5")])
    except:
        pass
    try:
        return float(twix_obj.hdr.MeasYaps[("sWiPMemBlock", "adFree", "5")])
    except:
        pass
    logging.info("Returning default flip angle of 5 degrees.")
    return 5


def get_orientation(twix_obj: mapvbvd._attrdict.AttrDict) -> str:
    """Get the orientation of the image.

    Args:
        twix_obj: twix object returned from mapVBVD function.
    Returns:
        orientation. Returns coronal if not found.
    """
    orientation = ""
    try:
        orientation = str(twix_obj.hdr.Dicom.tOrientation)
    except:
        logging.info("Unable to find orientation from twix object, returning coronal.")
    return orientation.lower() if orientation else constants.Orientation.CORONAL


def get_protocol_name(twix_obj: mapvbvd._attrdict.AttrDict) -> str:
    """Get the protocol name.

    Args:
        twix_obj: twix object returned from mapVBVD function.
    Returns:
        protocol name. Returns "unknown" if not found.
    """
    try:
        return str(twix_obj.hdr.Config.ProtocolName)
    except:
        return "unknown"


def get_dyn_data(
    twix_obj: mapvbvd._attrdict.AttrDict, n_skip_end: int = 20
) -> np.ndarray:
    """Get the dissolved phase FIDS used for dyn. spectroscopy from twix object.

    Args:
        twix_obj: twix object returned from mapVBVD function
    Returns:
        TODO
    """
    # get raw FIDs
    raw_fids = np.transpose(twix_obj.image[""].astype(np.cdouble))

    # get contrast labels, hard code for now until we fiure out how to read this from twix file
    num_calibration_gas_fids = 20
    contrast_labels = np.zeros(raw_fids.shape[0])
    contrast_labels[:-num_calibration_gas_fids] = constants.ContrastLabels.DISSOLVED
    contrast_labels[-num_calibration_gas_fids:] = constants.ContrastLabels.GAS

    # get bonus spectra labels
    bonus_spectra_labels = (
        np.ones(raw_fids.shape[0]) * constants.BonusSpectraLabels.NOT_BONUS
    )
    set_labels = np.ones(raw_fids.shape[0]) 
    
    return {
        constants.IOFields.FIDS: raw_fids,
        constants.IOFields.CONTRAST_LABELS: contrast_labels,
        constants.IOFields.SET_LABELS: set_labels,
        constants.IOFields.BONUS_SPECTRA_LABELS: bonus_spectra_labels,
        constants.IOFields.N_FRAMES: raw_fids.shape[0],
        constants.IOFields.N_POINTS: raw_fids.shape[1],
    }


def get_bandwidth(
    twix_obj: mapvbvd._attrdict.AttrDict, data_dict: Dict[str, Any], filename: str
    ) -> float:
    """Get the bandwidth in Hz/pixel.

    If the filename contains "BW", then this is a Ziyi-era sequence and the bandwidth
    must be calculated differently.

    Args:
        twix_obj: twix object returned from mapVBVD function.
        data_dict: dictionary containing the output of get_gx_data function.
        filename: filename of the twix file.
    Returns:
        bandwidth in Hz/pixel
    """
    sample_time = get_dwell_time(twix_obj=twix_obj)
    npts = data_dict[constants.IOFields.FIDS_DIS].shape[1]
    return (
        1.0 / (2 * sample_time * npts)
        if "BW" not in filename
        else 1.0 / (2 * npts * sample_time / 2)
    )


def get_bonus_number_gas(
    twix_obj: mapvbvd._attrdict.AttrDict, multi_echo_flag: str = "single_echo"
    ) -> int:
    """Get number of gas bonus spectra

    Args:
        twix_obj: twix object returned from mapVBVD function.
        multi_echo_flag: multi-echo flag from config file
    Returns:
        number of bonus spectra
    """
    if multi_echo_flag == "single_echo" or multi_echo_flag == "multi_echo":
        bonus_number_gas = int(twix_obj.hdr.MeasYaps[("sWipMemBlock", "adFree", "10")])
    elif multi_echo_flag == "multi_echo_2":
        bonus_number_gas = int(twix_obj.hdr.MeasYaps[("sWipMemBlock", "adFree", "9")])
    else:
        raise ValueError("Unable to extract number of gas bonus spectra.")
    
    return bonus_number_gas


def get_bonus_number_dissolved(
    twix_obj: mapvbvd._attrdict.AttrDict, multi_echo_flag: str = "single_echo"
    ) -> int:
    """Get number of dissolved bonus spectra

    Args:
        twix_obj: twix object returned from mapVBVD function.
        multi_echo_flag: multi-echo flag from config file
    Returns:
        number of dissolved bonus spectra
    """
    if multi_echo_flag == "single_echo" or multi_echo_flag == "multi_echo":
        bonus_number_dissolved = int(twix_obj.hdr.MeasYaps[("sWipMemBlock", "adFree", "5")])
    elif multi_echo_flag == "multi_echo_2":
        bonus_number_dissolved = int(twix_obj.hdr.MeasYaps[("sWipMemBlock","adFree","3")])
    else:
        raise ValueError("Unable to extract number of dissolved bonus spectra.")
    
    return bonus_number_dissolved


def get_gx_data(twix_obj: mapvbvd._attrdict.AttrDict) -> Dict[str, Any]:
    """Get the dissolved phase and gas phase FIDs from twix object.

    For reconstruction, we also need important information like the gradient delay,
    number of fids in each phase, etc. Note, this cannot be trivially read from the
    twix object, and need to hard code some values. For example, the gradient delay
    is slightly different depending on the scanner.
    Args:
        twix_obj: twix object returned from mapVBVD function
    Returns:
        TODO
    """
    raw_fids = np.transpose(twix_obj.image.unsorted().astype(np.cdouble))
    contrast_labels = np.zeros(raw_fids.shape[0])
    set_labels = np.ones(raw_fids.shape[0])
    bonus_spectra_labels = (
        np.ones(raw_fids.shape[0]) * constants.BonusSpectraLabels.NOT_BONUS
    )

    # extract number of bonus spectra
    bonus_number_gas = get_bonus_number_gas(twix_obj, "single_echo")
    bonus_number_dissolved = get_bonus_number_dissolved(twix_obj, "single_echo")
    bonus_number = bonus_number_gas + bonus_number_dissolved

    # read in data
    contrast_labels[0:-bonus_number:2] = constants.ContrastLabels.GAS
    contrast_labels[1:-bonus_number:2] = constants.ContrastLabels.DISSOLVED
    contrast_labels[-bonus_number_gas:] = constants.ContrastLabels.GAS
    contrast_labels[-bonus_number:-bonus_number_gas] = constants.ContrastLabels.DISSOLVED

    # set bonus spectra labels
    bonus_spectra_labels[-bonus_number:] = constants.BonusSpectraLabels.BONUS

    # extract gas and dissolved phase fids (minus bonus spectra)
    data_gas = raw_fids[:-bonus_number][
        contrast_labels[:-bonus_number] == constants.ContrastLabels.GAS
    ]
    data_dis = raw_fids[:-bonus_number][
        contrast_labels[:-bonus_number] == constants.ContrastLabels.DISSOLVED
    ]

    # define number of frames and gradient delay
    n_frames = int((raw_fids.shape[0] - bonus_number) / 2)
    
    return {
        constants.IOFields.FIDS: raw_fids,
        constants.IOFields.FIDS_GAS: data_gas,
        constants.IOFields.FIDS_DIS: data_dis,
        constants.IOFields.CONTRAST_LABELS: contrast_labels,
        constants.IOFields.SET_LABELS: set_labels,
        constants.IOFields.BONUS_SPECTRA_LABELS: bonus_spectra_labels,
        constants.IOFields.N_FRAMES: n_frames,
        constants.IOFields.NUMBER_OF_ECHO: 1,
    }

def get_gx_data_multi_echo(twix_obj: mapvbvd._attrdict.AttrDict) -> Dict[str, Any]:
    """Get the dissolved phase and gas phase FIDs from twix object.

    For reconstruction, we also need important information like the gradient delay,
    number of fids in each phase, etc. Note, this cannot be trivially read from the
    twix object, and need to hard code some values. For example, the gradient delay
    is slightly different depending on the scanner.
    Args:
        twix_obj: twix object returned from mapVBVD function
    Returns:
        TODO
    """
    raw_fids = np.transpose(twix_obj.image.unsorted().astype(np.cdouble))
    contrast_labels = np.zeros(raw_fids.shape[0])
    set_labels = np.zeros(raw_fids.shape[0])
    bonus_spectra_labels = (
        np.ones(raw_fids.shape[0]) * constants.BonusSpectraLabels.NOT_BONUS
    )

    logging.info(get_TE(twix_obj,"multi_echo"))    

    # extract number of bonus spectra
    bonus_number_gas = get_bonus_number_gas(twix_obj, "multi_echo")
    bonus_number_dissolved = get_bonus_number_dissolved(twix_obj, "multi_echo")
    bonus_number = bonus_number_gas + bonus_number_dissolved

    # set bonus spectra labels
    bonus_spectra_labels[-bonus_number:] = constants.BonusSpectraLabels.BONUS
    contrast_labels[0:-bonus_number:4] = constants.ContrastLabels.GAS
    contrast_labels[1:-bonus_number:4] = constants.ContrastLabels.GAS
    contrast_labels[2:-bonus_number:4] = constants.ContrastLabels.DISSOLVED
    contrast_labels[3:-bonus_number:4] = constants.ContrastLabels.DISSOLVED
                
    set_labels [-bonus_number:] = 1
    set_labels[0:-bonus_number:4] = 1
    set_labels[1:-bonus_number:4] = 2
    set_labels[2:-bonus_number:4] = 1
    set_labels[3:-bonus_number:4] = 2

    n_frames = int((raw_fids.shape[0] - bonus_number) / 4)
    data_gas = raw_fids[
        contrast_labels == constants.ContrastLabels.GAS
    ]
    data_dis = raw_fids[
        contrast_labels== constants.ContrastLabels.DISSOLVED
    ]

    return {
        constants.IOFields.FIDS: raw_fids,
        constants.IOFields.FIDS_GAS: data_gas,
        constants.IOFields.FIDS_DIS: data_dis,
        constants.IOFields.CONTRAST_LABELS: contrast_labels,
        constants.IOFields.SET_LABELS: set_labels,
        constants.IOFields.BONUS_SPECTRA_LABELS: bonus_spectra_labels,
        constants.IOFields.N_FRAMES: n_frames,
        constants.IOFields.NUMBER_OF_ECHO: 2
    }


def get_gx_data_multi_echo_2(twix_obj: mapvbvd._attrdict.AttrDict) -> Dict[str, Any]:
    """Get the dissolved phase and gas phase FIDs from twix object.
    Initially written for DixonXP_2501_KUMC sequence

    For reconstruction, we also need important information like the gradient delay,
    number of fids in each phase, etc. Note, this cannot be trivially read from the
    twix object, and need to hard code some values. For example, the gradient delay
    is slightly different depending on the scanner.
    Args:
        twix_obj: twix object returned from mapVBVD function
    Returns:
        TODO
    """
    raw_fids = np.transpose(twix_obj.image.unsorted().astype(np.cdouble))
    contrast_labels = np.zeros(raw_fids.shape[0])
    set_labels = np.zeros(raw_fids.shape[0])
    bonus_spectra_labels = (
        np.ones(raw_fids.shape[0]) * constants.BonusSpectraLabels.NOT_BONUS
    )

    logging.info(get_TE(twix_obj,"multi_echo_2"))  

    # extract number of bonus spectra
    bonus_number_gas = get_bonus_number_gas(twix_obj, "multi_echo_2")
    bonus_number_dissolved = get_bonus_number_dissolved(twix_obj, "multi_echo_2")
    bonus_number = bonus_number_gas + bonus_number_dissolved

    # set bonus spectra labels
    number_of_echo = int(twix_obj.hdr.Phoenix[("alTR", "4")])

    bonus_spectra_labels[-bonus_number:] = constants.BonusSpectraLabels.BONUS
    contrast_labels[0:-bonus_number:5] = constants.ContrastLabels.GAS
    contrast_labels[1:-bonus_number:5] = constants.ContrastLabels.GAS
    contrast_labels[2:-bonus_number:5] = constants.ContrastLabels.DISSOLVED
    contrast_labels[3:-bonus_number:5] = constants.ContrastLabels.DISSOLVED
    contrast_labels[4:-bonus_number:5] = constants.ContrastLabels.DISSOLVED
                
    set_labels [-bonus_number:] = 1
    set_labels[0:-bonus_number:5] = 1
    set_labels[1:-bonus_number:5] = 2
    set_labels[2:-bonus_number:5] = 1
    set_labels[3:-bonus_number:5] = 2
    set_labels[4:-bonus_number:5] = 3

    n_frames = int((raw_fids.shape[0] - bonus_number) / 5)
    data_gas = raw_fids[
        contrast_labels == constants.ContrastLabels.GAS
    ]
    data_dis = raw_fids[
        contrast_labels== constants.ContrastLabels.DISSOLVED
    ]

    return {
        constants.IOFields.FIDS: raw_fids,
        constants.IOFields.FIDS_GAS: data_gas,
        constants.IOFields.FIDS_DIS: data_dis,
        constants.IOFields.CONTRAST_LABELS: contrast_labels,
        constants.IOFields.SET_LABELS: set_labels,
        constants.IOFields.BONUS_SPECTRA_LABELS: bonus_spectra_labels,
        constants.IOFields.N_FRAMES: n_frames,
        constants.IOFields.NUMBER_OF_ECHO: number_of_echo
    }


def get_ute_data(twix_obj: mapvbvd._attrdict.AttrDict) -> Dict[str, Any]:
    """Get the UTE FIDs from twix object.

    Args:
        twix_obj: twix object returned from mapVBVD function
    Returns:
        TODO

    For reconstruction, we also need important information like the gradient delay,
    number of fids in each phase, etc. Note, this cannot be trivially read from the
    twix object, and need to hard code some values. For example, the gradient delay
    is slightly different depending on the scanner.
    """
    raw_fids = np.array(twix_obj.image.unsorted().astype(np.cdouble))

    if raw_fids.ndim == 3:
        raw_fids = np.squeeze(raw_fids[:, 0, :])

    if raw_fids.shape[1] == 4601:
        # For some reason, the raw data is 4601 points long. We need to remove the
        # last projection.
        raw_fids = raw_fids[:, :4600]
        nframes = 4601
    elif raw_fids.shape[1] == 4630:
        # bonus spectra at the end
        raw_fids = raw_fids[:, :4600]
        nframes = 4600
    else:
        nframes = raw_fids.shape[1]

    raw_fids = np.transpose(raw_fids)

    # generate contrast labels
    contrast_labels = np.zeros(raw_fids.shape[0])

    # get bonus spectra labels
    bonus_spectra_labels = (
        np.ones(raw_fids.shape[0]) * constants.BonusSpectraLabels.NOT_BONUS
    )

    return {
        constants.IOFields.CONTRAST_LABELS: contrast_labels,
        constants.IOFields.BONUS_SPECTRA_LABELS: bonus_spectra_labels,
        constants.IOFields.FIDS: raw_fids,
        constants.IOFields.N_FRAMES: nframes,
    }
