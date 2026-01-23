import pathlib
from copy import deepcopy
from functools import reduce
import numpy as np

from utils import read_input


DAY = 9

TEST_INPUT = \
"""
7,1
11,1
11,7
9,7
9,5
2,5
2,3
7,3
"""

TEST_RESULT_PART_ONE = 50
TEST_RESULT_PART_TWO = 24

def read_points(lines: list[str]) -> np.ndarray:
    return np.array([[int(s) for s in line.split(',')] for line in lines])


def solve_part_one(lines: list[str]) -> int:
    # More or less brute force solution for now
    # points in (N, 2)
    points = read_points(lines)
    n_points = points.shape[0]
    # point pairs in (N, N, 2)
    pairs = np.tile(points[:, np.newaxis, :], reps=(1, n_points, 1))
    # coord-wise differences within pairs
    # (N, N, 2)
    pair_diff = pairs - np.transpose(pairs, axes=(1, 0, 2))
    # absolute differences (in x and y). +1 due to the way area is calulated in this puzzle
    pair_diff = np.abs(pair_diff) + 1
    # rect areas for each pair: (|dx| + 1) * (|dy| + 1)
    rect_areas = pair_diff[:, :, 0] * pair_diff[:, :, 1]

    return np.max(rect_areas)


def solve_part_two(lines: list[str]) -> int:
    # points in (N, 2)
    points = read_points(lines)
    n_points = points.shape[0]
    # point pairs in (N, N, 2)
    pairs = np.tile(points[:, np.newaxis, :], reps=(1, n_points, 1))
    # coord-wise differences within pairs
    # (N, N, 2)
    pair_diff = pairs - np.transpose(pairs, axes=(1, 0, 2))
    # absolute differences (in x and y). +1 due to the way area is calculated in this puzzle
    pair_diff = np.abs(pair_diff) + 1
    # rect areas for each pair: (|dx| + 1) * (|dy| + 1)
    rect_areas = pair_diff[:, :, 0] * pair_diff[:, :, 1]

    # Sort possible rects by area (descending)
    # As soon as we find a valid one, it will be the largest
    sorting_indices = np.unravel_index(np.argsort(rect_areas, axis=None)[::-1], rect_areas.shape)
    max_area = 0
    for i, j in zip(*sorting_indices):
        # Get opposing corners for this rect
        p0, p2 = points[[i, j]]
        # Ensure p0 left of p2
        if p0[0] > p2[0]:
            p0, p2 = p2, p0
        # Generate other rect corners
        p1 = (p2[0], p0[1])
        p3 = (p0[0], p2[1])
        # Ensure p0, p1, p2, p3 is top-left, top-right, bottom-right, bottom-left
        if p0[1] > p2[1]:
            p0, p1, p2, p3 = p3, p2, p1, p0

        valid = True
        # Iterate through all red tiles (and edges)
        for k in range(n_points):
            kx, ky = points[k]
            nx, ny = points[k-1]
            # If any other red tile lies in rect -> discard
            if  p0[0] < kx < p2[0] and p0[1] < ky < p2[1]:
                valid = False
                break
            # Now look at the red tile edge
            if kx == nx:
                # Vertical edge, with k above n
                if ky > ny:
                    kx, ky, nx, ny = nx, ny, kx, ky

                # If the edge starts/end above/below the rect
                # and intersects the rect in x-axis (not on rect border)
                # -> discard
                if ky <= p0[1] and ny >= p2[1] and p0[0] < kx < p2[0]:
                    valid = False
                    break
            else:
                # Horizontal edge, with k left of n
                if kx > nx:
                    kx, ky, nx, ny = nx, ny, kx, ky
                    
                # If the edge starts/end right/left of the rect
                # and intersects the rect in y-axis (not on rect border)
                # -> discard
                if kx <= p0[0] and nx >= p2[0] and p0[1] < ky < p2[1]:
                    valid = False
                    break
                
        if valid is True:
            max_area = rect_areas[i,j]
            break

    return max_area


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
