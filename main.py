#!/usr/bin/env python

import game
import random
import copy
import math

EMPTY = "-"
HIT = "h"
DESTROY = "d"
SHIPS = (1, 2, 2, 3, 4, 5)


def main():
    num_attempts = 10
    total_steps = 0
    for _ in range(num_attempts):
        steps = 0
        g = game.Game()
        board = g.get_board()
        while board:
            # print_board(board)
            steps += 1
            if steps > 100:
                # print_board(board)
                g.replay()
                return
            has_moved = False
            # hits = get_all_hits(board)
            hit_clusters = get_clusters(board, c=HIT)
            hits = get_all_hits(board)
            ships_left = get_ships_left(board)
            # print(f"Ships left: {ships_left}")
            # if hit_clusters and (pos := targets_around_hits(board, hits)):

            if hits:
                pos = target_around_hits(board, hits)
                board = g.next_move(pos)
            else:
                board = g.next_move(random_target(board))
        total_steps += steps
    print(f"Game over! Average number of moves was {total_steps/num_attempts}")


def print_board(board):
    print("_" * len(board) * 2)
    for row in board:
        print("".join(row))
    print("_" * len(board) * 2)


def target_around_hits(board, hits):
    targets = get_adjecent_targets(board, hits)
    ships_left = get_ships_left(board)
    if 1 in ships_left:
        ships_left.remove(1)
    size = len(hits)
    if size == 1:
        return targets[0]
    ship_placements = set()
    for hit in hits:
        ship_placements = ship_placements.union(
            get_ships_over_pos(board, hit, ships_left)
        )
    ship_placements = tuple(ship_placements)
    validator = get_placement_validator(hits, ship_placements, ships_left)
    combinations = []
    for n in range(1, 5):
        combs = all_valid_combinations(len(ship_placements), n, validator)
        if combs:
            combinations.extend(combs)
    pos_count = {}
    for comb in combinations:
        for ship in [ship_placements[i] for i in comb]:
            for pos in ship:
                if pos not in hits:
                    pos_count[pos] = pos_count.get(pos, 0) + 1
    if not pos_count.keys():
        print_board(board)
        print(ship_placements)
    most_common_pos = max(pos_count.keys(), key=lambda k: pos_count[k])
    return most_common_pos


def print_simulated_placements(board, ships):
    board_copy = copy.deepcopy(board)
    for ship in ships:
        char = str(len(ship))
        for x, y in ship:
            board_copy[x][y] = char
    print_board(board_copy)


def all_valid_combinations(length, n, validator=None):
    combs = []
    if not validator:
        validator = lambda a: True
    # for n in range(1, max_num + 1):
    current_comb = [0] * n
    all_valid_combinations_util(length, n, validator, combs, current_comb, 0)
    return combs


def all_valid_combinations_util(length, n, validator, combs, current_comb, index):
    if not n:
        if validator(current_comb):
            combs.append(list(current_comb))
        return

    prev = -1 if not index else current_comb[index - 1]

    for i in range(prev + 1, length):
        current_comb[index] = i
        all_valid_combinations_util(
            length, n - 1, validator, combs, current_comb, index + 1
        )


def get_placement_validator(hit_cluster, placements, ships_left):
    def validator(combination):
        positions = set()
        ships_left_copy = list(ships_left)
        for i in combination:
            if (length := len(placements[i])) not in ships_left_copy:
                return False
            ships_left_copy.remove(length)
            for pos in placements[i]:
                if pos in positions:
                    return False
                positions.add(pos)
        for hit in hit_cluster:
            if hit not in positions:
                return False
        return True

    return validator


def get_ships_over_pos(board, pos, ships_left):
    """Finds all potential ship placements overlapping given position"""
    x1, y1 = pos
    all_placements = []
    start = next(
        (
            x + 1
            for x in range(x1, 0, -1)
            if board[x][y1] != HIT and board[x][y1] != EMPTY
        ),
        0,
    )
    end = next(
        (
            x - 1
            for x in range(x1, len(board))
            if board[x][y1] != HIT and board[x][y1] != EMPTY
        ),
        len(board) - 1,
    )
    row = [(x, y1) for x in range(start, end + 1)]
    start = next(
        (
            y + 1
            for y in range(y1, 0, -1)
            if board[x1][y] != HIT and board[x1][y] != EMPTY
        ),
        0,
    )
    end = next(
        (
            y - 1
            for y in range(y1, len(board))
            if board[x1][y] != HIT and board[x1][y] != EMPTY
        ),
        len(board) - 1,
    )
    col = [(x1, y) for y in range(start, end + 1)]
    for size in set(ships_left):
        all_placements.extend(all_snippets_of_length(row, size))
        all_placements.extend(all_snippets_of_length(col, size))
    if not all_placements:
        return None
    ships = set()
    for ship in all_placements:
        if pos not in ship:
            continue
        values = [board[x][y] for x, y in ship]
        if EMPTY not in values:
            continue
        ships.add(tuple(ship))
    return ships


