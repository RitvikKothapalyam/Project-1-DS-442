"""
solution_q2.py  --  Question 2: Uniform Cost Search with non-uniform action costs

Run with:  python solution_q2.py                 (runs both cost models)
           python solution_q2.py --cost-model A  (runs only model A)
           python solution_q2.py --cost-model B  (runs only model B)

The cost model may also be selected with a second line in input.txt:
    3, 3, 0, 0, L
    A
A command-line flag, if given, overrides the file.

COST MODELS
  A -- cost by passenger type:  2 units per missionary + 1 unit per cannibal
  B -- cost by boat direction:  left -> right = 2,  right -> left = 1
"""

import heapq
import sys

MOVES = [(0, 1), (0, 2), (1, 0), (1, 1), (2, 0)]


def is_valid(state):
    m_l, c_l, m_r, c_r, _ = state
    if min(m_l, c_l, m_r, c_r) < 0:
        return False
    if m_l > 0 and c_l > m_l:
        return False
    if m_r > 0 and c_r > m_r:
        return False
    return True


def successors(state):
    m_l, c_l, m_r, c_r, boat = state
    result = []
    for (m, c) in MOVES:
        if boat == 'L':
            if m > m_l or c > c_l:
                continue
            nxt = (m_l - m, c_l - c, m_r + m, c_r + c, 'R')
        else:
            if m > m_r or c > c_r:
                continue
            nxt = (m_l + m, c_l + c, m_r - m, c_r - c, 'L')
        if is_valid(nxt):
            result.append(((m, c), nxt))
    return result


def is_goal(state):
    return state[0] == 0 and state[1] == 0


def cost_model_a(action, state, next_state):
    """2 units per missionary aboard + 1 unit per cannibal aboard."""
    m, c = action
    return 2 * m + 1 * c


def cost_model_b(action, state, next_state):
    """Against the current (L -> R) costs 2; with the current (R -> L) costs 1."""
    return 2 if state[4] == 'L' else 1


COST_MODELS = {'A': cost_model_a, 'B': cost_model_b}


def uniform_cost_search(start, cost_fn):
    """Dijkstra over the state graph. Returns (path, actions, total_cost, expansions)."""
    counter = 0                                   # FIFO tie-breaker
    frontier = [(0, counter, start, [start], [])]
    best_g = {start: 0}
    closed = set()
    expansions = 0

    while frontier:
        g, _, state, path, actions = heapq.heappop(frontier)

        if state in closed:                       # stale queue entry
            continue
        closed.add(state)

        if is_goal(state):
            return path, actions, g, expansions

        expansions += 1
        for action, nxt in successors(state):
            new_g = g + cost_fn(action, state, nxt)
            if nxt not in best_g or new_g < best_g[nxt]:
                best_g[nxt] = new_g
                counter += 1
                heapq.heappush(
                    frontier,
                    (new_g, counter, nxt, path + [nxt], actions + [action])
                )

    return None, None, None, expansions


def read_input(filename="input.txt"):
    """Return (start_state, cost_model_from_file_or_None)."""
    lines = []
    with open(filename) as f:
        for raw in f:
            line = raw.strip()
            if line and not line.startswith("#"):
                lines.append(line)

    if not lines:
        raise ValueError("input.txt contained no state line")

    parts = [p.strip() for p in lines[0].split(",")]
    if len(parts) != 5:
        raise ValueError("Expected 5 comma-separated fields, got: " + lines[0])
    m_l, c_l, m_r, c_r = (int(parts[i]) for i in range(4))
    boat = parts[4].upper()
    if boat not in ("L", "R"):
        raise ValueError("Boat must be L or R, got: " + parts[4])

    model = None
    if len(lines) > 1:
        candidate = lines[1].upper()
        if candidate in COST_MODELS:
            model = candidate

    return (m_l, c_l, m_r, c_r, boat), model


def parse_flag(argv):
    for i, arg in enumerate(argv):
        if arg == "--cost-model" and i + 1 < len(argv):
            return argv[i + 1].upper()
        if arg.startswith("--cost-model="):
            return arg.split("=", 1)[1].upper()
    return None


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
    start, file_model = read_input("input.txt")
    flag_model = parse_flag(sys.argv[1:])

    chosen = flag_model or file_model            # flag wins over file
    if chosen is not None and chosen not in COST_MODELS:
        raise SystemExit("Unknown cost model: {} (expected A or B)".format(chosen))

    models = [chosen] if chosen else ['A', 'B']

    for i, name in enumerate(models):
        if i:
            print()
        result = uniform_cost_search(start, COST_MODELS[name])
        report("Q2.1 (UCS, cost model {})".format(name), result)


if __name__ == "__main__":
    main()