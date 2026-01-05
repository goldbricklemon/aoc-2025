import pathlib
from copy import deepcopy
from functools import reduce
import numpy as np
from enum import Enum

from utils import read_input


DAY = 6

TEST_INPUT = \
"""
123 328  51 64 
 45 64  387 23 
  6 98  215 314
*   +   *   +  
"""

TEST_RESULT_PART_ONE = 4277556
TEST_RESULT_PART_TWO = 3263827

class Problem:
    
    class Operator(Enum):
        ADD = "+"
        MULTIPLY = "*"
    
    def __init__(self, operands: list[int], operator: Operator | None=None) -> None:
        self.operands = operands
        self.operator = operator
        
    def solve(self) -> int:
        match self.operator:
            case Problem.Operator.ADD:
                return sum(self.operands)
            case Problem.Operator.MULTIPLY:
                return reduce(lambda a, b: a * b, self.operands, 1)
            case _:
                raise ValueError(self.operator)
                

def read_sheet(lines: list[str]) -> list[Problem]:
    
    def extract_numbers(line: str) -> list[int]:
        return[int(s) for s in line.strip().split(" ") if s.isdigit()]
    
    num_problems = len(extract_numbers(lines[0]))
    problems = [Problem([], None) for _ in range(num_problems)]
    
    # Assign numbers to problems
    for line in lines[:-1]:
        for i, num in enumerate(extract_numbers(line)):
            problems[i].operands.append(num)
                
    # Assing all operators from the last line
    for i, op_str in enumerate(s for s in lines[-1].split(" ") if s != ""):
        problems[i].operator = Problem.Operator(op_str.strip()) 
    
    return problems


def solve_part_one(lines: list[str]) -> int:
    problems = read_sheet(lines)
    return sum(problem.solve() for problem in problems)

#########################################################

def read_sheet_part_two(lines: list[str]) -> list[Problem]:
    last_line = lines[-1]
    problems = []
    i = 0
    while i < len(last_line):
        op_char = last_line[i]
        problem = Problem([], operator=Problem.Operator(op_char))
        problems.append(problem)
        op_i = i
        while i < len(last_line) and (i == op_i or last_line[i] == " "):
            num_str = "".join([line[i] for line in lines[:-1]]).strip()
            if len(num_str) >= 1:
                problem.operands.append(int(num_str))
            i += 1
    
    return problems


def solve_part_two(lines: list[str]) -> int:
    problems = read_sheet_part_two(lines)
    return sum(problem.solve() for problem in problems)


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
