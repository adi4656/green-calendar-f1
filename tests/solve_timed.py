import datetime
import sys
import pathlib
import time

import matplotlib.pyplot as plt

import randomiser
SCHEDULER_PATH = pathlib.Path.cwd().parent / "src"
sys.path.append(str(SCHEDULER_PATH))
import scheduler

time_complexity = lambda n: (2**n) * (n**2)


def calculate_ratios(lower_set_size, upper_set_size, reps_per_size):
    ratios = []
    for set_size in range(lower_set_size, upper_set_size + 1):
        total_time = 0
        for i in range(reps_per_size):
            matrix = randomiser.random_matrix(set_size, 50)
            time_windows = randomiser.random_time_windows(set_size)
            time_windows = {}
            start = time.perf_counter()
            scheduler.solve(None, set(range(set_size)), matrix, time_windows)
            end = time.perf_counter()
            total_time += end - start
        ratios.append(
            (10**9) * (total_time / (time_complexity(set_size) * set_size)))
    return ratios


def main(lower_set_size, upper_set_size, reps_per_size):
    ratios = calculate_ratios(lower_set_size, upper_set_size, reps_per_size)
    print(ratios)
    set_sizes = range(lower_set_size, upper_set_size + 1)
    plt.plot(set_sizes, ratios, "ro")
    plt.xlabel("Set size")
    plt.ylabel("Speed : time complexity ratio")
    plt.show()


if __name__ == "__main__":
    try:
        lower_set_size = int(sys.argv[1])
    except IndexError:
        lower_set_size = 10
    try:
        upper_set_size = int(sys.argv[2])
    except IndexError:
        upper_set_size = 16
    try:
        reps_per_size = int(sys.argv[3])
    except IndexError:
        reps_per_size = 3
    main(lower_set_size, upper_set_size, reps_per_size)
