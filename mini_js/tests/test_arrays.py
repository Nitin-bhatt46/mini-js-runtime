import io
import sys
import unittest
from mini_js.lexer import Lexer
from mini_js.parser import Parser
from mini_js.interpreter import Interpreter, RunTimeError

class TestArrays(unittest.TestCase):
    
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

    def test_array_literals_and_indexing(self):
        # Basic parsing & indexing
        self.assertEqual(self.run_code("let a = [10, 20, 30]; a[1];"), 20)
        
        # Out of bounds index access in JS returns undefined (null in MiniJS)
        self.assertEqual(self.run_code("let a = [10, 20]; a[5];"), None)
        
        # Nested array literals
        self.assertEqual(self.run_code("let a = [1, [2, 3]]; a[1][0];"), 2)

    def test_array_index_assignment(self):
        # Normal index reassignment
        code = """
        let arr = [1, 2, 3];
        arr[0] = 99;
        arr[0];
        """
        self.assertEqual(self.run_code(code), 99)

        # Index assignment out of bounds (sparse array expansion)
        code = """
        let arr = [1, 2];
        arr[4] = 5;
        arr;
        """
        # [1, 2, None, None, 5]
        self.assertEqual(self.run_code(code), [1, 2, None, None, 5])

    def test_array_length(self):
        self.assertEqual(self.run_code("let a = [1, 2, 3]; a.length;"), 3)
        self.assertEqual(self.run_code("let a = []; a.length;"), 0)

    def test_array_method_push(self):
        code = """
        let a = [1, 2];
        let len = a.push(3, 4);
        console.log(a);
        len;
        """
        # push returns the new length of the array in JS (4)
        self.assertEqual(self.run_code(code), 4)
        
        output = self.run_and_capture(code)
        self.assertEqual(output, "[1, 2, 3, 4]\n")

    def test_array_method_pop(self):
        code = """
        let a = [10, 20];
        let popped = a.pop();
        console.log(a);
        popped;
        """
        # pop returns the popped element (20)
        self.assertEqual(self.run_code(code), 20)
        
        output = self.run_and_capture(code)
        self.assertEqual(output, "[10]\n")

    def test_array_method_reverse(self):
        code = """
        let a = [1, 2, 3];
        a.reverse();
        """
        self.assertEqual(self.run_code(code), [3, 2, 1])

    def test_array_method_includes(self):
        self.assertEqual(self.run_code("let a = [1, 2, 3]; a.includes(2);"), True)
        self.assertEqual(self.run_code("let a = [1, 2, 3]; a.includes(5);"), False)

    def test_array_method_index_of(self):
        self.assertEqual(self.run_code("let a = [10, 20, 30]; a.indexOf(20);"), 1)
        self.assertEqual(self.run_code("let a = [10, 20, 30]; a.indexOf(50);"), -1)

    def test_array_method_concat(self):
        code = """
        let a = [1, 2];
        let b = a.concat([3, 4], 5);
        b;
        """
        self.assertEqual(self.run_code(code), [1, 2, 3, 4, 5])
        # Ensure original is not modified
        self.assertEqual(self.run_code(code + " a;"), [1, 2])

    def test_array_console_log(self):
        code = "let arr = [1, 2, 3]; arr.push(4); console.log(arr);"
        output = self.run_and_capture(code)
        self.assertEqual(output, "[1, 2, 3, 4]\n")

if __name__ == "__main__":
    unittest.main()
