"""Convert calibration, Dixon, and proton Siemens twix files to MRD."""
import logging

from absl import app, flags
from ml_collections import config_flags

from config import base_config
from subject_classmap import Subject

FLAGS = flags.FLAGS

_CONFIG = config_flags.DEFINE_config_file("config", None, "config file.")


def siemens_to_mrd(config: base_config.Config):
    """Convert Siemens twix file to 129Xe MRD file.

    Args:
        config (config_dict.ConfigDict): config dict
    """
    subject = Subject(config=config)
    subject.read_twix_files()
    subject.get_trajectories()
    subject.write_all_mrd_files()


def main(argv):
    config = _CONFIG.value
    siemens_to_mrd(config)


if __name__ == "__main__":
    app.run(main)
