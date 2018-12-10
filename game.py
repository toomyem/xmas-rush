
import sys
import math
import io
import random

# Help the Christmas elves fetch presents in a magical labyrinth!

PUSH = 0
MOVE = 1

TILES = {
    "0000": ' ',
    "0001": '╴',
    "0010": '╵',
    "0011": '┐',
    "0100": '╶',
    "0101": '─',
    "0110": '┌',
    "0111": '┬',
    "1000": '╷',
    "1001": '┘',
    "1010": '│',
    "1011": '┤',
    "1100": '└',
    "1101": '┴',
    "1110": '├',
    "1111": '┼'
}


def log(msg):
    print(msg, file=sys.stderr, flush=True)


class Direction:
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy
        self.names = {
            (0, -1): "UP",
            (1, 0): "RIGHT",
            (0, 1): "DOWN",
            (-1, 0): "LEFT"
        }

    def __repr__(self):
        return self.names[(self.dx, self.dy)]

    def __eq__(self, other):
        return self.dx == other.dx and self.dy == other.dy

    def opposite(self):
        return Direction(-self.dx, -self.dy)


UP = Direction(0, -1)
RIGHT = Direction(1, 0)
DOWN = Direction(0, 1)
LEFT = Direction(-1, 0)

DIRS = [UP, RIGHT, DOWN, LEFT]


class Parser:
    def __init__(self, data):
        if type(data) == str:
            data = io.StringIO(data)
        self.file = data

    def is_ws(self, ch):
        return ch in [' ', '\t', '\r', '\n']

    def skip_ws(self):
        ch = self.file.read(1)
        while ch != '' and self.is_ws(ch):
            ch = self.file.read(1)
        return ch

    def next_word(self):
        w = self.skip_ws()
        while w != '':
            ch = self.file.read(1)
            if ch == '' or self.is_ws(ch):
                break
            w = w + ch
        return w

    def next_int(self):
        return int(self.next_word())

    def parse_player_info(self):
        num_cards = self.next_int()
        pos_x = self.next_int()
        pos_y = self.next_int()
        pattern = self.next_word()
        return PlayerInfo(num_cards, Position(pos_x, pos_y), Tile(pattern))

    def parse_items(self):
        num_items = self.next_int()
        items = []
        for _ in range(num_items):
            name = self.next_word()
            pos_x = self.next_int()
            pos_y = self.next_int()
            plr_id = self.next_int()
            items.append(Item(name, Position(pos_x, pos_y), plr_id))
        return items

    def parse_quests(self):
        num_quests = self.next_int()
        quests = []
        for _ in range(num_quests):
            name = self.next_word()
            plr_id = self.next_int()
            quests.append(Quest(name, plr_id))
        return quests

    def parse_board(self, size=7):
        cells = {}
        for y in range(size):
            for x in range(size):
                cells[(x, y)] = Tile(self.next_word())

        plr_info = self.parse_player_info()
        op_info = self.parse_player_info()
        items = self.parse_items()
        quests = self.parse_quests()
        return Board(size, cells, plr_info, op_info, items, quests)


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, dir):
        return Position(self.x + dir.dx, self.y + dir.dy)

    def __eq__(self, other):
        return isinstance(other, Position) and self.x == other.x and self.y == other.y

    def __repr__(self):
        return "P[%d,%d]" % (self.x, self.y)

    def dist(self, dest):
        return abs(self.x - dest.x) + abs(self.y - dest.y)

    def copy(self):
        return Position(self.x, self.y)


class Item:
    def __init__(self, name, pos, plr_id):
        self.name = name
        self.pos = pos
        self.player_id = plr_id

    def __repr__(self):
        return "Item(%s,%s,%d)" % (self.name, self.pos, self.player_id)


