"""
solution_q1.py  --  Question 1: DFS and BFS for the River Crossing Puzzle

Run with:  python solution_q1.py

CONVENTIONS (stated explicitly, because expansion counts depend on them)
  * Both searches are GRAPH searches: a state is never expanded twice.
  * A "node expansion" is counted each time a node is removed from the
    frontier and its successors are generated.  The goal node is NOT
    counted, because the search stops before expanding it.
  * The goal test is applied when a node is removed from the frontier.
  * Successors are generated in the fixed order
        (0,1), (0,2), (1,0), (1,1), (2,0)
    where (m, c) = m missionaries and c cannibals aboard the boat.
"""

from collections import deque

MOVES = [(0, 1), (0, 2), (1, 0), (1, 1), (2, 0)]


def is_valid(state):
    """Legal if no count is negative and, on either bank, cannibals do not
    outnumber missionaries when missionaries are present."""
    m_l, c_l, m_r, c_r, _ = state
    if min(m_l, c_l, m_r, c_r) < 0:
        return False
    if m_l > 0 and c_l > m_l:
        return False
    if m_r > 0 and c_r > m_r:
        return False
    return True


def successors(state):
    """Return [(action, next_state), ...] in the fixed MOVES order."""
    m_l, c_l, m_r, c_r, boat = state
    result = []
    for (m, c) in MOVES:
        if boat == 'L':                      # left -> right
            if m > m_l or c > c_l:
                continue
            nxt = (m_l - m, c_l - c, m_r + m, c_r + c, 'R')
        else:                                # right -> left
            if m > m_r or c > c_r:
                continue
            nxt = (m_l + m, c_l + c, m_r - m, c_r - c, 'L')
        if is_valid(nxt):
            result.append(((m, c), nxt))
    return result


def is_goal(state):
    return state[0] == 0 and state[1] == 0


def depth_first_search(start):
    """DFS with an explicit LIFO stack."""
    stack = [(start, [start], [])]
    visited = set()
    expansions = 0

    while stack:
        state, path, actions = stack.pop()
        if state in visited:
            continue
        visited.add(state)

        if is_goal(state):
            return path, actions, len(actions), expansions

        expansions += 1
        # Pushed in reverse so the first successor is popped first.
        for action, nxt in reversed(successors(state)):
            if nxt not in visited:
                stack.append((nxt, path + [nxt], actions + [action]))

    return None, None, None, expansions


def breadth_first_search(start):
    """BFS with a FIFO queue."""
    frontier = deque([(start, [start], [])])
    reached = {start}
    expansions = 0

    while frontier:
        state, path, actions = frontier.popleft()

        if is_goal(state):
            return path, actions, len(actions), expansions

        expansions += 1
        for action, nxt in successors(state):
            if nxt not in reached:
                reached.add(nxt)
                frontier.append((nxt, path + [nxt], actions + [action]))

    return None, None, None, expansions


def read_initial_state(filename="input.txt"):
    with open(filename) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 5:
                raise ValueError("Expected 5 comma-separated fields, got: " + line)
            m_l, c_l, m_r, c_r = (int(parts[i]) for i in range(4))
            boat = parts[4].upper()
            if boat not in ("L", "R"):
                raise ValueError("Boat must be L or R, got: " + parts[4])
            return (m_l, c_l, m_r, c_r, boat)
    raise ValueError("input.txt contained no state line")


def format_path(path):
    return " -> ".join("({},{},{},{},{})".format(*s) for s in path)


def report(label, result):
    path, actions, cost, expansions = result
    print("The solution of {} is:".format(label))
    if path is None:
        print("Solution Path: no solution found")
        print("Total cost = N/A")
    else:
        print("Solution Path: " + format_path(path))
        print("Total cost = {}".format(cost))
    print("Number of node expansions = {}".format(expansions))


def main():
    start = read_initial_state("input.txt")
    report("Q1.1.a (DFS)", depth_first_search(start))
    print()
    report("Q1.1.b (BFS)", breadth_first_search(start))


if __name__ == "__main__":
    main()