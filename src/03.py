import pathlib
from copy import deepcopy
from functools import reduce
import numpy as np

from utils import read_input


DAY = 3

TEST_INPUT = \
"""
987654321111111
811111111111119
234234234234278
818181911112111
"""

TEST_RESULT_PART_ONE = 357
TEST_RESULT_PART_TWO = 0

def read_banks(lines: list[str]) -> np.ndarray:
    rows = len(lines)
    cols = len(lines[0])
    banks = np.zeros((rows, cols), dtype=int)
    for i, line in enumerate(lines):
        banks[i] = [int(c) for c in line]
    return banks


def solve_part_one(lines: list[str]) -> int:
    banks = read_banks(lines)
    jolts = []
    for bank in banks:
        i1 = np.argmax(bank[:-1])
        d1 = bank[i1]
        d2 = np.max(bank[i1+1:])
        jolts.append(d1*10 + d2)

    return sum(jolts)


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
