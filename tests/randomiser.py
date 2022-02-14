import random
import numpy as np


def random_matrix(n, max_weight):
    matrix = np.random.randint(1, max_weight, (n, n))
    for i in range(n):
        matrix[i][i] = 0
    return matrix


def random_time_windows(set_size):
    timewindows = {}
    for race in range(set_size):
        race_time_windows = []
        # No point having more than 2 TWs
        # Doesn't test anything, and makes invalid route more likely -> less info
        for _ in range(random.randint(0, 2)):
            start = random.randint(1, set_size)
            end = random.randint(start, set_size)
            if random.choice([True, False]):
                start -= set_size + 1
            if random.choice([True, False]):
                end -= set_size + 1
            race_time_windows.append([start, end])
        # For race with no time windows, randomly choose whether to add empty list to timewindows
        if race_time_windows or random.choice([True, False]):
            timewindows[race] = race_time_windows
    return timewindows
