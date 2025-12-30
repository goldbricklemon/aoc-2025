import pathlib
from copy import deepcopy
from functools import reduce
import numpy as np

from utils import read_input


DAY = 0

TEST_INPUT = \
"""

"""

TEST_RESULT_PART_ONE = 0
TEST_RESULT_PART_TWO = 0


def solve_part_one(lines: list[str]) -> int:
    return 0


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
