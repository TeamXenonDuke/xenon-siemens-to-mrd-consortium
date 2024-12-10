"""Base configuration file."""
import sys

import numpy as np
from ml_collections import config_dict

# parent directory
sys.path.append("..")

from config import base_config
from utils import constants


class Config(base_config.Config):
    """Base config file.

    Attributes:
        data_dir: str, path to the data directory
        subject_id: str, the subject id
    """

    def __init__(self):
        """Initialize config parameters."""
        super().__init__()
        self.data_dir = "/Users/MyName/Documents/patients/007-005B/"
        self.subject_id = "007-005B"
        self.recon = Recon()
        self.dixon = Dixon()
        self.proton = Proton()


class Recon(base_config.Recon):
    """Define dixon and proton image reconstruction configurations.

    Attributes:
        recon_size (int)
        matrix_size (int)
    """

    def __init__(self):
        """Initialize the reconstruction parameters."""
        super().__init__()
        self.recon_size = 64
        self.matrix_size = 128

class Dixon(object):
    """Define Dixon sequence configurations."""

    def __init__(self):
        self._ = 0
        self.gradient_delay_x = -5
        self.gradient_delay_y = -5
        self.gradient_delay_z = -5


class Proton(object):
    """Define proton sequence configurations."""

    def __init__(self):
        self._ = 0
        self.gradient_delay_x = -5
        self.gradient_delay_y = -5
        self.gradient_delay_z = -5

def get_config() -> config_dict.ConfigDict:
    """Return the config dict. This is a required function.

    Returns:
        a ml_collections.config_dict.ConfigDict
    """
    return Config()
