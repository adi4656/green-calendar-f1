import json
import pathlib
import itertools
from math import inf

import numpy as np

import distance_calculator
import file_constants
import file_formatting


# Solved is the table that memoises calls to solve().
# It is kept as global state in anticipation of parallelising this algorithm.
# It is a large table - space complexity O(n * (2 ** n)).
# So it would be expensive to a) copy it for each parallel recursive calls
# and b) merge the results of each parallel recursive call into a new table.
solved = {}


def normalise_tws(tws, num_races):
    """Converts all negative positions in tws to positive,
    and makes each time window pair immutable.
    Logic is split from renaming of TWs,
    as unnormalised but integer-named TWs used in testing solve(),
    so good to have this func called within solve()."""
    make_positive = lambda pos: (pos + num_races + 1) if (pos < 0) else pos
    new_tws = {}
    for race in tws:
        new_tws[race] = [(make_positive(race_tw[0]), make_positive(race_tw[1]))
                         for race_tw in tws[race]]
    return new_tws


def _within_tws(start, to_visit, tws, num_races):
    """Checks race falls within allowed time window.
    KEY INSIGHT: Although the parameters seem not to convey info about
    where start and to_visit will occur in the final sequence,
    in fact the order of calls of solve means that
    there will never be any races in the sequence after the races in to_visit.
    WHY?
    We start with a candidate start race and the remaining races,
    so the remaining races (to_visit) will be the last N-1 races.
    Then we try a second race and
    recursively call on the second race and the remaining races minus this race.
    Hence to_visit will be the last N-2 races. Etc.
    HENCE we calculate the position of start by subtracting len(to_visit) from the number of races.
    Note that the time windows for the races in to_visit will have been checked in recursive calls.
    """
    if (start not in tws) or (not tws[start]):
        return True
    start_tws = tws[start]
    start_pos = num_races - len(to_visit)
    in_tw = lambda pos, tw: pos in range(tw[0], tw[1] + 1)
    return any((in_tw(start_pos, tw) for tw in start_tws))


def solve(start, to_visit, adj_matrix, unnormalised_tws):
    """
    PURPOSE
    Returns shortest path (in reversed order), starting at race start,
    and visiting every race in to_visit.
    FORMAT
    Returned data is of format (shortest path, length of this path).
    Race start is not included in the path.
    start = None indicates race start should be selected from to_visit.
    Shortest path is represented with a lazily evaluated itertools.chain,
    so copying it takes O(1) instead of O(N) time (important for the case
    when we find a start and to_visit already in solved).
    """
    global solved
    solved = {}
    
    num_races = len(adj_matrix)
    return _do_solve(
        start,
        to_visit,
        adj_matrix,
        normalise_tws(unnormalised_tws, num_races),
        num_races,
    )


def _do_solve(start, to_visit, adj_matrix, tws, num_races):
    """
    PURPOSE
    Performs main computation of solve.
    Logic is separated to avoid repeating computations in solve, and to not
    reset solved.
    FORMAT
    Time windows must be normalised.
    NUM_RACES must be number of races in graph represented by adj_matrix.
    Otherwise, as with solve.
    GUARANTEES
    Once function done executing,
    all parameters other than start must be unchanged.
    """
    global solved
    solved_key = (start, frozenset(to_visit))  # set cannot be hashed

    if solved_key in solved:
        # Since the returned path will be passed up to caller functions and mutated, return a copy.
        (path, cost) = solved[solved_key]
        return (itertools.chain(path), cost)

    if not _within_tws(start, to_visit, tws, num_races):
        return (itertools.chain(), inf)
    if to_visit == set():
        return (itertools.chain(), 0)

    minimum = inf
    path = itertools.chain()
    to_visit_copy = set(
        to_visit)  # directly passing to_visit unsafe due to risk of mutation
    for candidate_next in to_visit:
        to_visit_copy.remove(candidate_next)
        recursive_res = _do_solve(candidate_next, to_visit_copy, adj_matrix,
                                  tws, num_races)
        cost = recursive_res[1] + (adj_matrix[start][candidate_next]
                                   if start is not None else 0)
        if cost < minimum:
            minimum = cost
            path = itertools.chain([candidate_next], recursive_res[0])
        to_visit_copy.add(candidate_next)

    solved[solved_key] = (path, minimum)
    # Again copying path to ensure immutability
    return (itertools.chain(path), minimum)


def _load_data():
    with open(file_constants.RACE_DATA_PATH) as infile:
        race_data = json.load(infile)
    return race_data


def main():
    """Read appropriate external data,
    and output result of solve() in a human-friendly format."""
    race_data = _load_data()
    num_races, adj_matrix, renamed_tws, race_names_order = file_formatting.extract_all(race_data)

    res = solve(None, set(range(num_races)), adj_matrix, renamed_tws)
    if res[1] == inf:
        print("No route is possible. Check time windows.")
    else:
        print(f"Total CO2: {res[1]} tonnes")
        for race_index in res[0]:
            print(race_names_order[race_index])


if __name__ == "__main__":
    main()
