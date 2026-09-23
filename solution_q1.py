# solution_q1.py
# DS 442 - Question 1: DFS and BFS for the River Crossing Puzzle
# Run with: python solution_q1.py
#
# How we set this up which follows the Uninformed Search and Graph Search lecture slides:
#   - The puzzle is written as a search problem: start state, goal test,
#     and a successor function that returns (next state, action, cost).
#   - DFS and BFS use the exact same GRAPH-SEARCH function. The only
#     difference is the fringe: DFS uses a LIFO stack, BFS uses a FIFO queue.
#   - GRAPH-SEARCH keeps a closed set (a Python set, not a list) so the
#     same state is never expanded twice.
#   - The goal test happens when a node is removed from the fringe,
#     not when it is added.
#   - A node expansion is counted every time a state gets added to the
#     closed set and its successors are generated. The goal node isn't
#     counted since the search returns before expanding it.
#   - Every action costs 1, so total cost = number of boat trips.

from collections import deque

# All the ways the boat can be loaded: (missionaries, cannibals).
# The boat holds 1 or 2 people.
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

        # nobody can be negative
        if m_left < 0 or c_left < 0 or m_right < 0 or c_right < 0:
            return False
        # check BOTH banks, not just the one the boat left
        if m_left > 0 and c_left > m_left:
            return False
        if m_right > 0 and c_right > m_right:
            return False
        return True

    def get_successors(self, state):
        # returns a list of (next_state, action, step_cost)
        m_left, c_left, m_right, c_right, boat = state
        successors = []

        for m, c in MOVES:
            if boat == 'L':
                # boat goes left -> right
                next_state = (m_left - m, c_left - c, m_right + m, c_right + c, 'R')
            else:
                # boat goes right -> left
                next_state = (m_left + m, c_left + c, m_right - m, c_right - c, 'L')

            if self.is_valid(next_state):
                successors.append((next_state, (m, c), 1))

        return successors


# Fringe data structures 

class Stack:
    # LIFO: last thing pushed is the first thing popped which is used for DFS
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0


class Queue:
    # FIFO: first thing pushed is the first thing popped which is used for BFS
    def __init__(self):
        self.items = deque()

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.popleft()

    def is_empty(self):
        return len(self.items) == 0


# Search

def graph_search(problem, fringe, reverse_successors=False):
    # GRAPH-SEARCH:
    #   closed <- empty set
    #   put start node in fringe
    #   loop: pop node, goal test, if state not in closed -> add to closed and expand
    #
    # Each node on the fringe is (state, path of states, total cost)
    closed = set()
    expansions = 0

    start = problem.get_start_state()
    fringe.push((start, [start], 0))

    while True:
        if fringe.is_empty():
            return None, None, expansions    # = failure

        state, path, cost = fringe.pop()

        if problem.is_goal_state(state):
            return path, cost, expansions

        if state not in closed:
            closed.add(state)
            expansions += 1

            successors = problem.get_successors(state)
            if reverse_successors:
                # For the stack, push in reverse so the first move in MOVES
                # ends up on top and is explored first (left-to-right like
                # the DFS example in lecture)
                successors.reverse()

            for next_state, action, step_cost in successors:
                fringe.push((next_state, path + [next_state], cost + step_cost))


def depth_first_search(problem):
    return graph_search(problem, Stack(), reverse_successors=True)


def breadth_first_search(problem):
    return graph_search(problem, Queue())


# Input / Output

def read_start_state(filename):
    # input.txt looks like: 3, 3, 0, 0, L
    f = open(filename)
    line = f.readline().strip()
    f.close()

    parts = [p.strip() for p in line.split(",")]
    return (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), parts[4].upper())


def path_to_string(path):
    return " -> ".join("(%d,%d,%d,%d,%s)" % s for s in path)


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

    path, cost, expansions = depth_first_search(problem)
    print_solution("Q1.1.a (DFS)", path, cost, expansions)
    print()

    path, cost, expansions = breadth_first_search(problem)
    print_solution("Q1.1.b (BFS)", path, cost, expansions)


if __name__ == "__main__":
    main()
