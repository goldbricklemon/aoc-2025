from typing import Optional
import pathlib
from copy import deepcopy
from functools import reduce
from dataclasses import dataclass
from collections import deque
from itertools import chain
import numpy as np
import random
import tqdm

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


def read_machines(lines: list[str]) -> tuple[list[np.ndarray], list[list[tuple]], list[np.ndarray]]:
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
    # Number of presses previously used to reach the this counter state
    previous_presses: int
    # Currently known best number of presses to solve
    # Alternatively: Upper bound of max. presses
    best_total_presses: Optional[int]

    @classmethod
    def button_affects_counter(cls, button: tuple[int], counter_index:int) -> bool:
        return counter_index in button
    
    @classmethod
    def button_criticalities(cls, buttons: list[tuple[int]], state: np.ndarray) -> list[int]:
        """
        Idea for prioritizing certain buttons to test first:
        We should determine the number of presses for those buttons first, that more likely to be needed at all
        Extreme case: If a button b is the only remaining button that affects a non-zero counter c,
        we need to press it to be able to solve c at all.
        To measure this, we define the criticality of a button.
        The criticality of button b for counter c (where b affects c) is the number of total buttons (that can still be pressed)
        that also affect c
        The criticality of button b is then defined as the min. criticality for all of its affected counters.
        
        """
        criticalities = [0] * len(buttons)
        for b_i, button in enumerate(buttons):
            counter_crits = [sum(cls.button_affects_counter(b, ci) for b in buttons) for ci in button]
            for i, ci in enumerate(button):
                # Solved counters are no longer critical
                if state[ci] == 0:
                    counter_crits[i] = state.shape[0] + 1
            criticalities[b_i] = min(counter_crits)
        return criticalities
        

    @property
    def sorted_buttons_and_criticalities(self) -> tuple[list[tuple[int]], list[int]]:
        # Sort remaining buttons based on 
        # 1: Criticality (lower is more critical)
        # 2: The highest remaining counter that it affects (higher is better)
        # 3: the number of counters it affects (higher is better)
        
        criticalities = self.button_criticalities(self.remaining_buttons, self.counter_state)
        sorted_buttons =  sorted(zip(self.remaining_buttons, criticalities), key=lambda x: (x[1], -max(self.counter_state[x[0]]) , -len(x[0])), reverse=False)
        sorted_buttons, sorted_crits = zip(*sorted_buttons)
        return list(sorted_buttons), list(sorted_crits)

    def solve(self) -> tuple[bool, int]:
        n = self.counter_state.shape[0]
        
        # Base case 0: Lower bound on req. presses surpasses previous optimum
        # Consider this state as "unsolvable"
        max_counter = max(self.counter_state)
        if self.best_total_presses and self.previous_presses + max_counter >= self.best_total_presses:
            return False, 0
        
        # All counters that are not zero yet
        remaining_counter_indices = np.where(self.counter_state > 0)[0]
        
        # Base case 1: All solved
        if remaining_counter_indices.shape[0] == 0:
            return True, 0

        # Only keep buttons that can actually be pressed at least once
        self.remaining_buttons = [button for button in self.remaining_buttons if all([c_i in remaining_counter_indices for c_i in button])]

        # Base case 1: Is there a button for all remaining counters? If no, unsolvable
        full_counter_coverage = all([any([self.button_affects_counter(button, c_i) for button in self.remaining_buttons]) 
                                     for c_i in remaining_counter_indices])
        if not full_counter_coverage:
            return False, 0
        
        # Base case 2: Is the lower bound for still required presses already higher than the current optimum?
        # If so, "unsolvable"
        max_button_effect = max(len(button) for button in self.remaining_buttons)
        min_bound_presses = sum(self.counter_state) // max_button_effect
        if self.best_total_presses and self.previous_presses + min_bound_presses >= self.best_total_presses:
            return False, 0
        
        sorted_buttons, sorted_crits = self.sorted_buttons_and_criticalities

        # Recursive case
        # Not solved yet, still multiple buttons available
        # Pick button candidate, starting with the most valuables first (affecting the most counters)
        candidate_button, next_remaining_buttons = sorted_buttons[0], sorted_buttons[1:]
        button_mask = button_to_button_mask(candidate_button, n=n).astype(int)
        # Special case: Is the next button a max. critical one (i.e. the last one which can affect any non-zero counter)
        enforced_n_presses = None
        if sorted_crits[0] == 1:
            # Pick a non-zero critical counter
            critical_indices = [i for i in remaining_counter_indices if not any(self.button_affects_counter(b, i) for b in sorted_buttons[1:])]
            c_i = critical_indices[0]
            counter_value = self.counter_state[c_i]
            if button_mask[c_i]:
                # Press the button to solve this critical counter
                next_state = self.counter_state - (counter_value * button_mask)
                # This must then solve all critical counters of this button
                if not all(next_state[critical_indices] == 0):
                    # No longer solvable
                    return False, 0
                else:
                    # If this works, we have determined the number of presses for this button
                    enforced_n_presses = counter_value
        


        solved = False
        
        # Figure out max presses for candidate button
        max_presses = min(self.counter_state[candidate_button])
        min_presses = 0
        
        # Limit by bound
        if self.best_total_presses:
            max_presses = min(max_presses, self.best_total_presses - self.previous_presses - 1)
            
        # Limit to enforced presses for critical buttons
        if enforced_n_presses:
            max_presses = enforced_n_presses
            min_presses = enforced_n_presses
        
        best_n_presses = -1
        nums = list(range(min_presses, max_presses + 1))
        random.shuffle(nums)
        for n_presses in nums:
            if self.previous_presses == 0:
                print(f"Button: {candidate_button}")
                print(n_presses, max_presses)
            # New trial state: press the button that often and try to solve recursively
            next_state = self.counter_state - (n_presses * button_mask)
            next_solver_state = SolverState(next_state, next_remaining_buttons, previous_presses=self.previous_presses+n_presses, best_total_presses=self.best_total_presses)
            recursive_solved, recursive_n_presses = next_solver_state.solve()
            if recursive_solved:
                solved = True
                n_presses_candidate = recursive_n_presses + n_presses
                if best_n_presses < 0 or n_presses_candidate < best_n_presses:
                    best_n_presses = n_presses_candidate
                if not self.best_total_presses or best_n_presses + self.previous_presses < self.best_total_presses:
                    self.best_total_presses = best_n_presses + self.previous_presses
            
        if not solved:
            best_n_presses = 0
        return solved, best_n_presses


