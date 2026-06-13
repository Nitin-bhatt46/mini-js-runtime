import enum

class TokenType(enum.Enum):
    # Special types
    EOF = "EOF"
    ILLEGAL = "ILLEGAL"

    # Identifiers & Literals
    IDENT = "IDENT"
    NUMBER = "NUMBER"
    STRING = "STRING"

    # Keywords
    LET = "let"
    CONST = "const"
    FUNCTION = "function"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    FOR = "for"
    RETURN = "return"
    TRUE = "true"
    FALSE = "false"
    NULL = "null"

    # Operators
    PLUS = "+"
    MINUS = "-"
    ASTERISK = "*"
    SLASH = "/"
    PERCENT = "%"
    EXPONENT = "**"
    
    ASSIGN = "="
    EQ = "=="
    STRICT_EQ = "==="
    NOT_EQ = "!="
    
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="
    
    AND = "&&"
    OR = "||"
    BANG = "!"

    # Punctuation
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    SEMICOLON = ";"
    COMMA = ","
    DOT = "."
    COLON = ":"


class Token:
    """Represents a token produced by the Lexer."""
    
    def __init__(self, type_: TokenType, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line}, col={self.column})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return NotImplemented
        return (
            self.type == other.type
            and self.value == other.value
            and self.line == other.line
            and self.column == other.column
        )


# Mapping of keywords to their corresponding TokenType
KEYWORDS = {
    "let": TokenType.LET,
    "const": TokenType.CONST,
    "function": TokenType.FUNCTION,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "null": TokenType.NULL,
}
