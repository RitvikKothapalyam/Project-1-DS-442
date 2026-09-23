"""
solution_q3.py  --  Question 3: A* search with admissible heuristics

Run with:  python solution_q3.py

Uses Cost Model A throughout:  cost = 2 per missionary aboard + 1 per cannibal.

HEURISTICS
  h1  Passenger Weight Remaining
          h1(s) = 2 * M_left + 1 * C_left

  h2  Trip-Packing Lower Bound
          h2(s) = ceil( (2 * M_left + 1 * C_left) / 3 )

  h3  Weight-Plus-Return-Trips  (my own; Q3.2 Part C)
          Let W = 2 * M_left + C_left     (weight still to be ferried over)
              P = M_left + C_left         (people still on the left bank)
              B = return trips still required:
                      max(0, ceil(P/2) - 1)  if the boat is on the left
                      ceil(P/2)              if the boat is on the right
          h3(s) = 0            if P == 0
          h3(s) = W + 2 * B    otherwise

      Idea: h1 only charges for carrying the left-bank people across once,
      but the boat cannot come back by itself -- every return trip needs a
      rower, who costs at least 1 to bring back and at least 1 to ferry over
      again.  h3 adds that unavoidable shuttling cost, so h3 >= h1 >= h2.
"""

import heapq
import math

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
    m, c = action
    return 2 * m + 1 * c


def h1(state):
    """Passenger weight remaining on the left bank."""
    return 2 * state[0] + 1 * state[1]


def h2(state):
    """Trip-packing lower bound."""
    return math.ceil((2 * state[0] + 1 * state[1]) / 3)


def h3(state):
    """Weight remaining plus the cost of the return trips it forces."""
    m_l, c_l, _, _, boat = state
    weight = 2 * m_l + 1 * c_l
    people = m_l + c_l
    if people == 0:
        return 0
    if boat == 'L':
        returns = max(0, math.ceil(people / 2) - 1)
    else:
        returns = math.ceil(people / 2)
    return weight + 2 * returns


def a_star(start, heuristic, cost_fn=cost_model_a):
    """Returns (path, actions, total_cost, expansions)."""
    counter = 0
    frontier = [(heuristic(start), 0, counter, start, [start], [])]
    best_g = {start: 0}
    closed = set()
    expansions = 0

    while frontier:
        _, g, _, state, path, actions = heapq.heappop(frontier)

        if state in closed:
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
                    (new_g + heuristic(nxt), new_g, counter,
                     nxt, path + [nxt], actions + [action])
                )

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

    report("Q3.1 (Heuristic 1)", a_star(start, h1))
    print()
    report("Q3.1 (Heuristic 2)", a_star(start, h2))
    print()
    report("Q3.2 Part C (Heuristic 3)", a_star(start, h3))


if __name__ == "__main__":
    main()