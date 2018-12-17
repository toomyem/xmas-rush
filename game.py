
import sys
import math
import io
import random
import copy

# Help the Christmas elves fetch presents in a magical labyrinth!


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
        cells = []
        for _ in range(size):
            row = []
            for _ in range(size):
                row.append(Tile(self.next_word()))
            cells.append(row)

        plr_info = self.parse_player_info()
        op_info = self.parse_player_info()
        items = self.parse_items()
        quests = self.parse_quests()
        return Board(size, cells, plr_info, op_info, items, quests)


class Item:
    def __init__(self, name, pos, plr_id):
        self.name = name
        self.pos = pos
        self.player_id = plr_id

    def __repr__(self):
        return "(%s,%s,%d)" % (self.name, self.pos, self.player_id)


class Tile:
    def __init__(self, pattern):
        self.pattern = pattern
        self.visited = False

    def __eq__(self, other):
        return isinstance(other, Tile) and self.pattern == other.pattern

    def __repr__(self):
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
        return "{%s,%d}" % (self.item_name, self.player_id)


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
            s += " ".join(["%s" % self.cells[y][x]
                           for x in range(self.size)]) + "\n"
        s += str(self.player_info) + "\n" + \
            str(self.opponent_info) + "\n" + str(self.items) + "\n"
        return s

    def get_items(self):
        my_quests = [q for q in self.quests if q.player_id == 0]
        #log("my quests: %s" % str(my_quests))
        items = [i for i in self.items if i.name in [
            q.item_name for q in my_quests] and i.player_id == 0]
        return items

    def possible_moves(self):
        for n in [-1, 0, 1]:
            nx = self.player_info.pos.x + n
            if nx >= 0 and nx < self.size:
                yield((UP, nx))
                yield((DOWN, nx))
            ny = self.player_info.pos.y + n
            if ny >= 0 and ny < self.size:
                yield((LEFT, ny))
                yield((RIGHT, ny))

    def valid_pos(self, pos):
        return pos.x >= 0 and pos.x < self.size and pos.y >= 0 and pos.y < self.size

    def get_tile(self, pos):
        return self.cells[pos.y][pos.x]

    def can_go(self, pos, dir):
        if self.valid_pos(pos + dir):
            if self.get_tile(pos).can_go(dir) and self.get_tile(pos + dir).can_go(dir.opposite()) and \
                    not self.get_tile(pos + dir).visited:
                return True
        return False

    def nearest_paths(self, pos, dest):
        self.found_paths = []
        self.best_dist = min([pos.dist(d) for d in dest])
        valid = [d for d in dest if self.valid_pos(d)]

        def walk(pos, path=[]):
            self.get_tile(pos).visited = True
            dist = min([pos.dist(d) for d in valid])
            if dist == self.best_dist:
                self.found_paths.append(path)
            elif dist < self.best_dist:
                self.found_paths = [path]
                self.best_dist = dist

            for dir in DIRS:
                if self.can_go(pos, dir) and len(path) < 20:
                    walk(pos + dir, path + [dir])
            self.get_tile(pos).visited = False

        if len(valid) > 0:
            walk(pos)
            log("pos: %s, dest: %s, dist: %d" %
                (str(pos), str(valid), self.best_dist))
        else:
            self.found_paths.append([])
        return self.found_paths

    def push(self, offset, dir):
        cells = copy.deepcopy(self.cells)
        plr_info = self.player_info.copy()
        opp_info = self.opponent_info.copy()
        items = copy.deepcopy(self.items)
        N = self.size-1

        if dir == RIGHT:
            tile = cells[offset][N]
            for i in range(N, 0, -1):
                cells[offset][i] = cells[offset][i-1]
            cells[offset][0] = plr_info.tile
            plr_info.tile = tile
            if plr_info.pos.y == offset:
                plr_info.pos.x = (plr_info.pos.x + 1) % self.size
            if opp_info.pos.y == offset:
                opp_info.pos.x = (opp_info.pos.x + 1) % self.size
            for i in items:
                if i.pos.y == offset:
                    i.pos.x = (i.pos.x + 1) % self.size
                elif i.pos.x == -1:
                    i.pos = Position(0, offset)
        elif dir == DOWN:
            tile = cells[N][offset]
            for i in range(N, 0, -1):
                cells[i][offset] = cells[i-1][offset]
            cells[0][offset] = plr_info.tile
            plr_info.tile = tile
            if plr_info.pos.x == offset:
                plr_info.pos.y = (plr_info.pos.y + 1) % self.size
            if opp_info.pos.x == offset:
                opp_info.pos.y = (opp_info.pos.y + 1) % self.size
            for i in items:
                if i.pos.x == offset:
                    i.pos.y = (i.pos.y + 1) % self.size
                elif i.pos.x == -1:
                    i.pos = Position(offset, 0)
        elif dir == LEFT:
            tile = cells[offset][0]
            for i in range(0, N):
                cells[offset][i] = cells[offset][i+1]
            cells[offset][N] = plr_info.tile
            plr_info.tile = tile
            if plr_info.pos.y == offset:
                plr_info.pos.x = (plr_info.pos.x + N) % self.size
            if opp_info.pos.y == offset:
                opp_info.pos.x = (opp_info.pos.x + N) % self.size
            for i in items:
                if i.pos.y == offset:
                    i.pos.x = (i.pos.x + N) % self.size
                elif i.pos.x == -1:
                    i.pos = Position(N, offset)
        elif dir == UP:
            tile = cells[0][offset]
            for i in range(0, N):
                cells[i][offset] = cells[i+1][offset]
            cells[N][offset] = plr_info.tile
            plr_info.tile = tile
            if plr_info.pos.x == offset:
                plr_info.pos.y = (plr_info.pos.y + N) % self.size
            if opp_info.pos.x == offset:
                opp_info.pos.y = (opp_info.pos.y + N) % self.size
            for i in items:
                if i.pos.x == offset:
                    i.pos.y = (i.pos.y + N) % self.size
                elif i.pos.x == -1:
                    i.pos = Position(offset, N)

        return Board(self.size, cells, plr_info, opp_info, items, self.quests)