def solve_machine_part_two(target_state: np.ndarray, buttons: list[tuple[int]]) -> int:
    # Create initial solver state, then solve recursively
    # We use the target_state as the initial state, and try to reach the zero-vec
    min_button_effect = min(len(button) for button in buttons)
    solver_state = SolverState(target_state, buttons, previous_presses=0, best_total_presses=(sum(target_state) // min_button_effect) + 1)
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
    for (joults, buttons) in tqdm.tqdm(zip(target_joults, button_sequences), total=len(target_joults)):
        print()
        print(joults)
        print()
        n = solve_machine_part_two(target_state=joults, buttons=buttons)
        results.append(n)
    
    return sum(results)


if __name__ == '__main__':
    test_input= read_input.read_test_input(TEST_INPUT)
    input_path = pathlib.Path(__file__).parent.parent.joinpath(f'ressources/{DAY:02d}.txt')
    real_input = read_input.read_input(str(input_path))

    #################################
    # print(f'### DAY {DAY} - PART ONE ###')
    
    # test_out_1 = solve_part_one(test_input)
    # print(f'Test output: {test_out_1}. Expected output: {TEST_RESULT_PART_ONE}')
    # assert test_out_1 == TEST_RESULT_PART_ONE, "Test for part one failed"

    # real_out_1 = solve_part_one(real_input)
    # print(f'Real output: {real_out_1}')

    #################################
    print(f'### DAY {DAY} - PART TWO ###')
    
    test_out_2 = solve_part_two(test_input)
    print(f'Test output: {test_out_2}. Expected output: {TEST_RESULT_PART_TWO}')
    assert test_out_2 == TEST_RESULT_PART_TWO, "Test for part two failed"

    real_out_2 = solve_part_two(real_input)
    print(f'Real output: {real_out_2}')
