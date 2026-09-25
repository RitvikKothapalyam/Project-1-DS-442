# solution_q3.py
# DS 442 - Question 3: A* Search with Admissible Heuristics

import sys
import heapq
import math


# Possible boat loads: (missionaries, cannibals)
MOVES = [(0, 1), (0, 2), (1, 0), (1, 1), (2, 0)]


class RiverCrossingProblem:
    # State = (M_left, C_left, M_right, C_right, Boat)

    def __init__(self, start_state):
        self.start_state = start_state

    def get_start_state(self):
        return self.start_state

    def is_goal_state(self, state):
        # Everyone is on the right bank
        return state[0] == 0 and state[1] == 0

    def is_valid(self, state):
        m_left, c_left, m_right, c_right, boat = state

        # Check for negative values
        if m_left < 0 or c_left < 0 or m_right < 0 or c_right < 0:
            return False

        # Cannibals cannot outnumber missionaries
        if m_left > 0 and c_left > m_left:
            return False

        if m_right > 0 and c_right > m_right:
            return False

        return True

    def step_cost(self, move):
        # Cost Model A
        m, c = move
        return 2 * m + c

    def get_successors(self, state):
        m_left, c_left, m_right, c_right, boat = state
        successors = []

        for m, c in MOVES:
            if boat == 'L':
                # Move from left to right
                next_state = (
                    m_left - m,
                    c_left - c,
                    m_right + m,
                    c_right + c,
                    'R'
                )
            else:
                # Move from right to left
                next_state = (
                    m_left + m,
                    c_left + c,
                    m_right - m,
                    c_right - c,
                    'L'
                )

            if self.is_valid(next_state):
                cost = self.step_cost((m, c))
                successors.append((next_state, (m, c), cost))

        return successors


# Heuristic functions

def heuristic_1(state):
    # Cost of carrying everyone on the left across
    m_left, c_left = state[0], state[1]
    return 2 * m_left + c_left


def heuristic_2(state):
    # Lower bound based on carrying up to two people per trip
    m_left, c_left = state[0], state[1]
    return math.ceil((2 * m_left + c_left) / 3)


def heuristic_3(state):
    # h1 plus a lower bound for the return trips
    m_left, c_left, m_right, c_right, boat = state
    people_left = m_left + c_left

    if boat == 'L':
        returns_needed = max(0, people_left - 2)
    else:
        returns_needed = people_left

    return heuristic_1(state) + 2 * returns_needed


HEURISTICS = {
    1: heuristic_1,
    2: heuristic_2,
    3: heuristic_3
}


# Priority queue used by A*
class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        # Count keeps tied priorities in insertion order
        heapq.heappush(self.heap, (priority, self.count, item))
        self.count += 1

    def pop(self):
        priority, count, item = heapq.heappop(self.heap)
        return item

    def is_empty(self):
        return len(self.heap) == 0


def a_star_search(problem, heuristic):
    closed = set()
    expansions = 0
    fringe = PriorityQueue()

    start = problem.get_start_state()

    # Store state, path, and cost so far
    fringe.push(
        (start, [start], 0),
        heuristic(start)
    )

    while True:
        if fringe.is_empty():
            return None, None, expansions

        state, path, cost = fringe.pop()

        # Check the goal when the node is removed
        if problem.is_goal_state(state):
            return path, cost, expansions

        if state not in closed:
            closed.add(state)
            expansions += 1

            for next_state, action, step_cost in problem.get_successors(state):
                g = cost + step_cost
                f = g + heuristic(next_state)

                fringe.push(
                    (next_state, path + [next_state], g),
                    f
                )


def read_start_state(filename):
    # Read the starting state from input.txt
    with open(filename) as f:
        line = f.readline().strip()

    parts = [p.strip() for p in line.split(",")]

    return (
        int(parts[0]),
        int(parts[1]),
        int(parts[2]),
        int(parts[3]),
        parts[4].upper()
    )


def path_to_string(path):
    return " -> ".join(
        "(%d,%d,%d,%d,%s)" % state for state in path
    )


def print_solution(name, path, cost, expansions):
    print("The solution of " + name + " is:")

    if path is None:
        print("Solution Path: no solution found")
        print("Total cost = N/A")
    else:
        print("Solution Path: " + path_to_string(path))
        print("Total cost = " + str(cost))

    print("Number of node expansions = " + str(expansions))


def main():
    problem = RiverCrossingProblem(read_start_state("input.txt"))

    # Run one heuristic if specified, otherwise run all three
    if len(sys.argv) > 1:
        if sys.argv[1] not in ('1', '2', '3'):
            print("Heuristic must be 1, 2 or 3")
            return

        choices = [int(sys.argv[1])]
    else:
        choices = [1, 2, 3]

    for i in range(len(choices)):
        h = choices[i]

        path, cost, expansions = a_star_search(
            problem,
            HEURISTICS[h]
        )

        print_solution(
            "Q3.1 (Heuristic " + str(h) + ")",
            path,
            cost,
            expansions
        )

        if i < len(choices) - 1:
            print()


if __name__ == "__main__":
    main()
