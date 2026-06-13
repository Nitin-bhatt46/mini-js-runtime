import io
import sys
import unittest
from mini_js.lexer import Lexer
from mini_js.parser import Parser
from mini_js.interpreter import Interpreter, RunTimeError

class TestStrings(unittest.TestCase):

    def run_code(self, source_code: str) -> any:
        """Helper to tokenize, parse, and interpret code."""
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        return interpreter.evaluate(ast)

    def run_and_capture(self, source_code: str) -> str:
        """Helper to run code and capture stdout prints."""
        old_stdout = sys.stdout
        captured = io.StringIO()
        sys.stdout = captured
        try:
            self.run_code(source_code)
            return captured.getvalue()
        finally:
            sys.stdout = old_stdout

    def test_string_concatenation(self):
        self.assertEqual(self.run_code('"hello" + "world";'), "helloworld")
        self.assertEqual(self.run_code('"hello" + 5;'), "hello5")
        self.assertEqual(self.run_code('"hello" + true;'), "hellotrue")
        self.assertEqual(self.run_code('"hello" + null;'), "hellonull")
        self.assertEqual(self.run_code('5 + "hello";'), "5hello")
        self.assertEqual(self.run_code('true + "hello";'), "truehello")
        self.assertEqual(self.run_code('null + "hello";'), "nullhello")

    def test_string_length(self):
        self.assertEqual(self.run_code('"hello".length;'), 5)
        self.assertEqual(self.run_code('"".length;'), 0)

    def test_string_indexing_and_coercion(self):
        self.assertEqual(self.run_code('"hello"[1];'), "e")
        # Test whole float index coercion on strings
        self.assertEqual(self.run_code('"hello"[1.0];'), "e")
        self.assertEqual(self.run_code('"hello"[10];'), None)

        # Test whole float index coercion on arrays
        self.assertEqual(self.run_code("[10, 20, 30][1.0];"), 20)
        self.assertEqual(self.run_code("let a = [10, 20]; a[1.0] = 99; a;"), [10, 99])

    def test_string_split(self):
        self.assertEqual(self.run_code('"a,b,c".split(",");'), ["a", "b", "c"])
        self.assertEqual(self.run_code('"abc".split("");'), ["a", "b", "c"])
        self.assertEqual(self.run_code('"abc".split();'), ["abc"])

    def test_array_join(self):
        self.assertEqual(self.run_code("[1, 2, 3].join('-');"), "1-2-3")
        self.assertEqual(self.run_code("[true, false, null].join(',');"), "true,false,")
        self.assertEqual(self.run_code("[1, [2, 3]].join('|');"), "1|2,3")
        # Default separator is ','
        self.assertEqual(self.run_code("[1, 2, 3].join();"), "1,2,3")

    def test_string_replace(self):
        # Only first occurrence replaced
        self.assertEqual(self.run_code('"hello".replace("l", "x");'), "hexlo")
        self.assertEqual(self.run_code('"hello".replace("z", "x");'), "hello")

    def test_string_substring(self):
        # Basic substring
        self.assertEqual(self.run_code('"hello".substring(1, 3);'), "el")
        # Swap start and end
        self.assertEqual(self.run_code('"hello".substring(3, 1);'), "el")
        # Default end is length
        self.assertEqual(self.run_code('"hello".substring(2);'), "llo")
        # Negative bounds treated as 0
        self.assertEqual(self.run_code('"hello".substring(-2, 3);'), "hel")
        self.assertEqual(self.run_code('"hello".substring(1, -5);'), "h")
        # Out of bounds treated as length
        self.assertEqual(self.run_code('"hello".substring(1, 100);'), "ello")
        # Swapping floats
        self.assertEqual(self.run_code('"hello".substring(1.2, 3.8);'), "el")

    def test_string_slice(self):
        # Basic slice
        self.assertEqual(self.run_code('"hello".slice(1, 3);'), "el")
        # Default end is length
        self.assertEqual(self.run_code('"hello".slice(2);'), "llo")
        # Negative start relative to end of string
        self.assertEqual(self.run_code('"hello".slice(-3);'), "llo")
        self.assertEqual(self.run_code('"hello".slice(1, -1);'), "ell")
        # If start >= end, returns empty string (no swapping like substring)
        self.assertEqual(self.run_code('"hello".slice(3, 1);'), "")

    def test_string_trim(self):
        self.assertEqual(self.run_code('"   hello   ".trim();'), "hello")
        self.assertEqual(self.run_code('"\\n\\t hello\\r".trim();'), "hello")

    def test_string_casing(self):
        self.assertEqual(self.run_code('"Hello".toUpperCase();'), "HELLO")
        self.assertEqual(self.run_code('"Hello".toLowerCase();'), "hello")

    def test_string_includes(self):
        self.assertEqual(self.run_code('"hello".includes("ell");'), True)
        self.assertEqual(self.run_code('"hello".includes("ell", 2);'), False)
        self.assertEqual(self.run_code('"hello".includes("world");'), False)

    def test_string_starts_with(self):
        self.assertEqual(self.run_code('"hello".startsWith("he");'), True)
        self.assertEqual(self.run_code('"hello".startsWith("ll", 2);'), True)
        self.assertEqual(self.run_code('"hello".startsWith("he", 1);'), False)

    def test_string_ends_with(self):
        self.assertEqual(self.run_code('"hello".endsWith("lo");'), True)
        self.assertEqual(self.run_code('"hello".endsWith("he", 2);'), True)
        self.assertEqual(self.run_code('"hello".endsWith("lo", 3);'), False)

    def test_string_index_of(self):
        self.assertEqual(self.run_code('"hello".indexOf("ll");'), 2)
        self.assertEqual(self.run_code('"hello".indexOf("x");'), -1)
        # Search starting from index 3
        self.assertEqual(self.run_code('"hello".indexOf("l", 3);'), 3)
        self.assertEqual(self.run_code('"hello".indexOf("l", 4);'), -1)

if __name__ == "__main__":
    unittest.main()
