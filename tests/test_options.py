import unittest

from main import parse_options


class ParseOptionsTests(unittest.TestCase):
    def test_empty_json_defaults_to_empty_dict(self):
        self.assertEqual(parse_options("{}"), {})
        self.assertEqual(parse_options(""), {})

    def test_valid_json_is_parsed(self):
        self.assertEqual(parse_options('{"temperature": 0.5, "top_p": 0.9}'), {
            "temperature": 0.5,
            "top_p": 0.9,
        })

    def test_invalid_json_raises_value_error(self):
        with self.assertRaises(ValueError):
            parse_options('{not valid json}')


if __name__ == "__main__":
    unittest.main()
