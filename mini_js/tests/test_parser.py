import unittest
from mini_js.lexer import Lexer
from mini_js.parser import Parser, ParserError
from mini_js.ast import (
    Program,
    VariableDeclaration,
    AssignmentExpression,
    BinaryExpression,
    UnaryExpression,
    Identifier,
    Literal,
    BlockStatement,
    ExpressionStatement,
)

class TestParser(unittest.TestCase):

    def parse_code(self, source_code: str) -> dict:
        """Helper to tokenize, parse, and serialize to dictionary representation."""
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        return ast.to_dict()

    def test_variable_declarations(self):
        # Initialized variable
        ast_dict = self.parse_code("let x = 5;")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "VariableDeclaration",
                    "kind": "let",
                    "identifier": {"type": "Identifier", "name": "x"},
                    "init": {"type": "Literal", "value": 5}
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

        # Const declaration
        ast_dict = self.parse_code("const y = 10.5;")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "VariableDeclaration",
                    "kind": "const",
                    "identifier": {"type": "Identifier", "name": "y"},
                    "init": {"type": "Literal", "value": 10.5}
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

        # Uninitialized variable (only allowed for let)
        ast_dict = self.parse_code("let z;")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "VariableDeclaration",
                    "kind": "let",
                    "identifier": {"type": "Identifier", "name": "z"},
                    "init": None
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

    def test_basic_expressions(self):
        ast_dict = self.parse_code("1 + 2;")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "ExpressionStatement",
                    "expression": {
                        "type": "BinaryExpression",
                        "operator": "+",
                        "left": {"type": "Literal", "value": 1},
                        "right": {"type": "Literal", "value": 2}
                    }
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

        ast_dict = self.parse_code("a * b % c;")
        # (a * b) % c because of left-associativity and equal precedence between * and %
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "ExpressionStatement",
                    "expression": {
                        "type": "BinaryExpression",
                        "operator": "%",
                        "left": {
                            "type": "BinaryExpression",
                            "operator": "*",
                            "left": {"type": "Identifier", "name": "a"},
                            "right": {"type": "Identifier", "name": "b"}
                        },
                        "right": {"type": "Identifier", "name": "c"}
                    }
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

    def test_precedence_and_grouping(self):
        # 1 + 2 * 3 (multiplication is higher precedence)
        ast_dict = self.parse_code("1 + 2 * 3;")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "ExpressionStatement",
                    "expression": {
                        "type": "BinaryExpression",
                        "operator": "+",
                        "left": {"type": "Literal", "value": 1},
                        "right": {
                            "type": "BinaryExpression",
                            "operator": "*",
                            "left": {"type": "Literal", "value": 2},
                            "right": {"type": "Literal", "value": 3}
                        }
                    }
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

        # (1 + 2) * 3 (grouping forces addition first)
        ast_dict = self.parse_code("(1 + 2) * 3;")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "ExpressionStatement",
                    "expression": {
                        "type": "BinaryExpression",
                        "operator": "*",
                        "left": {
                            "type": "BinaryExpression",
                            "operator": "+",
                            "left": {"type": "Literal", "value": 1},
                            "right": {"type": "Literal", "value": 2}
                        },
                        "right": {"type": "Literal", "value": 3}
                    }
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

    def test_exponentiation_right_associativity(self):
        # 2 ** 3 ** 4 parses as 2 ** (3 ** 4)
        ast_dict = self.parse_code("2 ** 3 ** 4;")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "ExpressionStatement",
                    "expression": {
                        "type": "BinaryExpression",
                        "operator": "**",
                        "left": {"type": "Literal", "value": 2},
                        "right": {
                            "type": "BinaryExpression",
                            "operator": "**",
                            "left": {"type": "Literal", "value": 3},
                            "right": {"type": "Literal", "value": 4}
                        }
                    }
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

    def test_comparisons(self):
        operators = [">", "<", ">=", "<=", "==="]
        for op in operators:
            ast_dict = self.parse_code(f"x {op} y;")
            expected = {
                "type": "Program",
                "body": [
                    {
                        "type": "ExpressionStatement",
                        "expression": {
                            "type": "BinaryExpression",
                            "operator": op,
                            "left": {"type": "Identifier", "name": "x"},
                            "right": {"type": "Identifier", "name": "y"}
                        }
                    }
                ]
            }
            self.assertEqual(ast_dict, expected)

    def test_logical_operators(self):
        # a || b && c parses as a || (b && c) because && is higher precedence
        ast_dict = self.parse_code("a || b && c;")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "ExpressionStatement",
                    "expression": {
                        "type": "BinaryExpression",
                        "operator": "||",
                        "left": {"type": "Identifier", "name": "a"},
                        "right": {
                            "type": "BinaryExpression",
                            "operator": "&&",
                            "left": {"type": "Identifier", "name": "b"},
                            "right": {"type": "Identifier", "name": "c"}
                        }
                    }
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

    def test_unary_operators(self):
        ast_dict = self.parse_code("!true;")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "ExpressionStatement",
                    "expression": {
                        "type": "UnaryExpression",
                        "operator": "!",
                        "argument": {"type": "Literal", "value": True}
                    }
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

    def test_assignment_expressions(self):
        # x = y = 5 parses as x = (y = 5) due to right-associativity
        ast_dict = self.parse_code("x = y = 5;")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "ExpressionStatement",
                    "expression": {
                        "type": "AssignmentExpression",
                        "operator": "=",
                        "left": {"type": "Identifier", "name": "x"},
                        "right": {
                            "type": "AssignmentExpression",
                            "operator": "=",
                            "left": {"type": "Identifier", "name": "y"},
                            "right": {"type": "Literal", "value": 5}
                        }
                    }
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

    def test_block_statements(self):
        ast_dict = self.parse_code("{ let x = 1; const y = 2; }")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "BlockStatement",
                    "body": [
                        {
                            "type": "VariableDeclaration",
                            "kind": "let",
                            "identifier": {"type": "Identifier", "name": "x"},
                            "init": {"type": "Literal", "value": 1}
                        },
                        {
                            "type": "VariableDeclaration",
                            "kind": "const",
                            "identifier": {"type": "Identifier", "name": "y"},
                            "init": {"type": "Literal", "value": 2}
                        }
                    ]
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

    def test_if_statements(self):
        # 1. Simple if
        ast_dict = self.parse_code("if (x > 3) { let y = 1; }")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "IfStatement",
                    "test": {
                        "type": "BinaryExpression",
                        "operator": ">",
                        "left": {"type": "Identifier", "name": "x"},
                        "right": {"type": "Literal", "value": 3}
                    },
                    "consequent": {
                        "type": "BlockStatement",
                        "body": [
                            {
                                "type": "VariableDeclaration",
                                "kind": "let",
                                "identifier": {"type": "Identifier", "name": "y"},
                                "init": {"type": "Literal", "value": 1}
                            }
                        ]
                    },
                    "alternate": None
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

        # 2. If-else
        ast_dict = self.parse_code("if (false) {} else { x = 1; }")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "IfStatement",
                    "test": {"type": "Literal", "value": False},
                    "consequent": {"type": "BlockStatement", "body": []},
                    "alternate": {
                        "type": "BlockStatement",
                        "body": [
                            {
                                "type": "ExpressionStatement",
                                "expression": {
                                    "type": "AssignmentExpression",
                                    "operator": "=",
                                    "left": {"type": "Identifier", "name": "x"},
                                    "right": {"type": "Literal", "value": 1}
                                }
                            }
                        ]
                    }
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

        # 3. Else-if chain
        ast_dict = self.parse_code("if (a) {} else if (b) {} else {}")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "IfStatement",
                    "test": {"type": "Identifier", "name": "a"},
                    "consequent": {"type": "BlockStatement", "body": []},
                    "alternate": {
                        "type": "IfStatement",
                        "test": {"type": "Identifier", "name": "b"},
                        "consequent": {"type": "BlockStatement", "body": []},
                        "alternate": {"type": "BlockStatement", "body": []}
                    }
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

    def test_while_loops(self):
        ast_dict = self.parse_code("while (i < 5) { i = i + 1; }")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "WhileStatement",
                    "test": {
                        "type": "BinaryExpression",
                        "operator": "<",
                        "left": {"type": "Identifier", "name": "i"},
                        "right": {"type": "Literal", "value": 5}
                    },
                    "body": {
                        "type": "BlockStatement",
                        "body": [
                            {
                                "type": "ExpressionStatement",
                                "expression": {
                                    "type": "AssignmentExpression",
                                    "operator": "=",
                                    "left": {"type": "Identifier", "name": "i"},
                                    "right": {
                                        "type": "BinaryExpression",
                                        "operator": "+",
                                        "left": {"type": "Identifier", "name": "i"},
                                        "right": {"type": "Literal", "value": 1}
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

    def test_for_loops(self):
        # 1. Standard for loop
        ast_dict = self.parse_code("for (let i = 0; i < 5; i = i + 1) { }")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "ForStatement",
                    "init": {
                        "type": "VariableDeclaration",
                        "kind": "let",
                        "identifier": {"type": "Identifier", "name": "i"},
                        "init": {"type": "Literal", "value": 0}
                    },
                    "test": {
                        "type": "BinaryExpression",
                        "operator": "<",
                        "left": {"type": "Identifier", "name": "i"},
                        "right": {"type": "Literal", "value": 5}
                    },
                    "update": {
                        "type": "AssignmentExpression",
                        "operator": "=",
                        "left": {"type": "Identifier", "name": "i"},
                        "right": {
                            "type": "BinaryExpression",
                            "operator": "+",
                            "left": {"type": "Identifier", "name": "i"},
                            "right": {"type": "Literal", "value": 1}
                        }
                    },
                    "body": {"type": "BlockStatement", "body": []}
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

        # 2. Empty for loop
        ast_dict = self.parse_code("for (;;) {}")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "ForStatement",
                    "init": None,
                    "test": None,
                    "update": None,
                    "body": {"type": "BlockStatement", "body": []}
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

    def test_functions(self):
        # 1. Function declaration with parameters
        ast_dict = self.parse_code("function add(a, b) { return a + b; }")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "FunctionDeclaration",
                    "id": {"type": "Identifier", "name": "add"},
                    "params": [
                        {"type": "Identifier", "name": "a"},
                        {"type": "Identifier", "name": "b"}
                    ],
                    "body": {
                        "type": "BlockStatement",
                        "body": [
                            {
                                "type": "ReturnStatement",
                                "argument": {
                                    "type": "BinaryExpression",
                                    "operator": "+",
                                    "left": {"type": "Identifier", "name": "a"},
                                    "right": {"type": "Identifier", "name": "b"}
                                }
                            }
                        ]
                    }
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

        # 2. Return statement without argument
        ast_dict = self.parse_code("return;")
        expected = {
            "type": "Program",
            "body": [
                {
                    "type": "ReturnStatement",
                    "argument": None
                }
            ]
        }
        self.assertEqual(ast_dict, expected)

    def test_parser_errors(self):
        # 1. Missing semicolon on variable declaration
        with self.assertRaises(ParserError) as context:
            self.parse_code("let x = 5")
        self.assertEqual(context.exception.line, 1)
        self.assertEqual(context.exception.column, 10)  # EOF position
        self.assertIn("Expect ';'", context.exception.message)

        # 2. Missing closing parenthesis in grouping
        with self.assertRaises(ParserError) as context:
            self.parse_code("(1 + 2")
        self.assertIn("Expect ')'", context.exception.message)

        # 3. Missing closing brace in block statement
        with self.assertRaises(ParserError) as context:
            self.parse_code("{ let x = 1;")
        self.assertIn("Expect '}'", context.exception.message)

        # 4. Invalid assignment target (Literal)
        with self.assertRaises(ParserError) as context:
            self.parse_code("5 = x;")
        self.assertIn("Invalid assignment target", context.exception.message)

if __name__ == "__main__":
    unittest.main()