class Board:
    def __init__(self, size, cells, plr_info, op_info, items=[], quests=[]):
        self.size = size
        self.cells = cells
        self.player_info = plr_info
        self.opponent_info = op_info
        self.items = items
        self.quests = quests

    def __repr__(self):
        s = ""
        for y in range(self.size):
            s += " ".join([str(self.cells[(x, y)])
                           for x in range(self.size)]) + "\n"
        return s

    def valid_pos(self, pos):
        return pos.x >= 0 and pos.x < self.size and pos.y >= 0 and pos.y < self.size

    def get_tile(self, pos):
        return self.cells[(pos.x, pos.y)]

    def can_go(self, pos, dir):
        if self.valid_pos(pos + dir):
            if self.get_tile(pos).can_go(dir) and self.get_tile(pos + dir).can_go(dir.opposite()) and \
                    not self.get_tile(pos + dir).visited:
                return True
        return False

    def nearest_paths(self, pos, dest):
        self.found_paths = []
        self.best_dist = pos.dist(dest)
        # log("Walk from pos: %s, dist: %d" % (pos, self.best_dist))

        def walk(pos, path=[]):
            self.get_tile(pos).visited = True
            dist = pos.dist(dest)
            if dist == self.best_dist:
                self.found_paths.append(path)
            elif dist < self.best_dist:
                self.found_paths = [path]
                self.best_dist = dist

            for dir in DIRS:
                if self.can_go(pos, dir) and len(path) < 20:
                    walk(pos + dir, path + [dir])
            self.get_tile(pos).visited = False

        walk(pos)
        return self.found_paths

    def push(self, offset, dir):
        cells = self.cells.copy()
        plr_info = self.player_info.copy()
        for i in range(1, self.size):
            if dir == RIGHT:
                if i == 1:
                    tile = cells[(self.size-i, offset)]
                cells[(self.size-i, offset)] = cells[(self.size-i-1, offset)]
                if i == self.size-1:
                    cells[(self.size-i-1, offset)] = plr_info.tile
                    plr_info.tile = tile
        return Board(self.size, cells, plr_info, self.opponent_info, self.items, self.quests)


class Tile:
    def __init__(self, pattern):
        self.pattern = pattern
        self.visited = False

    def __eq__(self, other):
        return isinstance(other, Tile) and self.pattern == other.pattern

    def __repr__(self):
        # return TILES.get(self.pattern, "?")
        return self.pattern

    def can_go(self, dir):
        if dir == UP and self.pattern[0] == "1":
            return True
        if dir == RIGHT and self.pattern[1] == "1":
            return True
        if dir == DOWN and self.pattern[2] == "1":
            return True
        if dir == LEFT and self.pattern[3] == "1":
            return True
        return False

    def copy(self):
        return Tile(self.pattern)


class PlayerInfo:
    def __init__(self, num_cards, pos, tile):
        # num_player_cards: the total number of quests for a player (hidden and revealed)
        self.num_cards = num_cards
        self.pos = pos
        self.tile = tile

    def __repr__(self):
        return "PlayerInfo(%d,%s,%s)" % (self.num_cards, self.pos, self.tile)

    def copy(self):
        return PlayerInfo(self.num_cards, self.pos.copy(), self.tile.copy())


class Quest:
    def __init__(self, name, plr_id):
        self.item_name = name
        self.player_id = plr_id

    def __repr__(self):
        return "Quest[%s,%d]" % (self.item_name, self.player_id)


def game_loop(parser):
    while True:
        turn_type = parser.next_int()
        log("Turn type: %d" % turn_type)
        board = parser.parse_board()

        # PUSH <id> <direction> | MOVE <direction> | PASS
        if turn_type == PUSH:
            dir = random.choice(DIRS)
            n = random.randint(0, 6)
            print("PUSH %d %s" % (n, dir), flush=True)
        elif turn_type == MOVE:
            paths = board.nearest_paths(
                board.player_info.pos, board.items[0].pos)
            path = paths[0]
            if len(path) == 0:
                print("PASS", flush=True)
            else:
                print("MOVE %s" % " ".join([str(d) for d in path]), flush=True)
        else:
            print("???", flush=True)


if __name__ == "__main__":
    game_loop(Parser(sys.stdin))
