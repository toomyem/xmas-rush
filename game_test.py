
import unittest
import io
import game


class Tests(unittest.TestCase):
    def test1(self):
        data = """
        0000 0000 0001
        0001 0001 0001
        1000 1000 1000
        """
        b = game.Board(3, src=io.StringIO(data))
        self.assertEqual(str(b), """
        0000|0000|0001
        0001|0001|0001
        1000|1000|1000
        Items:""".replace(" ", ""))


if __name__ == '__main__':
    unittest.main()
