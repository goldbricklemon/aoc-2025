import pathlib
from copy import deepcopy
from functools import reduce
import numpy as np

from utils import read_input


DAY = 2

TEST_INPUT = \
"""
11-22,95-115,998-1012,1188511880-1188511890,222220-222224,1698522-1698528,446443-446449,38593856-38593862,565653-565659,824824821-824824827,2121212118-2121212124
"""

TEST_RESULT_PART_ONE = 1227775554
TEST_RESULT_PART_TWO = 0

def read_ranges(line: str) -> tuple[int, int]:
    parts = line.split(",")
    return [(int(s) for s in p.split('-')) for p in parts]


def solve_part_one(lines: list[str]) -> int:
    ranges = read_ranges(lines[0])
    invalid_ids = []
    for start, end in ranges:
        for num in range(start, end+1):
            num_str = str(num)
            digits = len(num_str)
            if digits % 2 == 0:
                if num_str[:digits//2] == num_str[digits//2:]:
                    invalid_ids.append(num)
            
    return sum(invalid_ids)


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
