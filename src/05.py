import pathlib
from copy import deepcopy
from functools import reduce
import numpy as np

from utils import read_input


DAY = 5

TEST_INPUT = \
"""
3-5
10-14
16-20
12-18

1
5
8
11
17
32
"""

TEST_RESULT_PART_ONE = 3
TEST_RESULT_PART_TWO = 14


def read_ranges_and_ids(lines: list[str]) -> tuple[list[tuple[int, int]], list[int]]:
    id_ranges, ids = [], []
    read_ids = False
    for line in lines:
        if len(line) < 1:
            read_ids = True
        else:
            if read_ids:
                ids.append(int(line))
            else:
                id_range = line.split("-")
                id_range = tuple(int(s) for s in id_range)
                id_ranges.append(id_range)
    return id_ranges, ids
            

def compactify_ranges(id_ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge ID ranges such that only sorted, disjoint ranges remain.
    """
    cur_range = None
    compact_id_ranges = []
    for id_range in sorted(id_ranges):
        if cur_range is None:
            cur_range = id_range
        else:
            if id_range[0] > cur_range[1]:
                compact_id_ranges.append(cur_range)
                cur_range = id_range
            elif id_range[1] > cur_range[1]:
                cur_range = (cur_range[0], id_range[1])
                
    if cur_range is not None:
        compact_id_ranges.append(cur_range)
        
    return compact_id_ranges
                

def solve_part_one(lines: list[str]) -> int:
    id_ranges, ids = read_ranges_and_ids(lines)
    # Sort both ranges and ids
    id_ranges = compactify_ranges(id_ranges)
    ids = sorted(ids)
    
    range_index = 0
    fresh_ids = []
    # Iterate over sorted IDs and sorted ID ranges
    # Avoids an O(n^2) lookup algorithm
    for food_id in ids:
        while range_index < len(id_ranges) - 1 and id_ranges[range_index][1] < food_id:
            range_index += 1
        id_range = id_ranges[range_index]
        if id_range[0] <= food_id <= id_range[1]:
            fresh_ids.append(food_id)
    return len(fresh_ids)


def solve_part_two(lines: list[str]) -> int:
    id_ranges, ids = read_ranges_and_ids(lines)
    # Sort both ranges and ids
    id_ranges = compactify_ranges(id_ranges)
    total_fresh_ids = sum(end - start + 1 for start, end in id_ranges)
    return total_fresh_ids


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
