import unittest
from unittest.mock import patch

from parser import parse_input


class ParserFastPathTests(unittest.TestCase):
    def test_simple_instruction_uses_rule_based_parser_without_ai(self):
        with patch("parser.groq_client.is_available", return_value=True), patch(
            "parser.parse_with_ai", side_effect=AssertionError("AI parser should not be used for simple instructions")
        ):
            steps = parse_input("Open youtube and search for python tutorial")

        self.assertTrue(steps, "Expected parser to return steps")
        self.assertEqual(steps[0]["action"], "open")
        self.assertEqual(steps[-1]["action"], "screenshot")


if __name__ == "__main__":
    unittest.main()
