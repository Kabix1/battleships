#!/usr/bin/env python

import random


class Game:
    def __init__(self):
        SHIPS = (1, 2, 2, 3, 4, 5)
        self.size = 10
        self.board = [["-"] * self.size for _ in range(self.size)]
        self.ships = {}
        self.place_ships(SHIPS)

    def place_ships(self, ships):
        for num, ship in enumerate(ships):
            valid = False
            while not valid:
                x, y = random.randint(0, 9), random.randint(0, 9)
                ori = random.randint(0, 1)
                valid = self.is_valid_placement(ship, x, y, ori)
            self.ships[num] = {}
            for i in range(ship):
                self.board[x][y] = str(num)
                self.ships[num][(x, y)] = True
                x, y = (x + 1, y) if ori else (x, y + 1)

    def is_valid_placement(self, ship, x, y, ori):
        if ori and x + ship > self.size:
            return False
        if not ori and y + ship > self.size:
            return False
        for _ in range(ship):
            if self.board[x][y] != "-":
                return False
            x, y = (x + 1, y) if ori else (x, y + 1)
        return True

    def print_board(self):
        print("_" * self.size * 2)
        for row in self.board:
            print("".join(row))
        print("_" * self.size * 2)

    def get_board(self):
        public_board = []
        for row in self.board:
            public_row = []
            for c in row:
                if c.isnumeric():
                    public_row.append("-")
                else:
                    public_row.append(c)
            public_board.append(public_row)
        return public_board

    def next_move(self, pos):
        x, y = pos
        self.shoot(x, y)
        if self.ships:
            return self.get_board()
        else:
            return None

    def shoot(self, x, y):
        if self.board[x][y] == "-":
            self.board[x][y] = "m"
        elif self.board[x][y].isnumeric():
            ship_num = int(self.board[x][y])
            ship = self.ships[ship_num]
            ship[(x, y)] = False
            destroyed = True
            for cell in ship.values():
                if cell:
                    destroyed = False
            if destroyed:
                for sx, sy in ship.keys():
                    self.board[sx][sy] = "d"
                self.ships.pop(ship_num)
            else:
                self.board[x][y] = "h"
