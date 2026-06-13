class RunTimeError(Exception):
    """Exception raised for errors during script execution."""
    def __init__(self, message: str, line: int = 0, column: int = 0):
        super().__init__(f"RunTimeError: {message}")
        self.message = message
        self.line = line
        self.column = column



class Environment:
    """Manages variable binding scopes, constants validation, and nesting enclosing environments."""
    
    def __init__(self, enclosing: "Environment" = None):
        self.values = {}       # maps variable name -> value
        self.is_const = {}     # maps variable name -> bool
        self.enclosing = enclosing

    def define(self, name: str, value: any, is_const: bool) -> None:
        """Declares a variable in the local environment scope."""
        if name in self.values:
            raise RunTimeError(f"Identifier '{name}' has already been declared")
        self.values[name] = value
        self.is_const[name] = is_const

    def get(self, name: str) -> any:
        """Retrieves the value of a variable from this environment or outer scopes."""
        if name in self.values:
            return self.values[name]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise RunTimeError(f"'{name}' is not defined")

    def assign(self, name: str, value: any) -> None:
        """Assigns a new value to an already declared variable."""
        if name in self.values:
            if self.is_const[name]:
                raise RunTimeError(f"Assignment to constant variable '{name}'")
            self.values[name] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise RunTimeError(f"'{name}' is not defined")
