# solution_q1.py
# DS 442 - Question 1: DFS and BFS for the River Crossing Puzzle

from collections import deque


# Possible boat loads: (missionaries, cannibals)
MOVES = [(0, 1), (0, 2), (1, 0), (1, 1), (2, 0)]


class RiverCrossingProblem:
    # State = (M_left, C_left, M_right, C_right, Boat)

    def __init__(self, start_state):
        self.start_state = start_state

    def get_start_state(self):
        return self.start_state

    def is_goal_state(self, state):
        # Goal is when everyone is on the right side
        return state[0] == 0 and state[1] == 0

    def is_valid(self, state):
        m_left, c_left, m_right, c_right, boat = state

        # No one can be on a bank in a negative amount
        if m_left < 0 or c_left < 0 or m_right < 0 or c_right < 0:
            return False

        # Cannibals cannot outnumber missionaries
        if m_left > 0 and c_left > m_left:
            return False

        if m_right > 0 and c_right > m_right:
            return False

        return True

    def get_successors(self, state):
        m_left, c_left, m_right, c_right, boat = state
        successors = []

        for m, c in MOVES:
            if boat == 'L':
                # Move people from left to right
                next_state = (
                    m_left - m,
                    c_left - c,
                    m_right + m,
                    c_right + c,
                    'R'
                )
            else:
                # Move people from right to left
                next_state = (
                    m_left + m,
                    c_left + c,
                    m_right - m,
                    c_right - c,
                    'L'
                )

            if self.is_valid(next_state):
                successors.append((next_state, (m, c), 1))

        return successors


# Stack is used for DFS
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0


# Queue is used for BFS
class Queue:
    def __init__(self):
        self.items = deque()

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.popleft()

    def is_empty(self):
        return len(self.items) == 0


def graph_search(problem, fringe, reverse_successors=False):
    closed = set()
    expansions = 0

    start = problem.get_start_state()

    # Store state, path, and total cost
    fringe.push((start, [start], 0))

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

            successors = problem.get_successors(state)

            # Reverse for DFS so the moves are explored in order
            if reverse_successors:
                successors.reverse()

            for next_state, action, step_cost in successors:
                fringe.push(
                    (next_state, path + [next_state], cost + step_cost)
                )


def depth_first_search(problem):
    return graph_search(problem, Stack(), reverse_successors=True)


def breadth_first_search(problem):
    return graph_search(problem, Queue())


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

    # Run DFS
    path, cost, expansions = depth_first_search(problem)
    print_solution("Q1.1.a (DFS)", path, cost, expansions)
    print()

    # Run BFS
    path, cost, expansions = breadth_first_search(problem)
    print_solution("Q1.1.b (BFS)", path, cost, expansions)


if __name__ == "__main__":
    main()
