# solution_q2.py
# Question 2: Uniform Cost Search with non-uniform action costs
#
# Run with: python solution_q2.py           (runs both cost models)
#           python solution_q2.py A         (runs only cost model A)
#           python solution_q2.py B         (runs only cost model B)
#
# You can also pick the model by putting a second line in input.txt:
#     3, 3, 0, 0, L
#     A
#
# Cost Model A: 2 per missionary in the boat, 1 per cannibal.
# Cost Model B: going left to right costs 2, coming back costs 1.
#
# UCS orders the fringe by g(n), the cost so far, like in lecture.

import heapq
import sys

# All the ways the boat can be loaded: (missionaries, cannibals)
# The boat holds 1 or 2 people.
MOVES = [(0, 1), (0, 2), (1, 0), (1, 1), (2, 0)]


def is_safe(state):
    # A state is safe if nobody is negative and cannibals never outnumber
    # missionaries on a bank that has missionaries on it.
    m_left, c_left, m_right, c_right, boat = state

    if m_left < 0 or c_left < 0 or m_right < 0 or c_right < 0:
        return False
    if m_left > 0 and c_left > m_left:
        return False
    if m_right > 0 and c_right > m_right:
        return False
    return True


def get_successors(state):
    # Returns a list of (move, new_state) for every legal move from this state.
    m_left, c_left, m_right, c_right, boat = state
    successors = []

    for move in MOVES:
        m, c = move

        if boat == 'L':
            # Boat goes left to right, so those people leave the left bank.
            if m > m_left or c > c_left:
                continue
            new_state = (m_left - m, c_left - c, m_right + m, c_right + c, 'R')
        else:
            # Boat goes right to left.
            if m > m_right or c > c_right:
                continue
            new_state = (m_left + m, c_left + c, m_right - m, c_right - c, 'L')

        if is_safe(new_state):
            successors.append((move, new_state))

    return successors


def is_goal(state):
    # Everyone made it to the right bank.
    return state[0] == 0 and state[1] == 0


def get_cost(move, state, model):
    # How much this move costs, depending on which cost model we're using.
    if model == 'A':
        # Pay by who is in the boat.
        m, c = move
        return 2 * m + 1 * c
    else:
        # Pay by direction. The boat is still on the old side here,
        # so boat == 'L' means we are about to go left to right.
        if state[4] == 'L':
            return 2
        else:
            return 1


def ucs(start, model):
    # Fringe holds (g, order, state, path). heapq always pops the smallest g.
    # The order number is just a counter so that when two nodes tie on g,
    # whichever went in first comes out first. Without it Python would
    # compare the states themselves, which picks ties in a weird order.
    fringe = []
    order = 0
    heapq.heappush(fringe, (0, order, start, [start]))

    closed = set()
    expansions = 0

    while len(fringe) > 0:
        g, count, state, path = heapq.heappop(fringe)

        # Skip it if we already expanded this state.
        if state in closed:
            continue
        closed.add(state)

        # Stop when we DEQUEUE the goal, not when we enqueue it.
        if is_goal(state):
            return path, g, expansions

        expansions = expansions + 1

        for move, new_state in get_successors(state):
            if new_state not in closed:
                new_g = g + get_cost(move, state, model)
                order = order + 1
                heapq.heappush(fringe, (new_g, order, new_state, path + [new_state]))

    return None, 0, expansions


def read_input():
    # First line is the start state. An optional second line is the cost model.
    f = open("input.txt")
    lines = f.readlines()
    f.close()

    parts = lines[0].strip().split(",")
    m_left = int(parts[0])
    c_left = int(parts[1])
    m_right = int(parts[2])
    c_right = int(parts[3])
    boat = parts[4].strip().upper()
    start = (m_left, c_left, m_right, c_right, boat)

    model = None
    if len(lines) > 1:
        second = lines[1].strip().upper()
        if second == 'A' or second == 'B':
            model = second

    return start, model


def path_to_string(path):
    pieces = []
    for state in path:
        pieces.append("(%d,%d,%d,%d,%s)" % state)
    return " -> ".join(pieces)


def print_answer(name, path, cost, expansions):
    print("The solution of " + name + " is:")
    if path is None:
        print("Solution Path: no solution found")
        print("Total cost = N/A")
    else:
        print("Solution Path: " + path_to_string(path))
        print("Total cost = " + str(cost))
    print("Number of node expansions = " + str(expansions))


def main():
    start, file_model = read_input()

    # A model given on the command line beats the one in input.txt.
    model = file_model
    if len(sys.argv) > 1:
        model = sys.argv[1].strip().upper()

    if model == 'A' or model == 'B':
        models = [model]
    else:
        models = ['A', 'B']

    first = True
    for m in models:
        if not first:
            print()
        first = False

        path, cost, expansions = ucs(start, m)
        print_answer("Q2.1 (UCS, cost model " + m + ")", path, cost, expansions)


main()