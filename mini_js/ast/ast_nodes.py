import json


class ASTNode:
    """Base class for all AST nodes."""
    
    def to_dict(self) -> dict:
        """Returns a dictionary representation of the node for serialization and testing."""
        raise NotImplementedError("Each AST node must implement 'to_dict'")

    def __repr__(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class Program(ASTNode):
    """Represents the root program node containing statements."""
    
    def __init__(self, body: list[ASTNode]):
        self.type = "Program"
        self.body = body

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "body": [node.to_dict() for node in self.body]
        }


class VariableDeclaration(ASTNode):
    """Represents variable declarations (e.g. let x = 5; or const y = 10;)."""
    
    def __init__(self, kind: str, identifier: "Identifier", init: ASTNode | None):
        self.type = "VariableDeclaration"
        self.kind = kind  # "let" or "const"
        self.identifier = identifier
        self.init = init

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "kind": self.kind,
            "identifier": self.identifier.to_dict(),
            "init": self.init.to_dict() if self.init else None
        }


class AssignmentExpression(ASTNode):
    """Represents assignments (e.g. x = y)."""
    
    def __init__(self, operator: str, left: ASTNode, right: ASTNode):
        self.type = "AssignmentExpression"
        self.operator = operator  # "="
        self.left = left
        self.right = right

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "operator": self.operator,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }


class BinaryExpression(ASTNode):
    """Represents binary operations including arithmetic, comparisons, and logicals."""
    
    def __init__(self, operator: str, left: ASTNode, right: ASTNode):
        self.type = "BinaryExpression"
        self.operator = operator
        self.left = left
        self.right = right

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "operator": self.operator,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }


class UnaryExpression(ASTNode):
    """Represents unary operators (e.g. !x)."""
    
    def __init__(self, operator: str, argument: ASTNode):
        self.type = "UnaryExpression"
        self.operator = operator
        self.argument = argument

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "operator": self.operator,
            "argument": self.argument.to_dict()
        }


class Identifier(ASTNode):
    """Represents a variable identifier name."""
    
    def __init__(self, name: str):
        self.type = "Identifier"
        self.name = name

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "name": self.name
        }


class Literal(ASTNode):
    """Represents numeric, string, boolean, or null literals."""
    
    def __init__(self, value):
        self.type = "Literal"
        self.value = value

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "value": self.value
        }


class BlockStatement(ASTNode):
    """Represents block statements (e.g. { let x = 1; })."""
    
    def __init__(self, body: list[ASTNode]):
        self.type = "BlockStatement"
        self.body = body

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "body": [node.to_dict() for node in self.body]
        }


class ExpressionStatement(ASTNode):
    """Wraps an expression as a standalone statement."""
    
    def __init__(self, expression: ASTNode):
        self.type = "ExpressionStatement"
        self.expression = expression

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "expression": self.expression.to_dict()
        }


class CallExpression(ASTNode):
    """Represents a function call (e.g. func(arg1, arg2))."""
    
    def __init__(self, callee: ASTNode, arguments: list[ASTNode]):
        self.type = "CallExpression"
        self.callee = callee
        self.arguments = arguments

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "callee": self.callee.to_dict(),
            "arguments": [arg.to_dict() for arg in self.arguments]
        }


class MemberExpression(ASTNode):
    """Represents a member property access (e.g. obj.property)."""
    
    def __init__(self, object_: ASTNode, property_: Identifier):
        self.type = "MemberExpression"
        self.object = object_
        self.property = property_

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "object": self.object.to_dict(),
            "property": self.property.to_dict()
        }


class IfStatement(ASTNode):
    """Represents conditional statements (if ... else if ... else)."""
    
    def __init__(self, test: ASTNode, consequent: ASTNode, alternate: ASTNode | None):
        self.type = "IfStatement"
        self.test = test
        self.consequent = consequent
        self.alternate = alternate

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "test": self.test.to_dict(),
            "consequent": self.consequent.to_dict(),
            "alternate": self.alternate.to_dict() if self.alternate else None
        }


class WhileStatement(ASTNode):
    """Represents while loops (while (condition) statement)."""
    
    def __init__(self, test: ASTNode, body: ASTNode):
        self.type = "WhileStatement"
        self.test = test
        self.body = body

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "test": self.test.to_dict(),
            "body": self.body.to_dict()
        }


class ForStatement(ASTNode):
    """Represents for loops (for (init; test; update) statement)."""
    
    def __init__(self, init: ASTNode | None, test: ASTNode | None, update: ASTNode | None, body: ASTNode):
        self.type = "ForStatement"
        self.init = init
        self.test = test
        self.update = update
        self.body = body

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "init": self.init.to_dict() if self.init else None,
            "test": self.test.to_dict() if self.test else None,
            "update": self.update.to_dict() if self.update else None,
            "body": self.body.to_dict()
        }


class FunctionDeclaration(ASTNode):
    """Represents a function definition (function name(params) { body })."""
    
    def __init__(self, id_: "Identifier", params: list["Identifier"], body: "BlockStatement"):
        self.type = "FunctionDeclaration"
        self.id = id_
        self.params = params
        self.body = body

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "id": self.id.to_dict(),
            "params": [p.to_dict() for p in self.params],
            "body": self.body.to_dict()
        }


class ReturnStatement(ASTNode):
    """Represents return statements (return argument;)."""
    
    def __init__(self, argument: ASTNode | None):
        self.type = "ReturnStatement"
        self.argument = argument

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "argument": self.argument.to_dict() if self.argument else None
        }


class ArrayLiteral(ASTNode):
    """Represents an array literal (e.g. [1, 2, 3])."""
    
    def __init__(self, elements: list[ASTNode]):
        self.type = "ArrayLiteral"
        self.elements = elements

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "elements": [el.to_dict() for el in self.elements]
        }


class IndexExpression(ASTNode):
    """Represents index property access (e.g. object[property])."""
    
    def __init__(self, object_: ASTNode, property_: ASTNode):
        self.type = "IndexExpression"
        self.object = object_
        self.property = property_

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "object": self.object.to_dict(),
            "property": self.property.to_dict()
        }
