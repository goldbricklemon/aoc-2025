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


def point_in_polygon(p: tuple[int, int], poly_points:np.ndarray) -> tuple[bool, int]:
    # Ray-casting algorithm using the even-odd rule
    # Cast a horizontal ray from p to x-infinity and check number of poly edge intersections
    # Uses image coordinate system (y axis down)!
    px, py = p
    n_points = poly_points.shape[0]
    in_poly = False
    on_poly = False
    n_crosses = 0
    for i in range(n_points):
        ax, ay = poly_points[i-1]
        bx, by = poly_points[i]

        # Check if p is poly grid point
        if p == (ax, ay) or p == (bx, by):
            on_poly = True

        # Check if poly edge is horizontal and contains p
        elif (ay == by == py) and (ax <= px <= bx or bx <= px <= ax):
            on_poly = True
            
        # Check if ray overlaps with horizontal edge
        elif (ay == by == py) and (px <= ax and px <= bx):
            pass # do nothing
        
        # Check if ray can hit AB at all
        elif ay <= py <= by or by <= py <= ay:
            # Special case: ray hits the lower of both points
            # Ignore to avoid double-counting of this hit
            if ( py == ay and by <= ay ) or ( py == by and ay <= by ):
                continue

            # Use cross-product to determine the side of AB on which p lies
            cross = (ax - px) * (by - py) - (ay - py) * (bx - px)
            if cross == 0:
                # Ray intersects and is parallel to AB -> P lies on AB
                on_poly = True
            # In image coordinates, when a above b, then p must be right of AB to intersect
            # In this case, cross < 0
            elif (ay < by) == (cross < 0):
                n_crosses += 1
                in_poly = not in_poly

    return in_poly or on_poly, n_crosses



def solve_part_two(lines: list[str]) -> int:
    #poly = np.array([[1,2], [6,2], [6,4], [4,4], [4,6], [3,6], [3,5], [1,5]])
    #point_in_polygon((0,3), poly)
    #48:15

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

    max_area = 0
    for i in range(n_points):
        for j in range(i + 1, n_points):
            if rect_areas[i,j] > max_area:
                pi, pj = points[[i, j]]
                edge2 = (pi[0], pj[1])
                edge3 = (pj[0], pi[1])                
                if point_in_polygon(edge2, points) and point_in_polygon(edge3, points):
                    max_area = rect_areas[i,j]

    return max_area # Too high!


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
