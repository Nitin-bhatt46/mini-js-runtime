from mini_js.lexer import Token, TokenType
from mini_js.ast import (
    ASTNode,
    Program,
    VariableDeclaration,
    AssignmentExpression,
    BinaryExpression,
    UnaryExpression,
    Identifier,
    Literal,
    BlockStatement,
    ExpressionStatement,
    CallExpression,
    MemberExpression,
    IfStatement,
    WhileStatement,
    ForStatement,
    FunctionDeclaration,
    ReturnStatement,
    ArrayLiteral,
    IndexExpression,
)


class ParserError(Exception):
    """Custom exception raised for parsing errors."""
    
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"ParserError: {message} at line {line}, column {column}")
        self.message = message
        self.line = line
        self.column = column


class Parser:
    """Recursive descent parser to convert tokens into a structured AST."""
    
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current_position = 0

    @property
    def current_token(self) -> Token:
        """Returns the token currently under examination."""
        return self.tokens[self.current_position]

    def is_at_end(self) -> bool:
        """Checks if parsing has reached the end of the token stream."""
        return self.current_token.type == TokenType.EOF

    def advance(self) -> Token:
        """Advances the token pointer by one and returns the previous token."""
        if not self.is_at_end():
            self.current_position += 1
        return self.previous()

    def previous(self) -> Token:
        """Returns the token immediately preceding the current position."""
        return self.tokens[self.current_position - 1]

    def peek(self) -> Token:
        """Looks ahead at the current token without consuming it."""
        return self.tokens[self.current_position]

    def check(self, type_: TokenType) -> bool:
        """Checks if the current token matches a given type."""
        if self.is_at_end():
            return False
        return self.current_token.type == type_

    def match(self, *types: TokenType) -> bool:
        """If current token matches any of the types, consumes it and returns True."""
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, type_: TokenType, message: str) -> Token:
        """Consumes a specific token type or raises a ParserError with the given message."""
        if self.check(type_):
            return self.advance()
        raise ParserError(message, self.current_token.line, self.current_token.column)

    def parse(self) -> Program:
        """Parses the entire token list into a Program node."""
        body = []
        while not self.is_at_end():
            body.append(self.parse_statement())
        return Program(body)

    # --- Statement Parsers ---

    def parse_statement(self) -> ASTNode:
        """Dispatches parsing to specific statements based on current token."""
        if self.check(TokenType.LET) or self.check(TokenType.CONST):
            return self.parse_variable_declaration()
        if self.check(TokenType.LBRACE):
            return self.parse_block_statement()
        if self.check(TokenType.IF):
            return self.parse_if_statement()
        if self.check(TokenType.WHILE):
            return self.parse_while_statement()
        if self.check(TokenType.FOR):
            return self.parse_for_statement()
        if self.check(TokenType.FUNCTION):
            return self.parse_function_declaration()
        if self.check(TokenType.RETURN):
            return self.parse_return_statement()
        return self.parse_expression_statement()

    def parse_if_statement(self) -> IfStatement:
        """Parses if / else if / else statements."""
        self.consume(TokenType.IF, "Expect 'if'")
        self.consume(TokenType.LPAREN, "Expect '(' after 'if'")
        test = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expect ')' after condition")
        
        consequent = self.parse_statement()
        
        alternate = None
        if self.match(TokenType.ELSE):
            alternate = self.parse_statement()
            
        return IfStatement(test, consequent, alternate)

    def parse_while_statement(self) -> WhileStatement:
        """Parses while loop statements."""
        self.consume(TokenType.WHILE, "Expect 'while'")
        self.consume(TokenType.LPAREN, "Expect '(' after 'while'")
        test = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expect ')' after condition")
        
        body = self.parse_statement()
        return WhileStatement(test, body)

    def parse_for_statement(self) -> ForStatement:
        """Parses for loop statements."""
        self.consume(TokenType.FOR, "Expect 'for'")
        self.consume(TokenType.LPAREN, "Expect '(' after 'for'")
        
        # 1. Initialization
        init = None
        if self.match(TokenType.SEMICOLON):
            init = None
        elif self.check(TokenType.LET) or self.check(TokenType.CONST):
            init = self.parse_variable_declaration()
        else:
            init = self.parse_expression()
            self.consume(TokenType.SEMICOLON, "Expect ';' after loop initialization")
            
        # 2. Condition
        test = None
        if not self.check(TokenType.SEMICOLON):
            test = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition")
        
        # 3. Update/Increment
        update = None
        if not self.check(TokenType.RPAREN):
            update = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expect ')' after loop update")
        
        # 4. Body
        body = self.parse_statement()
        
        return ForStatement(init, test, update, body)

    def parse_function_declaration(self) -> FunctionDeclaration:
        """Parses function declaration statements."""
        self.consume(TokenType.FUNCTION, "Expect 'function'")
        ident_token = self.consume(TokenType.IDENT, "Expect function name")
        name_id = Identifier(ident_token.value)
        
        self.consume(TokenType.LPAREN, "Expect '(' after function name")
        params = []
        if not self.check(TokenType.RPAREN):
            while True:
                param_token = self.consume(TokenType.IDENT, "Expect parameter name")
                params.append(Identifier(param_token.value))
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RPAREN, "Expect ')' after parameters list")
        
        body = self.parse_block_statement()
        return FunctionDeclaration(name_id, params, body)

    def parse_return_statement(self) -> ReturnStatement:
        """Parses return statements."""
        self.consume(TokenType.RETURN, "Expect 'return'")
        argument = None
        if not self.check(TokenType.SEMICOLON):
            argument = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after return statement")
        return ReturnStatement(argument)

    def parse_variable_declaration(self) -> VariableDeclaration:
        """Parses variable declarations: (let | const) name [= init_expr];"""
        kind = self.advance().value  # Consume 'let' or 'const'
        ident_token = self.consume(TokenType.IDENT, "Expect variable name after declaration keyword")
        identifier = Identifier(ident_token.value)
        
        init = None
        if self.match(TokenType.ASSIGN):
            init = self.parse_expression()
            
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration")
        return VariableDeclaration(kind=kind, identifier=identifier, init=init)



    def parse_block_statement(self) -> BlockStatement:
        """Parses a block statement: { statement1; statement2; ... }"""
        self.consume(TokenType.LBRACE, "Expect '{' to begin block statement")
        body = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            body.append(self.parse_statement())
        self.consume(TokenType.RBRACE, "Expect '}' to close block statement")
        return BlockStatement(body)

    def parse_expression_statement(self) -> ExpressionStatement:
        """Parses a standalone expression statement: expr;"""
        expr = self.parse_expression()
        # Semicolon is technically required in many contexts, but we support optional semi for expression statements
        if self.match(TokenType.SEMICOLON):
            pass
        return ExpressionStatement(expr)

    # --- Expression Parsers (Precedence Order: Low to High) ---

    def parse_expression(self) -> ASTNode:
        """Main expression entry point."""
        return self.parse_assignment()

    def parse_assignment(self) -> ASTNode:
        """Parses assignment expression: name = value or index = value (right-associative)."""
        expr = self.parse_logical_or()
        
        if self.match(TokenType.ASSIGN):
            assign_token = self.previous()
            if not isinstance(expr, (Identifier, IndexExpression)):
                raise ParserError("Invalid assignment target", assign_token.line, assign_token.column)
            right = self.parse_assignment()  # right-associative recursion
            return AssignmentExpression(operator="=", left=expr, right=right)
            
        return expr

    def parse_logical_or(self) -> ASTNode:
        """Parses logical OR expressions: left || right (left-associative)."""
        expr = self.parse_logical_and()
        
        while self.match(TokenType.OR):
            op = "||"
            right = self.parse_logical_and()
            expr = BinaryExpression(operator=op, left=expr, right=right)
            
        return expr

    def parse_logical_and(self) -> ASTNode:
        """Parses logical AND expressions: left && right (left-associative)."""
        expr = self.parse_equality()
        
        while self.match(TokenType.AND):
            op = "&&"
            right = self.parse_equality()
            expr = BinaryExpression(operator=op, left=expr, right=right)
            
        return expr

    def parse_equality(self) -> ASTNode:
        """Parses equality expressions: left (== | === | !=) right (left-associative)."""
        expr = self.parse_comparison()
        
        while self.match(TokenType.STRICT_EQ, TokenType.EQ, TokenType.NOT_EQ):
            op = self.previous().value
            right = self.parse_comparison()
            expr = BinaryExpression(operator=op, left=expr, right=right)
            
        return expr

    def parse_comparison(self) -> ASTNode:
        """Parses comparisons: left (< | > | <= | >=) right (left-associative)."""
        expr = self.parse_additive()
        
        while self.match(TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            op = self.previous().value
            right = self.parse_additive()
            expr = BinaryExpression(operator=op, left=expr, right=right)
            
        return expr

    def parse_additive(self) -> ASTNode:
        """Parses arithmetic addition and subtraction: left (+ | -) right (left-associative)."""
        expr = self.parse_multiplicative()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.previous().value
            right = self.parse_multiplicative()
            expr = BinaryExpression(operator=op, left=expr, right=right)
            
        return expr

    def parse_multiplicative(self) -> ASTNode:
        """Parses arithmetic multiplication, division, and modulo: left (* | / | %) right (left-associative)."""
        expr = self.parse_exponentiation()
        
        while self.match(TokenType.ASTERISK, TokenType.SLASH, TokenType.PERCENT):
            op = self.previous().value
            right = self.parse_exponentiation()
            expr = BinaryExpression(operator=op, left=expr, right=right)
            
        return expr

    def parse_exponentiation(self) -> ASTNode:
        """Parses exponentiation: left ** right (right-associative)."""
        expr = self.parse_unary()
        
        if self.match(TokenType.EXPONENT):
            op = "**"
            right = self.parse_exponentiation()  # right-associative recursion
            expr = BinaryExpression(operator=op, left=expr, right=right)
            
        return expr

    def parse_unary(self) -> ASTNode:
        """Parses unary prefix operations: !, -, + (right-associative)."""
        if self.match(TokenType.BANG):
            op = "!"
            arg = self.parse_unary()
            return UnaryExpression(operator=op, argument=arg)
        if self.match(TokenType.MINUS):
            op = "-"
            arg = self.parse_unary()
            return UnaryExpression(operator=op, argument=arg)
        if self.match(TokenType.PLUS):
            op = "+"
            arg = self.parse_unary()
            return UnaryExpression(operator=op, argument=arg)
        return self.parse_call_member()


    def parse_call_member(self) -> ASTNode:
        """Parses function calls, member dot accesses, and bracket index expressions."""
        expr = self.parse_primary()
        while True:
            if self.match(TokenType.DOT):
                prop_token = self.consume(TokenType.IDENT, "Expect property name after '.'")
                property_node = Identifier(prop_token.value)
                expr = MemberExpression(expr, property_node)
            elif self.match(TokenType.LPAREN):
                args = []
                if not self.check(TokenType.RPAREN):
                    while True:
                        args.append(self.parse_expression())
                        if not self.match(TokenType.COMMA):
                            break
                self.consume(TokenType.RPAREN, "Expect ')' after arguments list")
                expr = CallExpression(expr, args)
            elif self.match(TokenType.LBRACKET):
                index_expr = self.parse_expression()
                self.consume(TokenType.RBRACKET, "Expect ']' after index access")
                expr = IndexExpression(expr, index_expr)
            else:
                break
        return expr

    def parse_primary(self) -> ASTNode:
        """Parses atomic primary values: Literals, Identifiers, Groupings, and Arrays."""
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.NULL):
            return Literal(None)

        if self.match(TokenType.NUMBER):
            val = self.previous().value
            if "." in val or "e" in val.lower():
                return Literal(float(val))
            return Literal(int(val))

        if self.match(TokenType.STRING):
            return Literal(self.previous().value)

        if self.match(TokenType.IDENT):
            return Identifier(self.previous().value)

        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expect ')' after expression grouping")
            return expr

        if self.match(TokenType.LBRACKET):
            elements = []
            if not self.check(TokenType.RBRACKET):
                while True:
                    elements.append(self.parse_expression())
                    if not self.match(TokenType.COMMA):
                        break
            self.consume(TokenType.RBRACKET, "Expect ']' after array elements")
            return ArrayLiteral(elements)

        raise ParserError(
            f"Expect expression but found '{self.current_token.value}'",
            self.current_token.line,
            self.current_token.column,
        )
