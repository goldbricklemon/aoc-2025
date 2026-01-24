import pathlib
from copy import deepcopy
from functools import reduce
from dataclasses import dataclass
from collections import deque
from itertools import chain
import numpy as np

from utils import read_input


DAY = 10

TEST_INPUT = \
"""
[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}
[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}
[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}
"""

TEST_RESULT_PART_ONE = 7
TEST_RESULT_PART_TWO = 0

@dataclass
class TrialSequence:
    state: np.ndarray
    button_sequence: set[int]

    def __len__(self):
        return len(self.button_sequence)


def read_machines(lines: list[str]) -> tuple[np.ndarray, list[list[tuple]]]:
    states = []
    button_sequences = []
    # No regex today, just not feeling it
    for line in lines:
        i = line.index("]")
        state = line[1:i]
        state = list(map(lambda c: True if c=="#" else False, state))
        state = np.array(state)
        states.append(state)
        line = line[i+1:]
        buttons = []
        while "(" in line:
            i, j = line.index("("), line.index(")")
            buttons.append([int(c) for c in line[i+1:j].split(",")])
            line = line[j+1:]
        button_sequences.append(buttons)
    # TODO: extract joults as well
    return states, button_sequences


def solve_machine_part_one(target_state: np.ndarray, buttons: list[tuple[int]]) -> int:
    # Generate bit-masks from buttons
    button_masks = []
    for button in buttons:
        mask = np.zeros_like(target_state)
        for i in button:
            mask[i] = True
        button_masks.append(mask)
    button_numbers = set(range(len(buttons)))
    # Lets try with semi-brute force including branch-and-bound
    # Include loop detection
    n_states = 2 ** (target_state.shape[0])
    reached_states = np.zeros((n_states,), dtype=bool)
    reached_states[0] = True

    def mask_to_int(mask: np.ndarray) -> int:
        value = 0
        for i, b in enumerate(mask[::-1]):
            value |= (int(b) << i)
        return value
    
    target_state_value = mask_to_int(target_state)

    # Generate seed trial
    trials = deque([TrialSequence(state=np.zeros_like(target_state), button_sequence=set())])
    min_n_presses = -1
    while min_n_presses == -1:
        trial = trials.popleft()
        # Never press a button more than once
        # Pressing a button two times in a sequence equals a no-op
        for b_i in button_numbers.difference(trial.button_sequence):
            mask = button_masks[b_i]
            new_state = np.logical_xor(trial.state, mask)
            new_state_value = mask_to_int(new_state)
            # Check if solved
            if new_state_value == target_state_value:
                min_n_presses = len(trial) + 1
                break
            
            # Don't visit a machine state more than once
            if reached_states[new_state_value]:
                continue
            
            # Prepare follow-up trial state
            extended_button_sequence = set(chain(trial.button_sequence, (b_i,)))
            next_trial = TrialSequence(new_state, button_sequence=extended_button_sequence)
            trials.append(next_trial)
            # Mark trial state in loop detection
            reached_states[new_state_value] = True

    return min_n_presses


def solve_part_one(lines: list[str]) -> int:
    states, button_sequences = read_machines(lines)
    results = []
    for state, buttons in zip(states, button_sequences):
        n = solve_machine_part_one(state, buttons)
        results.append(n)
    
    return sum(results)


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
