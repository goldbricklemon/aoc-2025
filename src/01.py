import pathlib
from copy import deepcopy
from functools import reduce
import numpy as np
from enum import Enum


from utils import read_input


DAY = 1

TEST_INPUT = \
"""
L68
L30
R48
L5
R60
L55
L1
L99
R14
L82
"""

TEST_RESULT_PART_ONE = 3
TEST_RESULT_PART_TWO = 6


class Direction(Enum):
    LEFT = "L"
    RIGHT = "R"


def parse_instructions(lines: list[str]) -> list[tuple[Direction, int]]:
    return [(Direction(l[0]), int(l[1:])) for l in lines]


class Dial:

    def __init__(self, value:int, max_value:int):
        self.value = value
        self.max_value = max_value
        self.ended_on_zero = 0
        self.passed_zero = 0

    def turn(self, direction:Direction, amount:int):
        full_rotations = amount // (self.max_value + 1)
        match direction:
            case Direction.LEFT:
                new_value = (self.value - amount) % (self.max_value + 1)
                if self.value != 0 and new_value > self.value:
                    self.passed_zero += 1
            case Direction.RIGHT:
                new_value = (self.value + amount) % (self.max_value + 1)
                if new_value != 0 and new_value < self.value:
                    self.passed_zero += 1

        self.value = new_value
        self.passed_zero += full_rotations

        if self.value == 0:
            self.ended_on_zero += 1
        

def solve_part_one(lines: list[str]) -> int:
    instructions = parse_instructions(lines)
    dial = Dial(value=50, max_value=99)
    num_zeros = 0
    for direction, amount in instructions:
        dial.turn(direction, amount)
    return dial.ended_on_zero


def solve_part_two(lines: list[str]) -> int:
    instructions = parse_instructions(lines)
    dial = Dial(value=50, max_value=99)
    num_zeros = 0
    for direction, amount in instructions:
        dial.turn(direction, amount)
    return dial.passed_zero + dial.ended_on_zero


if __name__ == '__main__':
    d = Direction("R")
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
