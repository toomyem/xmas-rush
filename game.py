
import sys
import math

# Help the Christmas elves fetch presents in a magical labyrinth!

PUSH = 0
MOVE = 1


def log(msg):
    print(msg, file=sys.stderr)


class Item:
    def __init__(self):
        name, x, y, player_id = input().split()
        self.name = name
        self.x = int(x)
        self.y = int(y)
        self.player_id = int(player_id)

    def __str__(self):
        return "Item(%s,%d,%d,%d)" % (self.name, self.x, self.y, self.player_id)


class Board:
    def __init__(self, size=7, src=sys.stdin):
        self.cells = []
        self.items = []
        for _ in range(size+1):
            self.cells.append(src.readline().split())

    def __str__(self):
        return "\n".join(["|".join(r) for r in self.cells]) + "\nItems:" + ",".join([str(i) for i in self.items])

    def read_items(self):
        # the total number of items available on board and on player tiles
        num_items = int(input())
        self.items = [Item() for _ in range(num_items)]

    def reachable_cells(self):
        return []


class Tile:
    def __init__(self, pattern):
        self.pattern = pattern

    def __str__(self):
        return "[%s]" % self.pattern


class PlayerInfo:
    def __init__(self):
        # num_player_cards: the total number of quests for a player (hidden and revealed)
        info = input().split()
        self.num_player_cards = int(info[0])
        self.player_x = int(info[1])
        self.player_y = int(info[2])
        self.tile = Tile(info[3])

    def __str__(self):
        return "PlayerInfo(%d,%d,%d,%s)" % (self.num_player_cards, self.player_x, self.player_y, self.tile)


class Quest:
    def __init__(self):
        item_name, player_id = input().split()
        self.item_name = item_name
        self.player_id = int(player_id)


def game_loop():
    while True:
        turn_type = int(input())
        board = Board()
        player_info = PlayerInfo()
        opponent_info = PlayerInfo()
        board.read_items()
        num_quests = int(input())
        quests = [Quest() for _ in range(num_quests)]

        # PUSH <id> <direction> | MOVE <direction> | PASS
        if turn_type == PUSH:
            print("PUSH 3 RIGHT")
        else:
            print("PASS")


if __name__ == "__main__":
    game_loop()