def all_snippets_of_length(a_list, length):
    snippets = []
    for start in range(len(a_list) - length + 1):
        snippets.append(a_list[start : start + length])
    return snippets


def get_adjecent_targets(board, cluster):
    targets = [
        (x, y)
        for x in range(len(board))
        for y in range(len(board[x]))
        if board[x][y] == EMPTY
    ]
    adj_targets = []
    for x1, y1 in targets:
        for x2, y2 in cluster:
            if abs(x1 - x2) + abs(y1 - y2) == 1 and (x1, y1) not in adj_targets:
                adj_targets.append((x1, y1))
    return adj_targets


def get_ships_left(board):
    """Analyses current board state to determine which ships are left"""
    clusters = get_clusters(board, c="d")
    clusters = [len(c) for c in clusters]
    clusters.sort()
    ships_left = list(SHIPS)
    for cluster in clusters:
        combinations = get_combinations(cluster, ships_left)
        if len(combinations) == 1 or cluster == 2:
            ships_remove = [ships_left[i] for i in combinations[0]]
            for ship in ships_remove:
                ships_left.remove(ship)

    return ships_left


def get_combinations_util(cluster, index, current_comb, combs, ships):
    if cluster < 0:
        return combs

    if not cluster:
        combs.append(current_comb[:index])

    prev = -1 if not index else current_comb[index - 1]

    for k in range(prev + 1, len(ships)):
        current_comb[index] = k
        get_combinations_util(cluster - ships[k], index + 1, current_comb, combs, ships)


def get_combinations(cluster, ships):
    combs = []
    current_comb = [0] * len(SHIPS)
    get_combinations_util(cluster, 0, current_comb, combs, ships)
    return combs


def get_clusters(board, c="d"):
    pos_dict = {}
    clusters = []
    unassigned = [
        (x, y)
        for x in range(len(board))
        for y in range(len(board[x]))
        if board[x][y] == c
    ]
    # for pos in unassigned:
    while unassigned:
        x0, y0 = unassigned.pop()
        new_cluster = [(x0, y0)]
        for x, y in new_cluster:
            for x2, y2 in reversed(unassigned):
                if abs(x2 - x) + abs(y2 - y) == 1:
                    new_cluster.append((x2, y2))
                    unassigned.remove((x2, y2))
        clusters.append(new_cluster)
    return clusters


def random_cell(board):
    x, y = random.randint(0, 9), random.randint(0, 9)
    return (x, y)


def random_target(board):
    x, y = random_cell(board)
    while not is_target(board, x, y):
        x, y = random_cell(board)
    return (x, y)


def get_hits(board):
    for x in range(len(board)):
        for y in range(len(board[x])):
            if board[x][y] == HIT:
                yield (x, y)


def get_all_hits(board):
    hits = []
    for x in range(len(board)):
        for y in range(len(board[x])):
            if board[x][y] == HIT:
                hits.append((x, y))
    return hits


def targets_around_hits(board, hits):
    # if len(hits) == 1:
    #     x, y = hits[0]
    #     return cell_around_point(board, x, y)
    # if len([h for h in hits if h[0] == hits[0][0]] == len(hits)):
    y_min = min([h[1] for h in hits])
    y_max = max([h[1] for h in hits])
    x_min = min([h[0] for h in hits])
    x_max = max([h[0] for h in hits])
    if y_min == y_max:
        y = y_min
        if is_target(board, x_min - 1, y):
            return (x_min - 1, y)
        if is_target(board, x_max + 1, y):
            return (x_max + 1, y)
    if x_min == x_max:
        x = x_min
        if is_target(board, x, y_min - 1):
            return (x, y_min - 1)
        if is_target(board, x, y_max + 1):
            return (x, y_max + 1)

    return None


def target_around_cell(board, x, y):
    if is_target(board, x + 1, y):
        return (x + 1, y)
    if is_target(board, x, y + 1):
        return (x, y + 1)
    if is_target(board, x - 1, y):
        return (x - 1, y)
    if is_target(board, x, y - 1):
        return (x, y - 1)
    return None


def is_target(board, x, y):
    if not (0 <= x < 10 and 0 <= y < 10):
        return False
    if board[x][y] != EMPTY:
        return False
    return True


if __name__ == "__main__":
    main()
