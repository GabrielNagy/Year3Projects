import unittest
import unittest.mock


class MyClass:
    def set_string(self):
        self.string = str(input("Enter string: "))

    def to_uppercase(self):
        return self.string.upper()


class Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_capitalization(self):
        with unittest.mock.patch('builtins.input', return_value='capitalize this'):
            line = "CAPITALIZE THIS"
            mock = MyClass()
            mock.set_string()
            self.assertEqual(mock.to_uppercase(), line)


if __name__ == "__main__":
    unittest.main()
