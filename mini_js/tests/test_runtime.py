import io
import sys
import unittest
from mini_js.runtime import Console

class TestRuntime(unittest.TestCase):
    
    def setUp(self):
        self.console = Console()
        self.held_stdout = sys.stdout
        self.captured = io.StringIO()
        sys.stdout = self.captured

    def tearDown(self):
        sys.stdout = self.held_stdout

    def test_console_log_string(self):
        self.console.log("Hello")
        self.assertEqual(self.captured.getvalue(), "Hello\n")

    def test_console_log_number(self):
        self.console.log(5)
        self.assertEqual(self.captured.getvalue(), "5\n")

    def test_console_log_booleans(self):
        self.console.log(True)
        self.assertEqual(self.captured.getvalue(), "true\n")
        
        # Reset capture
        self.captured.seek(0)
        self.captured.truncate(0)
        
        self.console.log(False)
        self.assertEqual(self.captured.getvalue(), "false\n")

    def test_console_log_null(self):
        self.console.log(None)
        self.assertEqual(self.captured.getvalue(), "null\n")

    def test_console_log_multiple_arguments(self):
        self.console.log("a", "b", 5)
        self.assertEqual(self.captured.getvalue(), "a b 5\n")

if __name__ == "__main__":
    unittest.main()
