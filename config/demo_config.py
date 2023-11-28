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
        self.data_dir = "007-005B"
        self.subject_id = "/Users/aribechtel/Documents/Mirror/patients/007-005B/test"


def get_config() -> config_dict.ConfigDict:
    """Return the config dict. This is a required function.

    Returns:
        a ml_collections.config_dict.ConfigDict
    """
    return Config()
