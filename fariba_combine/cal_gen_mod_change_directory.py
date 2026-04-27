"""
import os
import sys
import multiprocessing

# Change the current working directory
configfilename = "./amey_shinde/IMDb/data_files/small-64Movies.gen"

MLN_USR = "amey_shinde"
os.chdir("./HOMLN")

sys.path.append(
    "./HOMLN")
folder_path = os.getcwd()
MLN_USR = folder_path + "/amey_shinde"
configfilename = folder_path +"/amey_shinde/IMDb/data_files/small-64Movies.gen"

import HOMLN.layer_generator
if __name__ == '__main__':
    multiprocessing.freeze_support()
    HOMLN.layer_generator.main(MLN_USR, configfilename)
"""

# changed the path manipulation to use absolute paths instead of relative paths, and added comments to explain the changes.

import os
import sys
import multiprocessing

# find the absolute path of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# add the HOMLN directory to the system path
sys.path.append(os.path.join(BASE_DIR, "HOMLN"))

# define the path to the MLN_USR using the absolute path
MLN_USR = os.path.join(BASE_DIR, "amey_shinde")

# accept a config file path as a command-line argument, otherwise use the default
if len(sys.argv) > 1:
    configfilename = sys.argv[1]
else:
    configfilename = os.path.join(
        BASE_DIR,
        "amey_shinde",
        "Chocolate",
        "data_files",
        "unit_price.gen" # default fallback
    )

import HOMLN.layer_generator
if __name__ == '__main__':
    multiprocessing.freeze_support()
    HOMLN.layer_generator.main(MLN_USR, configfilename)