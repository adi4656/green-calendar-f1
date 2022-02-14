import itertools
import pathlib
import sys
import copy
from math import inf

import src.scheduler as scheduler


def valid(route, graph, all_races, all_time_windows):
    """Checks if all races in route fall within their time window."""

    position = 1
    for race in route:
        if race not in all_time_windows or (not all_time_windows[race]):
            satisfied = True
        else:
            satisfied = False
            for timewindow in all_time_windows[race]:
                start = timewindow[0]
                if start < 0:
                    start += len(all_races) + 1
                end = timewindow[1]
                if end < 0:
                    end += len(all_races) + 1
                if position in range(start, end + 1):
                    satisfied = True
                    break
        if not satisfied:
            return False
        position += 1
    return True


def calc_dist(route, num_cities, GRAPH):
    dist = 0
    for index in range(1, num_cities):
        dist += GRAPH[route[index - 1]][route[index]]
    return dist


def naive(GRAPH, all_races, all_time_windows):
    num_cities = len(GRAPH)
    all_time_windows = scheduler.normalise_tws(all_time_windows, num_cities)
    S = list(range(num_cities))
    routes = itertools.permutations(S, num_cities)
    selected_route = None
    minimum = inf
    for route in routes:
        dist = calc_dist(route, num_cities, GRAPH)
        if (dist < minimum) and valid(route, GRAPH, all_races,
                                      all_time_windows):
            selected_route = route
            minimum = dist
    if selected_route:
        selected_route = list(selected_route)
    return (selected_route, minimum)


def compare(graph, time_windows):
    scheduler.solved = {}
    num_races = len(graph)
    all_races = list(range(num_races))
    scheduler_result = scheduler.solve(None, set(all_races),
                                       copy.deepcopy(graph),
                                       copy.deepcopy(time_windows))
    naive_result = naive(graph, all_races, time_windows)
    return (scheduler_result, naive_result)
