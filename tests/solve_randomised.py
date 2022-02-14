import sys

import solver_comparer
import randomiser


def main(max_num_races, tests_per_num):
    for set_size in range(3, max_num_races):
        for i in range(tests_per_num):
            matrix = randomiser.random_matrix(set_size, 50)
            time_windows = randomiser.random_time_windows(set_size)
            (scheduler_res,
             naive_res) = solver_comparer.compare(matrix, time_windows)
            if scheduler_res[1] != naive_res[1]:
                print(matrix)
                print(time_windows)
                print(f"Naive: {naive_res[0]}")
                print(f"Scheduler: {list(scheduler_res[0])}")
                sys.exit()


if __name__ == "__main__":
    try:
        max_num_races = int(sys.argv[1])
    except IndexError:
        max_num_races = 5
    try:
        tests_per_num = int(sys.argv[2])
    except IndexError:
        tests_per_num = 100
    main(max_num_races, tests_per_num)
