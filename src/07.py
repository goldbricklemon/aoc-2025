import pathlib
from collections import deque
from copy import deepcopy
from functools import reduce
import numpy as np

from utils import read_input


DAY = 7

TEST_INPUT = \
"""
.......S.......
...............
.......^.......
...............
......^.^......
...............
.....^.^.^.....
...............
....^.^...^....
...............
...^.^...^.^...
...............
..^...^.....^..
...............
.^.^.^.^.^...^.
...............
"""

TEST_RESULT_PART_ONE = 21
TEST_RESULT_PART_TWO = 0


S = 'S'
SPLIT = "^"
BEAM = "|"
FREE = "."

def read_grid(lines: list[str]) -> np.ndarray:
    grid = np.array([[c for c in line] for line in lines], dtype='<U2')
    return grid


def solve_part_one(lines: list[str]) -> int:
    grid = read_grid(lines)
    rows = grid.shape[0]
    start_x: int = int(np.where(grid[0] == S)[0][0])
    beams = deque([(1, start_x)], maxlen=grid.size)
    num_splits = 0
    while len(beams) > 0:
        beam_y, beam_x = beams.pop()
        beam_y += 1
        while beam_y < rows and grid[beam_y, beam_x] == FREE:
            # Beam travels downwards freely
            grid[beam_y, beam_x] = BEAM
            beam_y += 1
        if beam_y < rows and grid[beam_y, beam_x] == SPLIT:
            # Beam hits a splitter (for the first time, implicitly)
            num_splits += 1
            for split_x in (beam_x - 1, beam_x  + 1):
                # Generate new beams if grid is free
                if grid[beam_y, split_x] == FREE:
                    grid[beam_y, split_x] = BEAM
                    beams.appendleft((beam_y, split_x))
    return num_splits


def solve_part_two(lines: list[str]) -> int:
    return 0


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
