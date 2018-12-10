
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
        self.board = game.Board(3, game.Parser("""
        0110 1011 0111
        1110 1100 1001
        1101 0011 0000"""))

    def test_get_tile(self):
        b = self.board
        self.assertEqual(b.get_tile(game.Position(0, 0)), game.Tile("0110"))
        self.assertEqual(b.get_tile(game.Position(2, 2)), game.Tile("0000"))

    def test_possible_dirs(self):
        b = self.board
        self.assertEqual(b.get_possible_dirs(
            game.Position(0, 1)), [game.UP, game.DOWN])

    def test_paths(self):
        b = self.board
        paths = b.nearest_paths(game.Position(0, 0), game.Position(2, 2))
        self.assertListEqual(paths, [[game.RIGHT, game.DOWN, game.RIGHT], [
                             game.DOWN, game.DOWN, game.RIGHT]])

    def test_big(self):
        b = game.Board(7, game.Parser("""
        0110 0110 1010 1011 1001 0101 0111
        1101 0101 0011 1001 1010 0101 1011
        1101 1111 0111 0101 1101 0110 1100
        1011 0011 0011 1111 1100 1100 1110
        0011 1001 0111 0101 1101 1111 0111
        1110 0101 1010 0110 1100 0101 0111
        1101 0101 0110 1110 1010 1001 1001"""))
        paths = b.nearest_paths(game.Position(0, 0), game.Position(6, 1))
        # print(paths)

    def test_push(self):
        b = game.Board(3, game.Parser("1 2 3 4 5 6 7 8 9"))
        b2 = b.push(1, game.RIGHT, game.Tile("x"))
        #self.assertEqual(repr(b2), "1 2 3\nx 4 5\n7 8 9")


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
