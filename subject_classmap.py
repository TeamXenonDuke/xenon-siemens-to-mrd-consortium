"""Module for gas exchange imaging subject."""
import glob
import logging
import os
from typing import Any, Dict

import nibabel as nib
import numpy as np

import preprocessing as pp
from config import base_config
from utils import constants, io_utils, traj_utils


class Subject(object):
    """Module to for processing gas exchange imaging.

    Attributes:
        config (config_dict.ConfigDict): config dict
        dict_dis (dict): dictionary of dissolved-phase data and metadata
        dict_dyn (dict): dictionary of dynamic spectroscopy data and metadata
        dict_proton (dict): dictionary of UTE proton data and metadata
    """

    def __init__(self, config: base_config.Config):
        """Init object."""
        self.config = config
        self.dict_dis = {}
        self.dict_dyn = {}
        self.dict_proton = {}

    def read_twix_files(self):
        """Read in twix files to dictionary, if they exist."""
        logging.info("Reading twix files.")
        try:
            self.dict_dis = io_utils.read_dis_twix(
                io_utils.get_dis_twix_files(str(self.config.data_dir))
            )
            self.dict_dis[constants.IOFields.SUBJECT_ID] = self.config.subject_id
        except:
            logging.info("Could not find/read Dixon file.")

        try:
            self.dict_dyn = io_utils.read_dyn_twix(
                io_utils.get_dyn_twix_files(str(self.config.data_dir))
            )
            self.dict_dyn[constants.IOFields.SUBJECT_ID] = self.config.subject_id
        except:
            logging.info("Could not find/read calibration file.")

        try:
            self.dict_proton = io_utils.read_ute_twix(
                io_utils.get_ute_twix_files(str(self.config.data_dir))
            )
            self.dict_proton[constants.IOFields.SUBJECT_ID] = self.config.subject_id
        except:
            logging.info("Could not find/read proton file.")

        if not (bool(self.dict_dis) or bool(self.dict_dyn) or bool(self.dict_proton)):
            ValueError("Could not read/find twix files.")

    def get_trajectories(self):
        """Get Dixon and proton trajectories.

        Also, calculates the scaling factor for the trajectory.
        """
        logging.info("Getting trajectories.")
        if bool(self.dict_dis):
            traj = pp.prepare_traj_interleaved(
                self.dict_dis,
                generate_traj=True,
            )

            traj_scaling_factor = traj_utils.get_scaling_factor(
                recon_size=int(self.config.recon.recon_size),
                n_points=self.dict_dis[constants.IOFields.N_POINTS],
                scale=True,
            )
            traj *= traj_scaling_factor
            self.dict_dis[constants.IOFields.TRAJ] = traj

        if bool(self.dict_proton):
            traj = pp.prepare_traj(self.dict_proton)
            traj *= traj_scaling_factor
            self.dict_proton[constants.IOFields.TRAJ] = traj

    def write_all_mrd_files(self):
        """Write MRD files."""
        logging.info("Writing MRD files.")
        if bool(self.dict_dis):
            io_utils.write_mrd_file(
                path=os.path.join("tmp", "{}_dixon.h5".format(self.config.subject_id)),
                data_dict=self.dict_dis,
                scan_type="dixon",
            )
        if bool(self.dict_dyn):
            io_utils.write_mrd_file(
                path=os.path.join(
                    "tmp", "{}_calibration.h5".format(self.config.subject_id)
                ),
                data_dict=self.dict_dyn,
                scan_type="calibration",
            )

        if bool(self.dict_proton):
            io_utils.write_mrd_file(
                path=os.path.join("tmp", "{}_proton.h5".format(self.config.subject_id)),
                data_dict=self.dict_proton,
                scan_type="proton",
            )

    def move_output_files(self):
        """Move output files into dedicated directory."""
        logging.info("Moving output files to subject directory.")
        output_files = glob.glob("tmp/*.h5")
        io_utils.move_files(output_files, self.config.data_dir)
