
import unittest
import game


class TestParser(unittest.TestCase):
    def test_word(self):
        p = game.Parser("\nhave 2 \nnames")
        self.assertEqual(p.next_word(), "have")
        self.assertEqual(p.next_int(), 2)
        self.assertEqual(p.next_word(), "names")


class TestDirection(unittest.TestCase):
    def test_oposite(self):
        d = game.Direction(1, 0)
        self.assertEqual(repr(d), "RIGHT")
        self.assertEqual(d, game.RIGHT)
        self.assertEqual(d.opposite(), game.LEFT)


class TestBoard(unittest.TestCase):
    def setUp(self):
        parser = game.Parser("""
        0110 1011 0111
        1110 1100 1001
        1101 0011 0000
        1 0 0 0001
        1 2 1 0010
        1 A 0 1 0
        0""")
        self.board = parser.parse_board(3)

    def test_get_tile(self):
        b = self.board
        self.assertEqual(b.get_tile(game.Position(0, 0)), game.Tile("0110"))
        self.assertEqual(b.get_tile(game.Position(2, 2)), game.Tile("0000"))

    def test_paths(self):
        b = self.board
        paths = b.nearest_paths(game.Position(0, 0), game.Position(2, 2))
        self.assertListEqual(paths, [[game.RIGHT, game.DOWN, game.RIGHT], [
                             game.DOWN, game.DOWN, game.RIGHT]])

    def test_push_right(self):
        b = self.board
        b2 = b.push(1, game.RIGHT)
        self.assertEqual(
            repr(b2), "0110 1011 0111\n0001 1110 1100\n1101 0011 0000\nPlayerInfo(1,P[0,0],1001)\nPlayerInfo(1,P[0,1],0010)\n[Item(A,P[1,1],0)]\n")

    def test_push_down(self):
        b = self.board
        b2 = b.push(2, game.DOWN)
        self.assertEqual(
            repr(b2), "0110 1011 0001\n1110 1100 0111\n1101 0011 1001\nPlayerInfo(1,P[0,0],0000)\nPlayerInfo(1,P[2,2],0010)\n[Item(A,P[0,1],0)]\n")

    def test_push_left(self):
        b = self.board
        b2 = b.push(0, game.LEFT)
        self.assertEqual(
            repr(b2), "1011 0111 0001\n1110 1100 1001\n1101 0011 0000\nPlayerInfo(1,P[2,0],0110)\nPlayerInfo(1,P[2,1],0010)\n[Item(A,P[0,1],0)]\n")

    def test_push_up(self):
        b = self.board
        b2 = b.push(0, game.UP)
        self.assertEqual(
            repr(b2), "1110 1011 0111\n1101 1100 1001\n0001 0011 0000\nPlayerInfo(1,P[0,2],0110)\nPlayerInfo(1,P[2,1],0010)\n[Item(A,P[0,0],0)]\n")


class TestPosition(unittest.TestCase):
    def test_add(self):
        p = game.Position(2, 5) + game.RIGHT + game.UP
        self.assertEqual((p.x, p.y), (3, 4))

    def test_dist(self):
        p = game.Position(1, 2)
        self.assertEqual(p.dist(p), 0)
        self.assertEqual(p.dist(game.Position(2, 0)), 3)


class TestTiles(unittest.TestCase):
    def test_can_go(self):
        t = game.Tile("1010")
        self.assertTrue(t.can_go(game.UP))
        self.assertFalse(t.can_go(game.RIGHT))


if __name__ == '__main__':
    unittest.main()
