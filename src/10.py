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
TEST_RESULT_PART_TWO = 33

@dataclass
class TrialSequence:
    state: np.ndarray
    button_sequence: set[int]

    def __len__(self):
        return len(self.button_sequence)
    
def button_to_button_mask(button: tuple[int], n: int) -> np.ndarray:
    mask = np.zeros((n,), dtype=bool)
    for i in button:
        mask[i] = True
    return mask


def read_machines(lines: list[str]) -> tuple[np.ndarray, list[list[tuple]], list[np.ndarray]]:
    states = []
    button_sequences = []
    joults_states = []
    # No regex today, just not feeling it
    for line in lines:
        i = line.index("]")
        state = list(map(lambda c: True if c=="#" else False, line[1:i]))
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
        joults = np.array([int(c) for c in line[line.index("{")+1: line.index("}")].split(",")])
        joults_states.append(joults)
    return states, button_sequences, joults_states


def solve_machine_part_one(target_state: np.ndarray, buttons: list[tuple[int]]) -> int:
    # Generate bit-masks from buttons
    button_masks = [button_to_button_mask(button, target_state.shape[0]) for button in buttons]
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


@dataclass
class SolverState:
    counter_state: np.ndarray
    remaining_buttons: list[tuple[int]]

    def _button_affects_counter(self, button: tuple[int], counter_index:int) -> bool:
        return counter_index in button

    @property
    def sorted_buttons(self) -> list[tuple[int]]:
        return sorted(self.remaining_buttons, key=lambda x: len(x), reverse=True)

    def solve(self) -> tuple[bool, int]:
        n = self.counter_state.shape[0]
        # All counters that are not zero yet
        remaining_counter_indices = np.where(self.counter_state > 0)[0]

        # Only keep buttons that can actually be pressed at least once
        self.remaining_buttons = [button for button in self.remaining_buttons if all([c_i in remaining_counter_indices for c_i in button])]

        # Base case 0: All solved
        if remaining_counter_indices.shape[0] == 0:
            return True, 0

        # Base case 2: Is there a button for all remaining counters? If no, return False, 0
        full_counter_coverage = all([any([self._button_affects_counter(button, c_i) for button in self.remaining_buttons]) 
                                     for c_i in remaining_counter_indices])
        if not full_counter_coverage:
            return False, 0
        

        # Base case 3: Is there only one button left? Check if solvable, record presses if so
        if len(self.remaining_buttons) == 1:
            # Pick the non-zero counter
            c_i = remaining_counter_indices[0]
            counter_value = self.counter_state[c_i]
            button = self.remaining_buttons[0]
            button_mask = button_to_button_mask(button, n=n)
            # Unsolvable by default
            solvable, n_presses = False, 0
            if button_mask[c_i]:
                next_state = self.counter_state - (counter_value * button_mask.astype(int))
                if all(next_state == 0):
                    # Solved
                    solvable, n_presses = True, int(counter_value)

            return solvable, n_presses
        

        # Recursive case
        # Not solved yet, still multiple buttons available
        # Pick button candidate, starting with the most valuables first (affecting the most counters)
        sorted_button_candidates = self.sorted_buttons
        solved = False
        best_n_presses = -1
        for b_i, candidate_button in enumerate(sorted_button_candidates):
            # Convert to ones mask
            ones_mask = button_to_button_mask(candidate_button, n=n).astype(int)
            # How often can we press this button given the remaining state?
            n_presses = int(min([self.counter_state[i] for i in candidate_button]))
            # New trial state: press the buttons that often and try to solve recursively
            next_state = self.counter_state - (n_presses * ones_mask)
            next_remaining_buttons = [button for i, button in enumerate(sorted_button_candidates) if i != b_i]
            next_solver_state = SolverState(next_state, next_remaining_buttons)
            recursive_solved, recursive_n_presses = next_solver_state.solve()
            if recursive_solved:
                solved = True
                n_presses_candidate = recursive_n_presses + n_presses
                if best_n_presses == -1 or n_presses_candidate < best_n_presses:
                    best_n_presses = n_presses_candidate
            
        if not solved:
            best_n_presses = 0
        return solved, best_n_presses


def solve_machine_part_two(target_state: np.ndarray, buttons: list[tuple[int]]) -> int:
    # Create initial solver state, then solve recursively
    # We use the target_state as the initial state, and try to reach the zero-vec
    solver_state = SolverState(target_state, buttons)
    solved, n_presses = solver_state.solve()
    if not solved:
        print(target_state)
        print(buttons)
        raise RecursionError("Recursive solver did not find solution")

    return n_presses



def solve_part_one(lines: list[str]) -> int:
    states, button_sequences, _ = read_machines(lines)
    results = []
    for state, buttons in zip(states, button_sequences):
        n = solve_machine_part_one(state, buttons)
        results.append(n)
    
    return sum(results)


def solve_part_two(lines: list[str]) -> int:
    _, button_sequences, target_joults = read_machines(lines)
    results = []
    for joults, buttons in zip(target_joults, button_sequences):
        n = solve_machine_part_two(target_state=joults, buttons=buttons)
        results.append(n)
    
    return sum(results)


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
