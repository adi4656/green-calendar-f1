# Structure of race data: dict {race shortname, values_arr}
# values_arr [address, IATA, leg]

import json

with open("races_old.txt", "r") as races_file:
    races = json.load(races_file)
europe = races["Europe"]
world = races["World Races"]
airports = races["Airports"]

new_data = {}
for i, europe_race in enumerate(europe):
    shortname = europe_race.split(",")[-1][1:]
    if shortname.startswith("Towcester"):
        shortname = "Britain"
    address = europe_race
    airport = airports[i]
    new_data[shortname] = [airport, "Europe", address]
for j, world_race in enumerate(world):
    shortname = world_race
    address = None
    airport = airports[j + len(europe)]
    new_data[shortname] = [airport, "Flyaway", address]
for i in range(25 - len(new_data)):
    new_data[i] = [None, None, new_data["Britain"][2]]
print(new_data)

with open("race_locations.txt", "w") as new_races_file:
    json.dump(new_data, new_races_file)
