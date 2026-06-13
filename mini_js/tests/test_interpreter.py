import io
import sys
import unittest
from mini_js.lexer import Lexer
from mini_js.parser import Parser
from mini_js.interpreter import Interpreter, RunTimeError

class TestInterpreter(unittest.TestCase):

    def run_code(self, source_code: str) -> any:
        """Helper to evaluate code and return last statement value."""
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        return interpreter.evaluate(ast)

    def run_and_capture(self, source_code: str) -> str:
        """Helper to evaluate code and capture stdout print logs."""
        old_stdout = sys.stdout
        captured = io.StringIO()
        sys.stdout = captured
        try:
            self.run_code(source_code)
            return captured.getvalue()
        finally:
            sys.stdout = old_stdout

    def test_basic_arithmetic(self):
        self.assertEqual(self.run_code("1 + 2;"), 3)
        self.assertEqual(self.run_code("10 - 4;"), 6)
        self.assertEqual(self.run_code("3 * 4;"), 12)
        self.assertEqual(self.run_code("10 / 2;"), 5.0)
        self.assertEqual(self.run_code("10 % 3;"), 1)
        self.assertEqual(self.run_code("2 ** 3;"), 8)

    def test_operator_precedence(self):
        self.assertEqual(self.run_code("1 + 2 * 3;"), 7)
        self.assertEqual(self.run_code("(1 + 2) * 3;"), 9)
        self.assertEqual(self.run_code("2 * 3 ** 2;"), 18)

    def test_string_concatenation(self):
        self.assertEqual(self.run_code('"hello " + "world";'), "hello world")
        self.assertEqual(self.run_code('"value: " + 42;'), "value: 42")
        self.assertEqual(self.run_code('true + " is truthy";'), "true is truthy")

    def test_comparisons(self):
        self.assertEqual(self.run_code("5 > 3;"), True)
        self.assertEqual(self.run_code("5 < 3;"), False)
        self.assertEqual(self.run_code("5 >= 5;"), True)
        self.assertEqual(self.run_code("5 <= 4;"), False)
        self.assertEqual(self.run_code("5 === 5.0;"), True)
        self.assertEqual(self.run_code("5 === '5';"), False)
        self.assertEqual(self.run_code("5 == '5';"), False)  # Simple comparison checks
        self.assertEqual(self.run_code("5 != 6;"), True)

    def test_logical_operators(self):
        self.assertEqual(self.run_code("true && false;"), False)
        self.assertEqual(self.run_code("true || false;"), True)
        self.assertEqual(self.run_code("!true;"), False)
        self.assertEqual(self.run_code("!false;"), True)
        
        # Short-circuiting tests
        self.assertEqual(self.run_code("0 && 'hello';"), 0)
        self.assertEqual(self.run_code("'hello' || 'world';"), "hello")
        self.assertEqual(self.run_code("null || 42;"), 42)

    def test_variable_declarations_and_scoping(self):
        code = """
        let x = 10;
        const y = 20;
        let z;
        x = x + y;
        """
        self.assertEqual(self.run_code(code), 30)

        # Block scoping variable masking
        code = """
        let a = 1;
        {
            let a = 100;
        }
        a;
        """
        self.assertEqual(self.run_code(code), 1)

        # Scoping assignments in nested blocks
        code = """
        let a = 1;
        {
            a = 99;
        }
        a;
        """
        self.assertEqual(self.run_code(code), 99)

    def test_console_log(self):
        code = """
        let a = 5;
        let b = 10;
        console.log(a + b);
        console.log("result:", true, null);
        """
        output = self.run_and_capture(code)
        expected = "15\nresult: true null\n"
        self.assertEqual(output, expected)

    def test_conditional_execution(self):
        # 1. Simple if truthy
        code = """
        let x = 0;
        if (5 > 3) {
            x = 100;
        }
        x;
        """
        self.assertEqual(self.run_code(code), 100)

        # 2. Simple if falsy (does not run consequent)
        code = """
        let x = 0;
        if (false) {
            x = 100;
        }
        x;
        """
        self.assertEqual(self.run_code(code), 0)

        # 3. If-else branching
        code = """
        let x = 0;
        if (false) {
            x = 100;
        } else {
            x = 200;
        }
        x;
        """
        self.assertEqual(self.run_code(code), 200)

        # 4. Else-if chain branching
        code = """
        let a = 10;
        let result = 0;
        if (a > 15) {
            result = 1;
        } else if (a > 5) {
            result = 2;
        } else {
            result = 3;
        }
        result;
        """
        self.assertEqual(self.run_code(code), 2)

    def test_while_loops(self):
        # 1. Loop counting test
        code = """
        let i = 0;
        let sum = 0;
        while (i < 5) {
            sum = sum + i;
            i = i + 1;
        }
        sum;
        """
        self.assertEqual(self.run_code(code), 10)

        # 2. Initially false loop (no execution)
        code = """
        let x = 10;
        while (x < 5) {
            x = 100;
        }
        x;
        """
        self.assertEqual(self.run_code(code), 10)

        # 3. Log values inside a loop
        code = """
        let i = 0;
        while (i < 3) {
            console.log(i);
            i = i + 1;
        }
        """
        output = self.run_and_capture(code)
        self.assertEqual(output, "0\n1\n2\n")

    def test_for_loops(self):
        # 1. Loop counting and summation
        code = """
        let sum = 0;
        for (let i = 1; i <= 5; i = i + 1) {
            sum = sum + i;
        }
        sum;
        """
        self.assertEqual(self.run_code(code), 15)

        # 2. Scoping check: variable declared in init is local to loop
        code = """
        let result = 10;
        for (let i = 0; i < 5; i = i + 1) {
            result = result + i;
        }
        // accessing 'i' outside should fail
        i;
        """
        with self.assertRaises(RunTimeError) as context:
            self.run_code(code)
        self.assertIn("is not defined", context.exception.message)

        # 3. Log verification in loop
        code = """
        for (let i = 1; i <= 3; i = i + 1) {
            console.log(i);
        }
        """
        output = self.run_and_capture(code)
        self.assertEqual(output, "1\n2\n3\n")

    def test_functions(self):
        # 1. Simple function evaluation
        code = """
        function add(a, b) {
            return a + b;
        }
        add(2, 3);
        """
        self.assertEqual(self.run_code(code), 5)

        # 2. Local scopes: variable leakage check
        code = """
        function test() {
            let localVar = 42;
            return localVar;
        }
        test();
        // localVar should not leak to global scope
        localVar;
        """
        with self.assertRaises(RunTimeError) as context:
            self.run_code(code)
        self.assertIn("is not defined", context.exception.message)

        # 3. Nested call evaluation
        code = """
        function double(x) {
            return x * 2;
        }
        function addAndDouble(a, b) {
            return double(a + b);
        }
        addAndDouble(3, 4);
        """
        self.assertEqual(self.run_code(code), 14)

        # 4. Closures check: functions capturing enclosing environment
        code = """
        let x = 10;
        function makeClosure() {
            return x;
        }
        {
            let x = 20;
            makeClosure(); // Should evaluate to 10 from its declaration closure
        }
        """
        self.assertEqual(self.run_code(code), 10)

    def test_runtime_errors_const_assignment(self):
        code = """
        const x = 10;
        x = 20;
        """
        with self.assertRaises(RunTimeError) as context:
            self.run_code(code)
        self.assertIn("Assignment to constant variable", context.exception.message)

    def test_runtime_errors_undeclared_variable(self):
        code = "y = 10;"
        with self.assertRaises(RunTimeError) as context:
            self.run_code(code)
        self.assertIn("not defined", context.exception.message)

    def test_runtime_errors_redeclaration(self):
        code = """
        let x = 10;
        let x = 20;
        """
        with self.assertRaises(RunTimeError) as context:
            self.run_code(code)
        self.assertIn("already been declared", context.exception.message)

    def test_runtime_errors_division_by_zero(self):
        with self.assertRaises(RunTimeError) as context:
            self.run_code("10 / 0;")
        self.assertIn("Division by zero", context.exception.message)

if __name__ == "__main__":
    unittest.main()
