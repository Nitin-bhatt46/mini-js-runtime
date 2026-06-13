from mini_js.lexer.token import Token, TokenType, KEYWORDS

class LexerError(Exception):
    """Custom exception raised for errors encountered during lexical analysis."""
    
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"LexerError: {message} at line {line}, column {column}")
        self.message = message
        self.line = line
        self.column = column


class Lexer:
    """performs lexical analysis on JavaScript source code, generating a list of Tokens."""

    def __init__(self, input_str: str):
        # Normalize newlines to \n to ensure consistent line/column counting
        self.input = input_str.replace("\r\n", "\n").replace("\r", "\n")
        self.position = 0
        self.read_position = 0
        self.ch = ""
        self.line = 1
        self.column = 1
        
        # Read the first character to initialize
        self.advance()

    def advance(self) -> None:
        """Moves the pointer forward by one character and tracks the line and column numbers."""
        if self.ch == "\n":
            self.line += 1
            self.column = 1
        elif self.ch != "":
            self.column += 1

        if self.read_position >= len(self.input):
            self.ch = ""
        else:
            self.ch = self.input[self.read_position]

        self.position = self.read_position
        self.read_position += 1

    def peek(self) -> str:
        """Looks ahead at the next character in the input without advancing the current position."""
        if self.read_position >= len(self.input):
            return ""
        return self.input[self.read_position]

    def skip_whitespace(self) -> None:
        """Skips spaces, tabs, newlines, and comments (both single-line and multi-line)."""
        while True:
            if self.ch in (" ", "\t", "\n", "\v", "\f"):
                self.advance()
            elif self.ch == "/" and self.peek() == "/":
                # Single-line comment: skip until newline or EOF
                self.advance()
                self.advance()
                while self.ch != "\n" and self.ch != "":
                    self.advance()
            elif self.ch == "/" and self.peek() == "*":
                # Multi-line comment: skip until */
                start_line = self.line
                start_col = self.column
                self.advance()
                self.advance()
                while not (self.ch == "*" and self.peek() == "/"):
                    if self.ch == "":
                        raise LexerError(
                            "Unclosed multi-line comment",
                            start_line,
                            start_col
                        )
                    self.advance()
                # Consume '*' and '/'
                self.advance()
                self.advance()
            else:
                break

    def read_number(self) -> str:
        """Reads and returns a numeric literal (supporting decimals and scientific notation)."""
        start_pos = self.position
        
        # Handle leading dot if present (e.g., .5)
        if self.ch == ".":
            self.advance()
            while self.ch.isdigit():
                self.advance()
        else:
            # Read digit sequence
            while self.ch.isdigit():
                self.advance()
            
            # Check for fractional part
            if self.ch == "." and self.peek().isdigit():
                self.advance()  # consume '.'
                while self.ch.isdigit():
                    self.advance()

        # Check for exponent scientific notation (e.g., 1e3, 1e-3, 1.5e+2)
        if self.ch in ("e", "E"):
            next_char = self.peek()
            if next_char.isdigit():
                self.advance()  # consume 'e'/'E'
                while self.ch.isdigit():
                    self.advance()
            elif next_char in ("+", "-"):
                # Peek two characters ahead to verify digits follow the sign
                if (self.read_position + 1 < len(self.input) and 
                        self.input[self.read_position + 1].isdigit()):
                    self.advance()  # consume 'e'/'E'
                    self.advance()  # consume '+' or '-'
                    while self.ch.isdigit():
                        self.advance()

        return self.input[start_pos:self.position]

    def read_identifier(self) -> str:
        """Reads and returns an identifier or keyword starting with a letter, _, or $."""
        start_pos = self.position
        while self.ch.isalnum() or self.ch in ("_", "$"):
            self.advance()
        return self.input[start_pos:self.position]

    def read_string(self) -> str:
        """Reads a double or single-quoted string literal, resolving escape sequences."""
        quote_char = self.ch
        start_line = self.line
        start_col = self.column
        
        self.advance()  # consume opening quote
        chars = []
        
        while self.ch != quote_char:
            if self.ch == "":
                raise LexerError(
                    "Unterminated string literal",
                    start_line,
                    start_col
                )
            
            if self.ch == "\\":
                self.advance()  # consume '\\'
                if self.ch == "":
                    raise LexerError(
                        "Unterminated string literal with trailing backslash",
                        start_line,
                        start_col
                    )
                # Escape sequences mapping
                escapes = {
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    "b": "\b",
                    "f": "\f",
                    "\\": "\\",
                    '"': '"',
                    "'": "'",
                }
                if self.ch in escapes:
                    chars.append(escapes[self.ch])
                else:
                    # Unrecognized escapes are treated literally
                    chars.append(self.ch)
            else:
                chars.append(self.ch)
            
            self.advance()
            
        self.advance()  # consume closing quote
        return "".join(chars)

    def tokenize(self) -> list[Token]:
        """Scans the source code and returns a list of Token objects, ending with EOF."""
        tokens = []
        
        while True:
            self.skip_whitespace()
            
            # Record starting coordinate of the token
            token_line = self.line
            token_column = self.column
            
            if self.ch == "":
                tokens.append(Token(TokenType.EOF, "", token_line, token_column))
                break

            # 1. Operators & Punctuation (handling longer prefixes first)
            # ===, ==, =
            if self.ch == "=":
                if self.peek() == "=":
                    self.advance()  # consume second '='
                    if self.peek() == "=":
                        self.advance()  # consume third '='
                        self.advance()
                        tokens.append(Token(TokenType.STRICT_EQ, "===", token_line, token_column))
                    else:
                        self.advance()
                        tokens.append(Token(TokenType.EQ, "==", token_line, token_column))
                else:
                    self.advance()
                    tokens.append(Token(TokenType.ASSIGN, "=", token_line, token_column))

            # !=
            elif self.ch == "!":
                if self.peek() == "=":
                    self.advance()  # consume second '='
                    self.advance()
                    tokens.append(Token(TokenType.NOT_EQ, "!=", token_line, token_column))
                else:
                    self.advance()
                    tokens.append(Token(TokenType.BANG, "!", token_line, token_column))

            # <=, <
            elif self.ch == "<":
                if self.peek() == "=":
                    self.advance()
                    self.advance()
                    tokens.append(Token(TokenType.LTE, "<=", token_line, token_column))
                else:
                    self.advance()
                    tokens.append(Token(TokenType.LT, "<", token_line, token_column))

            # >=, >
            elif self.ch == ">":
                if self.peek() == "=":
                    self.advance()
                    self.advance()
                    tokens.append(Token(TokenType.GTE, ">=", token_line, token_column))
                else:
                    self.advance()
                    tokens.append(Token(TokenType.GT, ">", token_line, token_column))

            # **, *
            elif self.ch == "*":
                if self.peek() == "*":
                    self.advance()
                    self.advance()
                    tokens.append(Token(TokenType.EXPONENT, "**", token_line, token_column))
                else:
                    self.advance()
                    tokens.append(Token(TokenType.ASTERISK, "*", token_line, token_column))

            # &&
            elif self.ch == "&":
                if self.peek() == "&":
                    self.advance()
                    self.advance()
                    tokens.append(Token(TokenType.AND, "&&", token_line, token_column))
                else:
                    illegal_char = self.ch
                    self.advance()
                    raise LexerError(
                        f"Unexpected character '{illegal_char}' (did you mean '&&'?)",
                        token_line,
                        token_column
                    )

            # ||
            elif self.ch == "|":
                if self.peek() == "|":
                    self.advance()
                    self.advance()
                    tokens.append(Token(TokenType.OR, "||", token_line, token_column))
                else:
                    illegal_char = self.ch
                    self.advance()
                    raise LexerError(
                        f"Unexpected character '{illegal_char}' (did you mean '||'?)",
                        token_line,
                        token_column
                    )

            # Single-character Operators
            elif self.ch == "+":
                self.advance()
                tokens.append(Token(TokenType.PLUS, "+", token_line, token_column))
            elif self.ch == "-":
                self.advance()
                tokens.append(Token(TokenType.MINUS, "-", token_line, token_column))
            elif self.ch == "/":
                self.advance()
                tokens.append(Token(TokenType.SLASH, "/", token_line, token_column))
            elif self.ch == "%":
                self.advance()
                tokens.append(Token(TokenType.PERCENT, "%", token_line, token_column))

            # Punctuation
            elif self.ch == "(":
                self.advance()
                tokens.append(Token(TokenType.LPAREN, "(", token_line, token_column))
            elif self.ch == ")":
                self.advance()
                tokens.append(Token(TokenType.RPAREN, ")", token_line, token_column))
            elif self.ch == "{":
                self.advance()
                tokens.append(Token(TokenType.LBRACE, "{", token_line, token_column))
            elif self.ch == "}":
                self.advance()
                tokens.append(Token(TokenType.RBRACE, "}", token_line, token_column))
            elif self.ch == "[":
                self.advance()
                tokens.append(Token(TokenType.LBRACKET, "[", token_line, token_column))
            elif self.ch == "]":
                self.advance()
                tokens.append(Token(TokenType.RBRACKET, "]", token_line, token_column))
            elif self.ch == ";":
                self.advance()
                tokens.append(Token(TokenType.SEMICOLON, ";", token_line, token_column))
            elif self.ch == ",":
                self.advance()
                tokens.append(Token(TokenType.COMMA, ",", token_line, token_column))
            elif self.ch == ".":
                # Check if it is the start of a decimal literal like `.5`
                if self.peek().isdigit():
                    num_val = self.read_number()
                    tokens.append(Token(TokenType.NUMBER, num_val, token_line, token_column))
                else:
                    self.advance()
                    tokens.append(Token(TokenType.DOT, ".", token_line, token_column))
            elif self.ch == ":":
                self.advance()
                tokens.append(Token(TokenType.COLON, ":", token_line, token_column))

            # 2. String Literals
            elif self.ch in ('"', "'"):
                str_val = self.read_string()
                tokens.append(Token(TokenType.STRING, str_val, token_line, token_column))

            # 3. Numeric Literals
            elif self.ch.isdigit():
                num_val = self.read_number()
                tokens.append(Token(TokenType.NUMBER, num_val, token_line, token_column))

            # 4. Identifiers & Keywords
            elif self.ch.isalpha() or self.ch in ("_", "$"):
                ident_val = self.read_identifier()
                if ident_val in KEYWORDS:
                    tokens.append(Token(KEYWORDS[ident_val], ident_val, token_line, token_column))
                else:
                    tokens.append(Token(TokenType.IDENT, ident_val, token_line, token_column))

            # 5. Unexpected Characters
            else:
                illegal_char = self.ch
                self.advance()
                raise LexerError(
                    f"Unexpected character '{illegal_char}'",
                    token_line,
                    token_column
                )

        return tokens
