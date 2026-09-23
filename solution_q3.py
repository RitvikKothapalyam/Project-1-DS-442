# solution_q3.py
# Question 3: A* Search with admissible heuristics
# Run with: python solution_q3.py
#
# Uses Cost Model A: each missionary in the boat costs 2, each cannibal costs 1.
# A* orders the fringe by f(n) = g(n) + h(n), like in lecture.

import heapq
import math

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


def get_cost(move):
    # Cost Model A: 2 per missionary, 1 per cannibal.
    m, c = move
    return 2 * m + 1 * c


# ---------- The three heuristics ----------

def h1(state):
    # Weight of everyone still waiting on the left bank.
    m_left = state[0]
    c_left = state[1]
    return 2 * m_left + 1 * c_left


def h2(state):
    # Same weight, divided by 3 and rounded up.
    m_left = state[0]
    c_left = state[1]
    return math.ceil((2 * m_left + 1 * c_left) / 3)


def h3(state):
    # My own heuristic. h1 only pays to send people over once, but the boat
    # can't row itself back. Every return trip needs someone in it, and that
    # person has to be brought over again later, so that's 2 extra cost per
    # return trip at minimum.
    m_left, c_left, m_right, c_right, boat = state

    weight = 2 * m_left + 1 * c_left
    people = m_left + c_left

    if people == 0:
        return 0

    # How many return trips are still needed, at minimum.
    if boat == 'L':
        trips_back = math.ceil(people / 2) - 1
        if trips_back < 0:
            trips_back = 0
    else:
        trips_back = math.ceil(people / 2)

    return weight + 2 * trips_back


# ---------- A* search ----------

def a_star(start, h):
    # Fringe holds (f, g, state, path). heapq always pops the smallest f.
    fringe = []
    heapq.heappush(fringe, (h(start), 0, start, [start]))

    closed = set()
    expansions = 0

    while len(fringe) > 0:
        f, g, state, path = heapq.heappop(fringe)

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
                new_g = g + get_cost(move)
                new_f = new_g + h(new_state)
                heapq.heappush(fringe, (new_f, new_g, new_state, path + [new_state]))

    return None, 0, expansions


# ---------- Input and output ----------

def read_start_state():
    # input.txt looks like: 3, 3, 0, 0, L
    f = open("input.txt")
    line = f.readline().strip()
    f.close()

    parts = line.split(",")
    m_left = int(parts[0])
    c_left = int(parts[1])
    m_right = int(parts[2])
    c_right = int(parts[3])
    boat = parts[4].strip().upper()

    return (m_left, c_left, m_right, c_right, boat)


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
    start = read_start_state()

    path, cost, expansions = a_star(start, h1)
    print_answer("Q3.1 (Heuristic 1)", path, cost, expansions)
    print()

    path, cost, expansions = a_star(start, h2)
    print_answer("Q3.1 (Heuristic 2)", path, cost, expansions)
    print()

    path, cost, expansions = a_star(start, h3)
    print_answer("Q3.2 Part C (Heuristic 3)", path, cost, expansions)


main()