"""Define important constants used throughout the pipeline."""
import enum

import numpy as np

FOVINFLATIONSCALE3D = 1000.0

_DEFAULT_SLICE_THICKNESS = 3.125
_DEFAULT_PIXEL_SIZE = 3.125
_DEFAULT_MAX_IMG_VALUE = 255.0

_RAYLEIGH_FACTOR = 0.66
GRYOMAGNETIC_RATIO = 11.777  # MHz/T
_VEN_PERCENTILE_RESCALE = 99.0
_VEN_PERCENTILE_THRESHOLD_SEG = 80
_PROTON_PERCENTILE_RESCALE = 99.8

KCO_ALPHA = 11.2  # membrane
KCO_BETA = 14.6  # RBC
VA_ALPHA = 1.43


class IOFields(object):
    """General IOFields constants."""

    BANDWIDTH = "bandwidth"
    BIASFIELD_KEY = "biasfield_key"
    BONUS_SPECTRA_LABELS = "bonus_spectra_labels"
    CONTRAST_LABELS = "contrast_labels"
    SET_LABELS = "set_labels"
    NUMBER_OF_ECHO = "number_of_echo"
    SAMPLE_TIME = "sample_time"
    FA_PROTON = "fa_proton"
    FA_DIS = "fa_dis"
    FA_GAS = "fa_gas"
    FIDS = "fids"
    FIDS_DIS = "fids_dis"
    FIDS_GAS = "fids_gas"
    FIELD_STRENGTH = "field_strength"
    FLIP_ANGLE_FACTOR = "flip_angle_factor"
    FOV = "fov"
    XE_CENTER_FREQUENCY = "xe_center_frequency"
    XE_DISSOLVED_OFFSET_FREQUENCY = "xe_dissolved_offset_frequency"
    GIT_BRANCH = "git_branch"
    GRAD_DELAY_X = "grad_delay_x"
    GRAD_DELAY_Y = "grad_delay_y"
    GRAD_DELAY_Z = "grad_delay_z"
    HB_CORRECTION_KEY = "hb_correction_key"
    HB = "hb"
    INSTITUTION = "institution"
    RBC_HB_CORRECTION_FACTOR = "rbc_hb_correction_factor"
    MEMBRANE_HB_CORRECTION_FACTOR = "membrane_hb_correction_factor"
    KERNEL_SHARPNESS = "kernel_sharpness"
    N_FRAMES = "n_frames"
    N_SKIP_END = "n_skip_end"
    N_SKIP_START = "n_skip_start"
    N_DIS_REMOVED = "n_dis_removed"
    N_GAS_REMOVED = "n_gas_removed"
    N_POINTS = "n_points"
    ORIENTATION = "orientation"
    PIPELINE_VERSION = "pipeline_version"
    PROCESS_DATE = "process_date"
    PROTOCOL_NAME = "protocol_name"
    RAMP_TIME = "ramp_time"
    REFERENCE_DATA_KEY = "reference_data_key"
    REGISTRATION_KEY = "registration_key"
    REMOVEOS = "removeos"
    REMOVE_NOISE = "remove_noise"
    SCAN_DATE = "scan_date"
    SCAN_TYPE = "scan_type"
    SEGMENTATION_KEY = "segmentation_key"
    SHAPE_FIDS = "shape_fids"
    SHAPE_IMAGE = "shape_image"
    SLICE_THICKNESS = "slice_thickness"
    SOFTWARE_VERSION = "software_version"
    SUBJECT_ID = "subject_id"
    SYSTEM_VENDOR = "system_vendor"
    T2_CORRECTION_FACTOR = "t2_correction_factor"
    TE = "te"
    TR_PROTON = "tr_proton"
    TR_GAS = "tr_gas"
    TR_DIS = "tr_dis"
    TRAJ = "traj"
    TRAJ_GAS = "traj_gas"
    TRAJ_DIS = "traj_dis"
    TRAJ_PROTON = "traj_proton"


class ImageType(enum.Enum):
    """Segmentation flags."""

    VENT = "vent"
    UTE = "ute"


class ScanType(enum.Enum):
    """Scan type."""

    NORMALDIXON = "normal"
    MEDIUMDIXON = "medium"
    FASTDIXON = "fast"


class Institution(enum.Enum):
    """Institution name."""

    DUKE = "duke"
    UVA = "uva"


class SystemVendor(enum.Enum):
    """Scanner system_vendor."""

    SIEMENS = "siemens"


class TrajType(object):
    """Trajectory type."""

    SPIRAL = "spiral"
    HALTON = "halton"
    HALTONSPIRAL = "haltonspiral"
    SPIRALRANDOM = "spiralrandom"
    ARCHIMEDIAN = "archimedian"
    GOLDENMEAN = "goldenmean"


class Orientation(object):
    """Image orientation."""

    CORONAL = "coronal"
    AXIAL = "axial"
    TRANSVERSE = "transverse"
    CORONAL_CCHMC = "coronal_cchmc"
    NONE = "none"


class ContrastLabels(object):
    """Numbers for labelling type of FID acquisition excitation."""

    PROTON = 0  # proton acquisition
    GAS = 1  # gas phase 129Xe acquisition
    DISSOLVED = 2  # dissolved phase 129Xe acquisition


class BonusSpectraLabels(object):
    """Numbers for labelling if FID acquisition is part of bonus spectra."""

    NOT_BONUS = 0  # not part of bonus spectra
    BONUS = 1  # part of bonus spectra
