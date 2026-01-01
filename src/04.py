import pathlib
from copy import deepcopy
from functools import reduce
import numpy as np
import scipy.signal

from utils import read_input


DAY = 4

TEST_INPUT = \
"""
..@@.@@@@.
@@@.@.@.@@
@@@@@.@.@@
@.@@@@..@.
@@.@@@@.@@
.@@@@@@@.@
.@.@.@.@@@
@.@@@.@@@@
.@@@@@@@@.
@.@.@@@.@.
"""

TEST_RESULT_PART_ONE = 13
TEST_RESULT_PART_TWO = 43

def read_map(lines: list[str]) -> np.ndarray:
    rows, cols = len(lines), len(lines[0])
    grid = np.zeros((rows, cols), dtype=int)
    for y, line in enumerate(lines):
        grid[y,:] = list(map(lambda c: 0 if c == "." else 1, line))
    return grid


def solve_part_one(lines: list[str]) -> int:
    grid = read_map(lines)
    # Check 3x3 neighbourhood
    filter = np.ones((3,3), dtype=int)
    filter[1, 1] = 0
    # Use implicit zero-padding
    accessible_locs = scipy.signal.convolve2d(grid, filter, mode="same", boundary="fill", fillvalue=0.)
    accessible_locs = np.where(accessible_locs < 4, 1, 0)
    accessible_rolls = np.logical_and(grid, accessible_locs)
    return np.sum(accessible_rolls)


def solve_part_two(lines: list[str]) -> int:
    grid = read_map(lines)
    # Check 3x3 neighbourhood
    filter = np.ones((3,3), dtype=int)
    filter[1, 1] = 0
    num_removed = 0
    num_accessible = -1
    while num_accessible != 0:
        accessible_locs = scipy.signal.convolve2d(grid, filter, mode="same", boundary="fill", fillvalue=0.)
        accessible_locs = np.where(accessible_locs < 4, 1, 0)
        accessible_rolls = np.logical_and(grid, accessible_locs)
        num_accessible = np.sum(accessible_rolls)
        num_removed += num_accessible
        # Remove accessible rolls from grid
        grid &= (~accessible_rolls)
    return num_removed


if __name__ == '__main__':
    test_input= read_input.read_test_input(TEST_INPUT)
    input_path = pathlib.Path(__file__).parent.parent.joinpath(f'ressources/{DAY:02d}.txt')
    real_input = read_input.read_input(str(input_path))

    #################################
    print(f'### DAY {DAY} - PART ONE ###')
    
    test_out_1 = solve_part_one(test_input)
    print(f'Test output: {test_out_1}. Expected output: {TEST_RESULT_PART_ONE}')
    assert test_out_1 == TEST_RESULT_PART_ONE, "Test for part one failed"

    real_out_1 = solve_part_one(real_input)
    print(f'Real output: {real_out_1}')

    #################################
    print(f'### DAY {DAY} - PART TWO ###')
    
    test_out_2 = solve_part_two(test_input)
    print(f'Test output: {test_out_2}. Expected output: {TEST_RESULT_PART_TWO}')
    assert test_out_2 == TEST_RESULT_PART_TWO, "Test for part two failed"

    real_out_2 = solve_part_two(real_input)
    print(f'Real output: {real_out_2}')
