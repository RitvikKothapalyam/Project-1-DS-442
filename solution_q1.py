# solution_q1.py
# Question 1: DFS and BFS for the River Crossing Puzzle
# Run with: python solution_q1.py
#
# Cost here is just the number of actions, since every move counts the same.
# Both searches are graph searches, so a state never gets expanded twice.
# I count an expansion every time I pop a node and generate its children.
# The goal node doesn't count, because the search stops before expanding it.

from collections import deque

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
    # Returns a list of new states we can reach from this one.
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
            successors.append(new_state)

    return successors


def is_goal(state):
    # Everyone made it to the right bank.
    return state[0] == 0 and state[1] == 0


def dfs(start):
    # DFS uses a stack, so we always work on the most recent node first.
    stack = [(start, [start])]
    visited = set()
    expansions = 0

    while len(stack) > 0:
        state, path = stack.pop()

        if state in visited:
            continue
        visited.add(state)

        if is_goal(state):
            return path, len(path) - 1, expansions

        expansions = expansions + 1

        # Reversed so the first successor ends up on top of the stack
        # and gets popped first.
        successors = get_successors(state)
        successors.reverse()
        for new_state in successors:
            if new_state not in visited:
                stack.append((new_state, path + [new_state]))

    return None, 0, expansions


def bfs(start):
    # BFS uses a queue, so we finish every node at one depth before
    # moving down to the next one.
    queue = deque()
    queue.append((start, [start]))
    seen = set()
    seen.add(start)
    expansions = 0

    while len(queue) > 0:
        state, path = queue.popleft()

        if is_goal(state):
            return path, len(path) - 1, expansions

        expansions = expansions + 1

        for new_state in get_successors(state):
            if new_state not in seen:
                seen.add(new_state)
                queue.append((new_state, path + [new_state]))

    return None, 0, expansions


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

    path, cost, expansions = dfs(start)
    print_answer("Q1.1.a (DFS)", path, cost, expansions)
    print()

    path, cost, expansions = bfs(start)
    print_answer("Q1.1.b (BFS)", path, cost, expansions)


main()