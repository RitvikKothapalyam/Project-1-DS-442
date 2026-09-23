# solution_q3.py
# DS 442 - Question 3: A* Search with Admissible Heuristics (Cost Model A)
#
# Run with:
#   python solution_q3.py        -> runs heuristics 1, 2 and 3
#   python solution_q3.py 2      -> runs only heuristic 2 (1, 2 or 3)
#
# How we set this up follows the Informed Search / A* slides:
#   - Same search problem as Q1/Q2, using Cost Model A
#     (2 per missionary + 1 per cannibal on the boat).
#   - A* is the same GRAPH-SEARCH as before. The fringe is a priority
#     queue ordered by f(n) = g(n) + h(n), where g(n) is the path cost so
#     far (backward cost) and h(n) is the heuristic (forward cost).
#   - The closed set is a Python set so no state gets expanded twice.
#   - The goal test happens when a node is DEQUEUED, not when it's
#     enqueued ("When should A* terminate?" slide).
#   - A node expansion is counted every time a state gets added to the
#     closed set and its successors are generated.
#
# Heuristics:
#   h1(s) = 2*M_left + C_left
#   h2(s) = ceil((2*M_left + C_left) / 3)
#   h3(s) = h1(s) + 2 * (minimum number of return trips still needed)
#     where, with N = M_left + C_left people still on the left:
#       boat on L: at least max(0, N - 2) return trips
#       boat on R: at least N return trips
#     (see the writeup for why this is admissible)

import sys
import heapq
import math

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

    def step_cost(self, move):
        # Cost Model A: missionaries are twice as costly to carry
        m, c = move
        return 2 * m + 1 * c

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
                successors.append((next_state, (m, c), self.step_cost((m, c))))

        return successors


# Heuristics

def heuristic_1(state):
    # Passenger weight remaining: everyone on the left still has to be
    # carried across at least once
    m_left, c_left = state[0], state[1]
    return 2 * m_left + c_left


def heuristic_2(state):
    # Trip-packing lower bound
    m_left, c_left = state[0], state[1]
    return math.ceil((2 * m_left + c_left) / 3)


def heuristic_3(state):
    # h1 plus the cost of the return trips we know we still have to make.
    # Every return trip carries at least 1 person (cost >= 1), and whoever
    # comes back has to be carried across again (cost >= 1 more).
    # So each required return trip adds at least 2 on top of h1.
    m_left, c_left, m_right, c_right, boat = state
    people_left = m_left + c_left

    if boat == 'L':
        returns_needed = max(0, people_left - 2)
    else:
        returns_needed = people_left

    return heuristic_1(state) + 2 * returns_needed


HEURISTICS = {1: heuristic_1, 2: heuristic_2, 3: heuristic_3}


# Fringe data structure

class PriorityQueue:
    # Pops the item with the lowest priority first.
    # The counter breaks ties so equal-priority nodes come out in the
    # order they were added.
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

def a_star_search(problem, heuristic):
    # GRAPH-SEARCH from the slides, with priority f(n) = g(n) + h(n):
    #   closed <- empty set
    #   put start node in fringe
    #   loop: pop lowest-f node, goal test, if state not in closed -> add to closed and expand
    #
    # Each node on the fringe is (state, path of states, total cost g)
    closed = set()
    expansions = 0
    fringe = PriorityQueue()

    start = problem.get_start_state()
    fringe.push((start, [start], 0), 0 + heuristic(start))

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
                g = cost + step_cost
                f = g + heuristic(next_state)
                fringe.push((next_state, path + [next_state], g), f)


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

    # pick the heuristic from the command line, otherwise run all three
    if len(sys.argv) > 1:
        if sys.argv[1] not in ('1', '2', '3'):
            print("Heuristic must be 1, 2 or 3")
            return
        choices = [int(sys.argv[1])]
    else:
        choices = [1, 2, 3]

    for i in range(len(choices)):
        h = choices[i]
        path, cost, expansions = a_star_search(problem, HEURISTICS[h])
        print_solution("Q3.1 (Heuristic " + str(h) + ")", path, cost, expansions)
        if i < len(choices) - 1:
            print()


if __name__ == "__main__":
    main()
