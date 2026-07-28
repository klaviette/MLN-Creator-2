"""
import os
import sys
import multiprocessing

# Change the current working directory
configfilename = "./datasets/IMDb/data_files/small-64Movies.gen"

MLN_USR = "datasets"
os.chdir("./HOMLN")

sys.path.append(
    "./HOMLN")
folder_path = os.getcwd()
MLN_USR = folder_path + "/datasets"
configfilename = folder_path +"/datasets/IMDb/data_files/small-64Movies.gen"

import HOMLN.layer_generator
if __name__ == '__main__':
    multiprocessing.freeze_support()
    HOMLN.layer_generator.main(MLN_USR, configfilename)
"""

# changed the path manipulation to use absolute paths instead of relative paths, and added comments to explain the changes.

import os
import sys
import multiprocessing
import pathlib

# find the absolute path of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# add the HOMLN directory to the system path
sys.path.append(os.path.join(BASE_DIR, "HOMLN"))

# accept a config file path as a command-line argument, otherwise use the default
if len(sys.argv) > 1:
    configfilename = sys.argv[1]
else:
    configfilename = os.path.join(
        BASE_DIR,
        "datasets",
        "Chocolate",
        "data_files",
        "unit_price.gen" # default fallback
    )

# Derive MLN_USR from the config file's location rather than the script location.
# Walk up the directory tree and stop at the first folder named "datasets".
# This works whether the .gen file lives in the bundled datasets/ folder or in
# a workspace folder like ~/MLNCreator/datasets/.
_config_path = pathlib.Path(configfilename).resolve()
MLN_USR = None
for _parent in _config_path.parents:
    if _parent.name == "datasets":
        MLN_USR = str(_parent)
        break
if MLN_USR is None:
    MLN_USR = os.path.join(BASE_DIR, "datasets")  # original fallback

import HOMLN.layer_generator
if __name__ == '__main__':
    multiprocessing.freeze_support()
    HOMLN.layer_generator.main(MLN_USR, configfilename)