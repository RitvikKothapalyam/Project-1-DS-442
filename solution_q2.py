# solution_q2.py
# DS 442 - Question 2: Uniform Cost Search for the River Crossing Puzzle
#
# Run with:
#   python solution_q2.py        -> runs both cost models (A then B)
#   python solution_q2.py A      -> cost model A only
#   python solution_q2.py B      -> cost model B only
#
# How we set this up which follows the Uninformed Search and Graph Search slides:
#   - Same search problem as Q1, but get_successors now returns the real
#     step cost of each action based on the chosen cost model.
#   - UCS is the same GRAPH-SEARCH as Q1. The only difference is the fringe:
#     UCS uses a priority queue ordered by cumulative path cost g(n).
#   - The closed set is a Python set so no state gets expanded twice.
#   - The goal test happens when a node is removed from the fringe, not
#     when it's added. This matters for UCS: a goal can be added with a
#     high cost and a cheaper path to it might still show up later.
#   - A node expansion is counted every time a state gets added to the
#     closed set and its successors are generated.
#
# Cost models:
#   A: 2 per missionary + 1 per cannibal on the boat
#   B: left -> right trip costs 2, right -> left trip costs 1

import sys
import heapq

# All the ways the boat can be loaded: (missionaries, cannibals).
# The boat holds 1 or 2 people.
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

        # nobody can be negative
        if m_left < 0 or c_left < 0 or m_right < 0 or c_right < 0:
            return False
        # check BOTH banks, not just the one the boat left
        if m_left > 0 and c_left > m_left:
            return False
        if m_right > 0 and c_right > m_right:
            return False
        return True

    def step_cost(self, move, boat):
        m, c = move
        if self.cost_model == 'A':
            # missionaries are twice as costly to carry as cannibals
            return 2 * m + 1 * c
        else:
            # cost model B: against the current (L -> R) is harder
            if boat == 'L':
                return 2
            else:
                return 1

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
                successors.append((next_state, (m, c), self.step_cost((m, c), boat)))

        return successors


# Fringe data structure

class PriorityQueue:
    # Pops the item with the lowest priority (cheapest path cost) first.
    # The counter breaks ties so equal-cost nodes come out in the order
    # they were added.
    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        heapq.heappush(self.heap, (priority, self.count, item))
        self.count += 1

    def pop(self):
        priority, count, item = heapq.heappop(self.heap)
        return item

    def is_empty(self):
        return len(self.heap) == 0


# Search

def uniform_cost_search(problem):
    # GRAPH-SEARCH from the slides, with a priority queue as the fringe:
    #   closed <- empty set
    #   put start node in fringe
    #   loop: pop cheapest node, goal test, if state not in closed -> add to closed and expand
    #
    # Each node on the fringe is (state, path of states, total cost g)
    closed = set()
    expansions = 0
    fringe = PriorityQueue()

    start = problem.get_start_state()
    fringe.push((start, [start], 0), 0)

    while True:
        if fringe.is_empty():
            return None, None, expansions    # failure

        state, path, cost = fringe.pop()

        if problem.is_goal_state(state):
            return path, cost, expansions

        if state not in closed:
            closed.add(state)
            expansions += 1

            for next_state, action, step_cost in problem.get_successors(state):
                new_cost = cost + step_cost
                fringe.push((next_state, path + [next_state], new_cost), new_cost)


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
    start = read_start_state("input.txt")

    # pick the cost model from the command line, otherwise run both
    if len(sys.argv) > 1:
        models = [sys.argv[1].upper()]
        if models[0] not in ('A', 'B'):
            print("Cost model must be A or B")
            return
    else:
        models = ['A', 'B']

    for i in range(len(models)):
        model = models[i]
        problem = RiverCrossingProblem(start, model)
        path, cost, expansions = uniform_cost_search(problem)
        print_solution("Q2.1 (UCS, cost model " + model + ")", path, cost, expansions)
        if i < len(models) - 1:
            print()


if __name__ == "__main__":
    main()
