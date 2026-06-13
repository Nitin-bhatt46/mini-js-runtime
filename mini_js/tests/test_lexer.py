import unittest
from mini_js.lexer import Lexer, LexerError, Token, TokenType

class TestLexer(unittest.TestCase):
    
    def test_empty_input(self):
        lexer = Lexer("")
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], Token(TokenType.EOF, "", 1, 1))

    def test_whitespace_and_comments(self):
        code = """
        // This is a single line comment
        let x = 10; /* This is a
        multi-line comment */
        const y = 20;
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        expected = [
            Token(TokenType.LET, "let", 3, 9),
            Token(TokenType.IDENT, "x", 3, 13),
            Token(TokenType.ASSIGN, "=", 3, 15),
            Token(TokenType.NUMBER, "10", 3, 17),
            Token(TokenType.SEMICOLON, ";", 3, 19),
            Token(TokenType.CONST, "const", 5, 9),
            Token(TokenType.IDENT, "y", 5, 15),
            Token(TokenType.ASSIGN, "=", 5, 17),
            Token(TokenType.NUMBER, "20", 5, 19),
            Token(TokenType.SEMICOLON, ";", 5, 21),
            Token(TokenType.EOF, "", 6, 9)
        ]
        self.assertEqual(tokens, expected)

    def test_keywords(self):
        code = "let const function if else while for return true false null"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.LET, TokenType.CONST, TokenType.FUNCTION, TokenType.IF,
            TokenType.ELSE, TokenType.WHILE, TokenType.FOR, TokenType.RETURN,
            TokenType.TRUE, TokenType.FALSE, TokenType.NULL, TokenType.EOF
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_operators(self):
        code = "+ - * / % ** = == === != < > <= >= && || !"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.PLUS, TokenType.MINUS, TokenType.ASTERISK, TokenType.SLASH,
            TokenType.PERCENT, TokenType.EXPONENT, TokenType.ASSIGN, TokenType.EQ,
            TokenType.STRICT_EQ, TokenType.NOT_EQ, TokenType.LT, TokenType.GT,
            TokenType.LTE, TokenType.GTE, TokenType.AND, TokenType.OR, TokenType.BANG,
            TokenType.EOF
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_punctuation(self):
        code = "( ) { } [ ] ; , . :"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE, TokenType.RBRACE,
            TokenType.LBRACKET, TokenType.RBRACKET, TokenType.SEMICOLON, TokenType.COMMA,
            TokenType.DOT, TokenType.COLON, TokenType.EOF
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_identifiers(self):
        code = "x _myVar $price var123"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        self.assertEqual(tokens[0], Token(TokenType.IDENT, "x", 1, 1))
        self.assertEqual(tokens[1], Token(TokenType.IDENT, "_myVar", 1, 3))
        self.assertEqual(tokens[2], Token(TokenType.IDENT, "$price", 1, 10))
        self.assertEqual(tokens[3], Token(TokenType.IDENT, "var123", 1, 17))
        self.assertEqual(tokens[-1].type, TokenType.EOF)

    def test_numbers(self):
        # Test integer, decimal, leading dot, and scientific notations
        code = "42 3.14 .75 1e3 1.5E-2 2e+4"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        expected_values = ["42", "3.14", ".75", "1e3", "1.5E-2", "2e+4"]
        self.assertEqual([t.value for t in tokens[:-1]], expected_values)
        for t in tokens[:-1]:
            self.assertEqual(t.type, TokenType.NUMBER)

    def test_strings(self):
        # Double and single quoted strings, including escapes
        code = '"hello" \'world\' "line\\nbreak" \'escaped\\\'quote\''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        expected_values = ["hello", "world", "line\nbreak", "escaped'quote"]
        self.assertEqual([t.value for t in tokens[:-1]], expected_values)
        for t in tokens[:-1]:
            self.assertEqual(t.type, TokenType.STRING)

    def test_sample_js_program(self):
        code = """
        let x = 5;
        console.log(x);
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        expected = [
            Token(TokenType.LET, "let", 2, 9),
            Token(TokenType.IDENT, "x", 2, 13),
            Token(TokenType.ASSIGN, "=", 2, 15),
            Token(TokenType.NUMBER, "5", 2, 17),
            Token(TokenType.SEMICOLON, ";", 2, 18),
            
            Token(TokenType.IDENT, "console", 3, 9),
            Token(TokenType.DOT, ".", 3, 16),
            Token(TokenType.IDENT, "log", 3, 17),
            Token(TokenType.LPAREN, "(", 3, 20),
            Token(TokenType.IDENT, "x", 3, 21),
            Token(TokenType.RPAREN, ")", 3, 22),
            Token(TokenType.SEMICOLON, ";", 3, 23),
            Token(TokenType.EOF, "", 4, 9),
        ]
        self.assertEqual(tokens, expected)

    def test_error_unclosed_string(self):
        code = 'let s = "hello'
        lexer = Lexer(code)
        with self.assertRaises(LexerError) as context:
            lexer.tokenize()
        self.assertEqual(context.exception.line, 1)
        self.assertEqual(context.exception.column, 9)
        self.assertIn("Unterminated string", context.exception.message)

    def test_error_unclosed_comment(self):
        code = 'let x = 1; /* unclosed comment'
        lexer = Lexer(code)
        with self.assertRaises(LexerError) as context:
            lexer.tokenize()
        self.assertEqual(context.exception.line, 1)
        self.assertEqual(context.exception.column, 12)
        self.assertIn("Unclosed multi-line comment", context.exception.message)

    def test_error_illegal_character(self):
        code = 'let x = #;'
        lexer = Lexer(code)
        with self.assertRaises(LexerError) as context:
            lexer.tokenize()
        self.assertEqual(context.exception.line, 1)
        self.assertEqual(context.exception.column, 9)
        self.assertIn("Unexpected character '#'", context.exception.message)

    def test_error_invalid_logical_and(self):
        code = 'let x = true & false;'
        lexer = Lexer(code)
        with self.assertRaises(LexerError) as context:
            lexer.tokenize()
        self.assertEqual(context.exception.line, 1)
        self.assertEqual(context.exception.column, 14)
        self.assertIn("Unexpected character '&'", context.exception.message)

if __name__ == "__main__":
    unittest.main()
