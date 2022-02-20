"""
Contains methods for formatting them to format required by scheduler, main.
Along with file_constants, allows use of consistent data model by these other programs.
Make sure to modify this and file_constants if you modify the structure.

"""
import numpy as np


import distance_calculator
import file_constants


def create_adj_matrix(num_races, race_names_order, race_data, routes):
    adj_matrix = np.full((num_races, num_races), 0, dtype=np.double)
    for row_index, from_race in enumerate(race_names_order):
        for col_index, to_race in enumerate(race_names_order):
            from_data = race_data[from_race]
            to_data = race_data[to_race]
            adj_matrix[row_index][col_index] = distance_calculator.emitted(
                (from_race, (from_data[file_constants.IATA_INDEX], from_data[file_constants.LEG_INDEX], from_data[file_constants.ADDRESS_INDEX])),
                (to_race, (to_data[file_constants.IATA_INDEX], to_data[file_constants.LEG_INDEX], to_data[file_constants.ADDRESS_INDEX])),
                routes)
    return adj_matrix


def extract_all(race_data, routes = file_constants.ALL_ROUTES):
    race_names_order = list(race_data.keys())
    num_races = len(race_names_order)
    renamed_tws = {
        race_names_order.index(race_name): race_data[race_name][file_constants.TWS_INDEX]
        for race_name in race_data
    }
    adj_matrix = create_adj_matrix(num_races, race_names_order, race_data, routes)
    return (num_races, adj_matrix, renamed_tws, race_names_order)


def get_table_data(races_data, columns_to_exclude):
    """ Strip columns_to_exclude from race_data.
    Used by RacesPage in GUI to remove Time Windows from its table.
    """
    table_data = {}
    for race in races_data:
        new_race_data = [el for col_index, el in enumerate(races_data[race]) if col_index not in columns_to_exclude]
        table_data[race] = new_race_data
    return table_data
    
