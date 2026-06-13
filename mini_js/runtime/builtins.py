import sys

class Console:
    """Built-in console object for standard stdout reporting."""
    
    def __init__(self):
        self.members = {
            "log": self.log
        }
        

    def log(self, *args) -> None:
        """Prints space-separated arguments to stdout, formatting JS-like values."""
        def to_js_str(val) -> str:
            if val is True:
                return "true"
            if val is False:
                return "false"
            if val is None:
                return "null"
            if isinstance(val, list):
                return "[" + ", ".join(to_js_str(item) for item in val) + "]"
            return str(val)

        print(" ".join(to_js_str(arg) for arg in args))
        sys.stdout.flush()
