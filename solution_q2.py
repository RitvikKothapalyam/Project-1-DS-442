# solution_q2.py
# DS 442 - Question 2: Uniform Cost Search for the River Crossing Puzzle

import sys
import heapq


# Possible boat loads: (missionaries, cannibals)
MOVES = [(0, 1), (0, 2), (1, 0), (1, 1), (2, 0)]


class RiverCrossingProblem:
    # State = (M_left, C_left, M_right, C_right, Boat)

    def __init__(self, start_state, cost_model):
        self.start_state = start_state
        self.cost_model = cost_model

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

    def step_cost(self, move, boat):
        m, c = move

        if self.cost_model == 'A':
            # Model A: missionaries cost 2, cannibals cost 1
            return 2 * m + c
        else:
            # Model B: left-to-right costs 2, right-to-left costs 1
            if boat == 'L':
                return 2
            else:
                return 1

    def get_successors(self, state):
        m_left, c_left, m_right, c_right, boat = state
        successors = []

        for m, c in MOVES:
            if boat == 'L':
                # Move from left bank to right bank
                next_state = (
                    m_left - m,
                    c_left - c,
                    m_right + m,
                    c_right + c,
                    'R'
                )
            else:
                # Move from right bank to left bank
                next_state = (
                    m_left + m,
                    c_left + c,
                    m_right - m,
                    c_right - c,
                    'L'
                )

            if self.is_valid(next_state):
                cost = self.step_cost((m, c), boat)
                successors.append((next_state, (m, c), cost))

        return successors


# Priority queue for UCS
class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        # Count keeps the order consistent when priorities are tied
        heapq.heappush(self.heap, (priority, self.count, item))
        self.count += 1

    def pop(self):
        priority, count, item = heapq.heappop(self.heap)
        return item

    def is_empty(self):
        return len(self.heap) == 0


def uniform_cost_search(problem):
    closed = set()
    expansions = 0
    fringe = PriorityQueue()

    start = problem.get_start_state()

    # Store state, path, and total path cost
    fringe.push((start, [start], 0), 0)

    while True:
        if fringe.is_empty():
            return None, None, expansions

        state, path, cost = fringe.pop()

        # UCS checks the goal when the node is removed
        if problem.is_goal_state(state):
            return path, cost, expansions

        if state not in closed:
            closed.add(state)
            expansions += 1

            for next_state, action, step_cost in problem.get_successors(state):
                new_cost = cost + step_cost

                fringe.push(
                    (next_state, path + [next_state], new_cost),
                    new_cost
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
    start = read_start_state("input.txt")

    # Run a specific model if one was provided
    if len(sys.argv) > 1:
        models = [sys.argv[1].upper()]

        if models[0] not in ('A', 'B'):
            print("Cost model must be A or B")
            return
    else:
        # Otherwise run both models
        models = ['A', 'B']

    for i in range(len(models)):
        model = models[i]
        problem = RiverCrossingProblem(start, model)

        path, cost, expansions = uniform_cost_search(problem)

        print_solution(
            "Q2.1 (UCS, cost model " + model + ")",
            path,
            cost,
            expansions
        )

        if i < len(models) - 1:
            print()


if __name__ == "__main__":
    main()
