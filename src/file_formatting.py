"""
Contains info about structures and filepaths of data files,
and methods for formatting them to format required by scheduler, main.
Allows use of consistent data model by these other programs.
Make sure to modify this if you modify the structure.
"""
import pathlib
import json

import numpy as np

import distance_calculator


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


def create_adj_matrix(num_races, race_names_order, race_data, routes):
    # Kept public in anticipation of use by GUI.
    adj_matrix = np.full((num_races, num_races), 0, dtype=np.double)
    for row_index, from_race in enumerate(race_names_order):
        for col_index, to_race in enumerate(race_names_order):
            from_data = race_data[from_race]
            to_data = race_data[to_race]
            adj_matrix[row_index][col_index] = distance_calculator.emitted(
                (from_race, (from_data[IATA_INDEX], from_data[LEG_INDEX], from_data[ADDRESS_INDEX])),
                (to_race, (to_data[IATA_INDEX], to_data[LEG_INDEX], to_data[ADDRESS_INDEX])),
                routes)
    return adj_matrix

def extract_all(race_data, routes = ALL_ROUTES):
    race_names_order = list(race_data.keys())
    num_races = len(race_names_order)
    renamed_tws = {
        race_names_order.index(race_name): race_data[race_name][TWS_INDEX]
        for race_name in race_data
    }
    adj_matrix = create_adj_matrix(num_races, race_names_order, race_data, routes)
    return (num_races, adj_matrix, renamed_tws, race_names_order)

