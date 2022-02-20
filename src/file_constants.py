"""
Contains info about structures and filepaths of data files.
Along with file_formatting, allows use of consistent data model by these other programs.
Make sure to modify this and file_formatting if you modify the structure.
"""
import pathlib
import json


# File paths
data_path = pathlib.Path.cwd().parent / "data"
ROUTES_PATH = data_path / "routes.txt"
RACE_DATA_PATH = data_path / "race_data.txt"
HQS_PATH = data_path / "headquarters.txt"
INTERVALS_INFO_PATH = data_path / "intervals_info.txt"

# Locations file
EUROPE_NAME = "Europe"
FLYAWAY_NAME = "Flyaway"
SUMMERBREAK_NAME = "Summer Break"
VALUE_LENGTH = 4
IATA_INDEX = 0
LEG_INDEX = 1
ADDRESS_INDEX = 2
TWS_INDEX = 3

# Routes file
PRECOMPUTED_NAME = "Precomputed"
OVERRIDEN_NAME = "User-defined"
with open(ROUTES_PATH) as routes_file:
    routes_data = json.load(routes_file)
precomputed_routes = routes_data[PRECOMPUTED_NAME]
user_defined_routes = routes_data[OVERRIDEN_NAME]
ALL_ROUTES = {
    **precomputed_routes,
    **user_defined_routes,
}  # making sure to override precomputed data with user-defined data