def game_loop(parser):
    last_move = ()
    stale = 0

    while True:
        turn_type = parser.next_int()
        log("Turn type: %d" % turn_type)
        board = parser.parse_board()
        log("Items: %s" % board.get_items())
        #log("Quests: %s" % board.quests)

        # PUSH <id> <direction> | MOVE <direction> | PASS
        if turn_type == 0:
            best_dist = 1e6
            best_moves = []

            for move in board.possible_moves():
                log(move)
                d, n = move
                b2 = board.push(n, d)
                items = b2.get_items()
                log("items: %s" % str(items))
                paths = b2.nearest_paths(b2.player_info.pos, [
                                         i.pos for i in items])
                if b2.best_dist < best_dist:
                    best_dist = b2.best_dist
                    best_moves = [move]
                    log("new best dist: %d" % best_dist)
                elif b2.best_dist == best_dist:
                    best_moves.append(move)
                if best_dist == 0:
                    break
            log("best_dist: %d\nmoves: %s" % (best_dist, str(best_moves)))
            dir, n = random.choice(best_moves)
            if last_move == (dir, n):
                stale += 1
                if stale > 3:
                    log("STALE!")
                    dir = random.choice(DIRS)
                    n = random.randint(0, 6)
                    stale = 0
                    last_move = (dir, n)
            else:
                stale = 0
                last_move = (dir, n)
            print("PUSH %d %s" % (n, dir), flush=True)
        else:
            best_dist = 1e6
            best_paths = []
            items = board.get_items()
            paths = board.nearest_paths(
                board.player_info.pos, [i.pos for i in items])
            if board.best_dist < best_dist:
                best_dist = board.best_dist
                best_paths = paths
                log("new best dist: %d\npaths: %s" %
                    (best_dist, best_paths))
            elif board.best_dist == best_dist:
                best_paths.extend(paths)
            log("paths: %s" % str(best_paths))
            path = random.choice(best_paths)
            if len(path) == 0:
                print("PASS", flush=True)
            else:
                print("MOVE %s" % " ".join([str(d) for d in path]), flush=True)


if __name__ == "__main__":
    game_loop(Parser(sys.stdin))
