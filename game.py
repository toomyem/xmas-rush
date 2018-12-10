
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


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, dir):
        return Position(self.x + dir.dx, self.y + dir.dy)

    def __repr__(self):
        return "P[%d,%d]" % (self.x, self.y)

    def dist(self, dest):
        return abs(self.x - dest.x) + abs(self.y - dest.y)


class Item:
    def __init__(self, parser):
        self.name = parser.next_word()
        self.pos = Position(parser.next_int(), parser.next_int())
        self.player_id = parser.next_int()

    def __repr__(self):
        return "Item(%s,%s,%d)" % (self.name, self.pos, self.player_id)


class Board:
    def __init__(self, size, parser):
        self.size = size
        self.cells = {}
        for y in range(size):
            for x in range(size):
                self.cells[(x, y)] = Tile(parser.next_word())

    def __repr__(self):
        return "".join([" ".join([str(tile) for tile in row])+"\n" for row in self.cells])

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

    def get_possible_dirs(self, pos):
        r = []
        for dir in DIRS:
            if self.can_go(pos, dir):
                r.append(dir)
        return r

    def nearest_paths(self, pos, dest):
        self.found_paths = []
        self.best_dist = pos.dist(dest)
        #log("Walk from pos: %s, dist: %d" % (pos, self.best_dist))

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

    def push(self, offset, dir, new_tile):
        return self


class Tile:
    def __init__(self, pattern):
        self.pattern = pattern
        self.visited = False

    def __eq__(self, other):
        return self.pattern == other.pattern

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


class PlayerInfo:
    def __init__(self, parser):
        # num_player_cards: the total number of quests for a player (hidden and revealed)
        self.num_player_cards = parser.next_int()
        self.pos = Position(parser.next_int(), parser.next_int())
        self.tile = Tile(parser.next_word())

    def __repr__(self):
        return "PlayerInfo(%d,%s,%s)" % (self.num_player_cards, self.pos, self.tile)


class Quest:
    def __init__(self, parser):
        self.item_name = parser.next_word()
        self.player_id = parser.next_int()

    def __repr__(self):
        return "Quest[%s,%d]" % (self.item_name, self.player_id)


def game_loop(parser):
    while True:
        turn_type = parser.next_int()
        log("Turn type: %d" % turn_type)
        board = Board(7, parser)
        player_info = PlayerInfo(parser)
        opponent_info = PlayerInfo(parser)
        num_items = parser.next_int()
        items = [Item(parser) for _ in range(num_items)]
        num_quests = parser.next_int()
        quests = [Quest(parser) for _ in range(num_quests)]

        # PUSH <id> <direction> | MOVE <direction> | PASS
        if turn_type == PUSH:
            dir = random.choice(DIRS)
            n = random.randint(0, 6)
            print("PUSH %d %s" % (n, dir), flush=True)
        elif turn_type == MOVE:
            paths = board.nearest_paths(player_info.pos, items[0].pos)
            path = paths[0]
            if len(path) == 0:
                print("PASS", flush=True)
            else:
                print("MOVE %s" % " ".join([str(d) for d in path]), flush=True)
        else:
            print("???", flush=True)


if __name__ == "__main__":
    game_loop(Parser(sys.stdin))
