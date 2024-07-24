"""Base configuration file."""
import sys

import numpy as np
from ml_collections import config_dict

# parent directory
sys.path.append("..")

from utils import constants


class Config(config_dict.ConfigDict):
    """Base config file.

    Attributes:
        data_dir (str): path to the data directory
        subject_id (str): the subject id
        recon (Recon): object containing reconstruction configurations for trajectory generation
        calibration (Calibration); object containing calibration sequence configurations
        dixon (Dixon): object containing Dixon sequence configurations
        proton (Proton): object containing proton sequence configurations
    """

    def __init__(self):
        """Initialize config parameters."""
        super().__init__()
        self.recon = Recon()
        self.calibration = Calibration()
        self.dixon = Dixon()
        self.proton = Proton()
        self.data_dir = ""
        self.subject_id = "test"
        self.multi_echo = False


class Recon(object):
    """Define dixon and proton image reconstruction configurations.

    Attributes:
        recon_size (int)
        matrix_size (int)
    """

    def __init__(self):
        """Initialize the reconstruction parameters."""
        self.recon_size = 64
        self.matrix_size = 128


class Calibration(object):
    """Define calibration sequence configurations.

    Attributes:
        num_gas_fids (int): number of gas FID acquisitions at end of sequence
    """

    def __init__(self):
        self._ = 0


class Dixon(object):
    """Define Dixon sequence configurations."""

    def __init__(self):
        self._ = 0


class Proton(object):
    """Define proton sequence configurations."""

    def __init__(self):
        self._ = 0


def get_config() -> config_dict.ConfigDict:
    """Return the config dict. This is a required function.

    Returns:
        a ml_collections.config_dict.ConfigDict
    """
    return Config()
