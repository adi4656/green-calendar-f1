import json
import math
import pathlib

import requests
import googlemaps

import file_constants


# Initialise constants, setup API clients

_FLIGHT_EFFICIENCY = (
    602.0 *
    (10**-6)) / 1000.0  # (602 * 10^-6) tonnes CO2 per tonne-km for air freight
_ROAD_EFFICIENCY = (
    62.0 *
    (10**-6)) / 1000.0  # (62 * 10^-6) tonnes CO2 per tonne-km for trucks
_TONNAGE = 500  # 50 tons per team, and 10 teams

project_path = pathlib.Path.cwd().parent
hqs_path = project_path / "data/headquarters.txt"
env_path = project_path / ".env"


with open(env_path) as env_file, open(hqs_path) as hq_file, open(file_constants.ROUTES_PATH) as routes_file:
    env = json.load(env_file)
    hq_data = json.load(hq_file)
    routes_data = json.load(routes_file)
  
_FLIGHT_API_URL = "https://distanceto.p.rapidapi.com/get"
_FLIGHT_API_HEADERS = {
    "x-rapidapi-host": "distanceto.p.rapidapi.com",
    "x-rapidapi-key": f"{env['rapidapi']}",
}
_GMAPS_CLIENT = googlemaps.Client(key=f"{env['googlemaps']}")

_EUROPE_HQS = hq_data[0]
_FLYAWAY_HQS = hq_data[1]
_ALL_HQS = {**_EUROPE_HQS, **_FLYAWAY_HQS}


def _flight_emitted(from_iata, to_iata):
    """Emissions per ton."""
    if from_iata == to_iata:
        return 0
    query = {
        "car": "false",
        "foot": "false",
        "route": json.dumps([{
            "t": from_iata
        }, {
            "t": to_iata
        }]),
    }
    resp_raw = requests.request("GET",
                                _FLIGHT_API_URL,
                                headers=_FLIGHT_API_HEADERS,
                                params=query)
    resp_data = json.loads(resp_raw.content)
    flight_list = resp_data["steps"][0]["distance"]["flight"]
    min_dist = min((flight["distance"] for flight in flight_list),
                   default=math.inf)
    return min_dist * _FLIGHT_EFFICIENCY


def _road_emitted(from_addr, to_addr):
    """Emissions per ton."""
    if from_addr == to_addr:
        return 0
    resp = _GMAPS_CLIENT.directions(from_addr, to_addr)
    legs = resp[0].get("legs")
    dist = sum((leg.get("distance").get("value") for leg in legs))
    dist /= 1000  # Converting API distance unit (metres) to program unit (km)
    return dist * _ROAD_EFFICIENCY


def _summerbreak_emitted(race_location):
    """The emissions per ton of a journey from race to an idealised "summer break race".
    Distances to this idealised race are weighted sums of distances to all teams' bases.
    Assumes each team has equal tonnage."""
    hq_weightage = 1 / (len(_ALL_HQS))
    (race_iata, race_leg, race_addr) = race_location

    emit_per_ton = 0
    for hq in _ALL_HQS:
        if (hq in _FLYAWAY_HQS) or (race_leg != file_constants.EUROPE_NAME):
            emit_per_ton += hq_weightage * _flight_emitted(
                race_iata, _ALL_HQS[hq])
        else:
            emit_per_ton += hq_weightage * _road_emitted(race_addr, hq)
    return emit_per_ton


def _memoise_emitted(emitted):
    """Memoises results of calls to emitted in an external file.
    Means if program has been run previously (eg in testing or in previous use of scheduler),
    a request sent to API on this previous run doesn't need to be re-sent.
    Decorator used as a) emitted is part of public API; b) can easily disable it to test API calls.
    """

    def wrapper(from_data, to_data, all_routes):
        (from_name, _) = from_data
        (to_name, _) = to_data
        race_pair = str((from_name, to_name))
        if race_pair in all_routes:
            return all_routes[race_pair]

        res = emitted(from_data, to_data)
        with open(file_constants.ROUTES_PATH) as routes_file:
            routes_data = json.load(routes_file)
        routes_data[file_constants.PRECOMPUTED_NAME][race_pair] = res
        with open(file_constants.ROUTES_PATH, "w") as routes_file:
            json.dump(routes_data, routes_file)
        return res

    return wrapper


@_memoise_emitted
def emitted(from_data, to_data, all_routes):
    """Total CO2 emitted by shortest route from race1 to race2,
    accounting for whether journey is by road or air."""
    (from_name, (from_iata, from_leg, from_addr)) = from_data
    (to_name, (to_iata, to_leg, to_addr)) = to_data
    if from_name == to_name:
        return 0

    try:
        if from_name == file_constants.SUMMERBREAK_NAME:
            emit_per_ton = _summerbreak_emitted((to_iata, to_leg, to_addr))
        elif to_name == file_constants.SUMMERBREAK_NAME:
            emit_per_ton = _summerbreak_emitted(
                (from_iata, from_leg, from_addr))
        elif (from_leg == file_constants.EUROPE_NAME) and (to_leg == file_constants.EUROPE_NAME):
            emit_per_ton = _road_emitted(from_addr, to_addr)
        else:
            emit_per_ton = _flight_emitted(from_iata, to_iata)
    # API responses could vary widely, so difficult to predict type of error.
    except:
        raise Exception("API access error.")
    return emit_per_ton * _TONNAGE
