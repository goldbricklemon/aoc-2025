import pathlib
from copy import deepcopy
from functools import reduce
import numpy as np
import itertools

from utils import read_input


DAY = 8

TEST_INPUT = \
"""
162,817,812
57,618,57
906,360,560
592,479,940
352,342,300
466,668,158
542,29,236
431,825,988
739,650,466
52,470,668
216,146,977
819,987,18
117,168,530
805,96,715
346,949,466
970,615,88
941,993,340
862,61,35
984,92,344
425,690,689
"""

TEST_RESULT_PART_ONE = 40
TEST_RESULT_PART_TWO = 25272

def read_jboxes(lines: list[str]) -> np.ndarray:
    jboxes = np.array([[int(s) for s in line.split(",")] for line in lines], dtype=int)
    return jboxes


def solve_part_one(lines: list[str], num_connections: int) -> int:
    # (N,3)
    jboxes = read_jboxes(lines)
    #### PREP
    n_boxes = jboxes.shape[0]
    # Tile to get distance between all pairs of boxes (N, N, 3)
    distances = np.tile(jboxes[:, np.newaxis, :], reps=(1, n_boxes, 1))
    # Computer pair-wise distances (N, N)
    distances = distances - np.transpose(distances, axes=(1, 0, 2))
    distances = np.linalg.norm(distances, ord=2, axis=2)
    # Set diagonal to inf
    distances[np.diag_indices(n_boxes)] = 1e9
    # Set everything below diagonal to inf
    distances[np.tril_indices_from(distances)] = 1e9
    # Get shortest pair-wise distances
    asc_dist_ind = np.unravel_index(np.argsort(distances, axis=None), distances.shape)
    
    ### SOLVING
    # Keep track of the circuit each box belongs to (initial: box ID = circuit ID)
    circuits = np.arange(n_boxes, dtype=int)
    # Keep track of circuit sizes (not neccessary, but simpler)
    circuit_sizes = np.ones_like(circuits, dtype=int)
    # Handle closest num_connections box pairs
    for i,j in itertools.islice(zip(*asc_dist_ind), num_connections):
        i_circ, j_circ = circuits[[i, j]]
        if i_circ != j_circ:
            # Increase/Reduce circuit size counters by adding j circuit to i circuit
            j_circ_size = circuit_sizes[j_circ]
            circuit_sizes[i_circ] += j_circ_size
            circuit_sizes[j_circ] -= j_circ_size
            # Connect j circuit to i curcuit
            circuits = np.where(circuits == j_circ, i_circ, circuits)
    
    # Sort circuit sizes in desc. order
    sorted_ciruit_sizes = np.sort(circuit_sizes)[::-1]
    # Multiply largest 4 circuit sizes
    result = reduce(lambda a, b: a * b, sorted_ciruit_sizes[:3], 1)
    return result


def solve_part_two(lines: list[str]) -> int:
    # (N,3)
    jboxes = read_jboxes(lines)
    #### PREP (identical to part one)
    n_boxes = jboxes.shape[0]
    # Tile to get distance between all pairs of boxes (N, N, 3)
    distances = np.tile(jboxes[:, np.newaxis, :], reps=(1, n_boxes, 1))
    # Computer pair-wise distances (N, N)
    distances = distances - np.transpose(distances, axes=(1, 0, 2))
    distances = np.linalg.norm(distances, ord=2, axis=2)
    # Set diagonal to inf
    distances[np.diag_indices(n_boxes)] = 1e9
    # Set everything below diagonal to inf
    distances[np.tril_indices_from(distances)] = 1e9
    # Get shortest pair-wise distances
    asc_dist_ind = np.unravel_index(np.argsort(distances, axis=None), distances.shape)
    
    ### SOLVING
    # Keep track of the circuit each box belongs to (initial: box ID = circuit ID)
    circuits = np.arange(n_boxes, dtype=int)
    # Keep track of circuit sizes (not neccessary, but simpler)
    circuit_sizes = np.ones_like(circuits, dtype=int)
    # Keep track of last box pair that gets connected
    last_i, last_j = 0, 0
    # Handle closest box pairs
    for i,j in zip(*asc_dist_ind):
        i_circ, j_circ = circuits[[i, j]]
        if i_circ != j_circ:
            # Increase/Reduce circuit size counters by adding j circuit to i circuit
            j_circ_size = circuit_sizes[j_circ]
            circuit_sizes[i_circ] += j_circ_size
            circuit_sizes[j_circ] -= j_circ_size
            # Connect j circuit to i curcuit
            circuits = np.where(circuits == j_circ, i_circ, circuits)
            if circuit_sizes[i_circ] == n_boxes:
                last_i, last_j = i, j
                break
            
    box_i, box_j = jboxes[[last_i, last_j]]
    
    return box_i[0] * box_j[0]


if __name__ == '__main__':
    test_input= read_input.read_test_input(TEST_INPUT)
    input_path = pathlib.Path(__file__).parent.parent.joinpath(f'ressources/{DAY:02d}.txt')
    real_input = read_input.read_input(str(input_path))

    #################################
    print(f'### DAY {DAY} - PART ONE ###')
    
    test_out_1 = solve_part_one(test_input, 10)
    print(f'Test output: {test_out_1}. Expected output: {TEST_RESULT_PART_ONE}')
    assert test_out_1 == TEST_RESULT_PART_ONE, "Test for part one failed"

    real_out_1 = solve_part_one(real_input, 1000)
    print(f'Real output: {real_out_1}')

    #################################
    print(f'### DAY {DAY} - PART TWO ###')
    
    test_out_2 = solve_part_two(test_input)
    print(f'Test output: {test_out_2}. Expected output: {TEST_RESULT_PART_TWO}')
    assert test_out_2 == TEST_RESULT_PART_TWO, "Test for part two failed"

    real_out_2 = solve_part_two(real_input)
    print(f'Real output: {real_out_2}')
