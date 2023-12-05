# xe-siemens-to-mrd

A tool for converting standard 129Xe MRI scans from Siemens twix files to ISMRMRD files. ISMRMRD files are formatted according to the 129Xe MRI clinical trials consortium specifications: https://docs.google.com/spreadsheets/d/1SeG4K4VgA1DUrTBhSjgeSqu3UCGiCWaLG3wqHg6hBh8/edit?usp=sharing.

## Table of contents:

1. [Setup](#setup)

2. [Usage](#usage)

## Setup

Download or clone this repository onto your local computer.

### 1.1 Python installation

First step of the setup process is to install python. This pipeline works with Python 3.8.8 in its current version. To create a virtual environment, a 'conda' distribution is required.

### 1.2 Create a virtual environment

To create a virtual environment using `conda` execute the command in the terminal:

```bash
conda create --name XeGas python=3.8.8
```

Here, XeGas is the the given name, but any name can be given.

To activate the environment, execute the command

```bash
conda activate XeGas
```

### 1.3 Install required packages

We will be using pip to install the required packages. First update the pip using:

```bash
pip install --upgrade pip
```

Now install a c compiler. Here we will install gcc compiler.

##### Linux and WSL users:

Get updates:

```bash
sudo apt-get update
```

Install gcc executing this command:

```bash
sudo apt install gcc
```

##### Mac Users:

Install gcc:

```bash
brew install gcc
```

Now we are ready to install necessary packages. Packages must be installed inside the virtual conda environment. The list of packages are in the `setup/requirements.txt` file. In the terminal, if you are not in the main program directory, change the directory using the `cd` command. To install the required packages, activate your virtual environment and execute the command:

```bash
pip install -r setup/requirements.txt
```

To confirm that correct packages are installed, execute the command

```
pip list
```

and verify that the packages in the virtual environment agree with that in the `requirements.txt` file.

## Usage

### 2.1 Configuration file

All subject information and scan parameters are specified in a subject-specific configuration file. Default configuration settings are defined in `config/base_config.py`. The defaults are inhereted by subject-specific config files, unless overriden.
<br />
<br />`config/demo_config.py` shows examples of basic config settings that you will usually want to change for each group of subject scans. Currently the only necessary configurations are the following:

- `data_dir`: Directory containing at least one of the following: calibration, proton, or Dixon scan twix file. This directory is where output MRD files will be saved.
- `subject_id`: Subject ID number that will be stored in the MRD file and used to label output files

`config/base_config.py` contains `Calibration`, `Dixon`, and `Proton` classes for potential future configurations for these scans.

### 2.2 Processing twix files

When a configuration file is processed, the pipeline will search for calibration, proton, and Dixon twix files in `data_dir` and convert any existing files to MRD format. MRD files are output to `data_dir`.

To process a configuration file, navigate to the main directory of this repository in terminal and excute the following command:

```bash
python main.py --config [path-to-config-file]
```
