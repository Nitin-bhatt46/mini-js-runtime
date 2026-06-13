import sys
from mini_js.ast import ASTNode
from mini_js.interpreter.environment import Environment, RunTimeError
from mini_js.runtime import Console

class ReturnValue(Exception):
    """Exception used for control flow execution to return values from functions."""
    def __init__(self, value: any):
        self.value = value


class JSFunction:
    """Runtime representation of a JavaScript function with a lexical closure."""
    
    def __init__(self, declaration, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def __call__(self, interpreter: "Interpreter", arguments: list[any]) -> any:
        env = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            env.define(param.name, arg, is_const=False)
            
        previous_env = interpreter.environment
        interpreter.environment = env
        try:
            interpreter.evaluate(self.declaration.body)
        except ReturnValue as ret:
            return ret.value
        finally:
            interpreter.environment = previous_env
        return None

class Interpreter:
    """Tree-walking interpreter for MiniJS using the Visitor Pattern."""
    
    def __init__(self):
        self.globals = Environment()
        # Initialize built-in console object from runtime package
        self.globals.define("console", Console(), is_const=True)
        self.environment = self.globals

    def evaluate(self, node: ASTNode) -> any:
        """Evaluates an AST node by dispatching to the appropriate visitor method."""
        method_name = f"visit_{node.type}"
        visitor = getattr(self, method_name, self.generic_visit)
        try:
            return visitor(node)
        except ReturnValue as e:
            raise e
        except RunTimeError as e:
            # If the error doesn't have coordinates, we can throw it upwards
            raise e
        except Exception as e:
            # Wrap any unhandled Python exceptions as RunTimeError
            raise RunTimeError(str(e))

    def generic_visit(self, node: ASTNode):
        raise NotImplementedError(f"No visit_{node.type} method defined.")

    def is_truthy(self, val) -> bool:
        """Javascript truthiness rule implementation."""
        if val is None:
            return False
        if val is False:
            return False
        if val == 0:  # Matches 0 and 0.0
            return False
        if val == "":
            return False
        return True

    def check_number_operands(self, operator: str, left: any, right: any) -> None:
        """Validates that both operands are numbers."""
        if (isinstance(left, (int, float)) and not isinstance(left, bool) and
                isinstance(right, (int, float)) and not isinstance(right, bool)):
            return
        raise RunTimeError(f"Operands for '{operator}' must be numbers")

    # --- Visitor Methods ---

    def visit_Program(self, node) -> any:
        result = None
        for statement in node.body:
            result = self.evaluate(statement)
        return result

    def visit_BlockStatement(self, node) -> any:
        previous_env = self.environment
        self.environment = Environment(previous_env)
        try:
            result = None
            for statement in node.body:
                result = self.evaluate(statement)
            return result
        finally:
            self.environment = previous_env

    def visit_IfStatement(self, node) -> any:
        test_val = self.evaluate(node.test)
        if self.is_truthy(test_val):
            return self.evaluate(node.consequent)
        elif node.alternate is not None:
            return self.evaluate(node.alternate)
        return None

    def visit_WhileStatement(self, node) -> any:
        result = None
        while self.is_truthy(self.evaluate(node.test)):
            result = self.evaluate(node.body)
        return result

    def visit_ForStatement(self, node) -> any:
        previous_env = self.environment
        self.environment = Environment(previous_env)
        try:
            if node.init is not None:
                self.evaluate(node.init)
            
            result = None
            while True:
                if node.test is not None:
                    test_val = self.evaluate(node.test)
                    if not self.is_truthy(test_val):
                        break
                
                result = self.evaluate(node.body)
                
                if node.update is not None:
                    self.evaluate(node.update)
            return result
        finally:
            self.environment = previous_env

    def visit_VariableDeclaration(self, node) -> None:
        val = None
        if node.init is not None:
            val = self.evaluate(node.init)
        
        self.environment.define(node.identifier.name, val, node.kind == "const")
        return None

    def visit_AssignmentExpression(self, node) -> any:
        val = self.evaluate(node.right)
        from mini_js.ast import Identifier, IndexExpression
        if isinstance(node.left, Identifier):
            self.environment.assign(node.left.name, val)
        elif isinstance(node.left, IndexExpression):
            obj = self.evaluate(node.left.object)
            idx = self.evaluate(node.left.property)
            if isinstance(idx, float) and idx.is_integer():
                idx = int(idx)
            if isinstance(obj, list):
                if not isinstance(idx, int):
                    raise RunTimeError("TypeError: Array index must be an integer")
                if 0 <= idx < len(obj):
                    obj[idx] = val
                elif idx == len(obj):
                    obj.append(val)
                else:
                    while len(obj) < idx:
                        obj.append(None)
                    obj.append(val)
            elif isinstance(obj, dict):
                obj[idx] = val
            else:
                raise RunTimeError(f"Cannot set property of non-object: {obj}")
        return val

    def visit_UnaryExpression(self, node) -> any:
        val = self.evaluate(node.argument)
        if node.operator == "!":
            return not self.is_truthy(val)
        if node.operator == "-":
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                return -val
            if val is True: return -1
            if val is False or val is None: return 0
            if isinstance(val, str):
                try:
                    if "." in val or "e" in val.lower():
                        return -float(val)
                    return -int(val)
                except ValueError:
                    raise RunTimeError(f"Cannot negate non-numeric string: '{val}'")
            raise RunTimeError(f"Operand for '-' must be a number, got: {val}")
        if node.operator == "+":
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                return +val
            if val is True: return 1
            if val is False or val is None: return 0
            if isinstance(val, str):
                try:
                    if "." in val or "e" in val.lower():
                        return float(val)
                    return int(val)
                except ValueError:
                    raise RunTimeError(f"Cannot convert non-numeric string to number: '{val}'")
            raise RunTimeError(f"Operand for '+' must be a number, got: {val}")
        raise RunTimeError(f"Unknown unary operator '{node.operator}'")


    def visit_BinaryExpression(self, node) -> any:
        # Short-circuit logical operators first
        if node.operator == "&&":
            left_val = self.evaluate(node.left)
            if not self.is_truthy(left_val):
                return left_val
            return self.evaluate(node.right)

        if node.operator == "||":
            left_val = self.evaluate(node.left)
            if self.is_truthy(left_val):
                return left_val
            return self.evaluate(node.right)

        # Evaluate both sides for arithmetic and comparison
        left_val = self.evaluate(node.left)
        right_val = self.evaluate(node.right)

        # Addition / Concatenation
        if node.operator == "+":
            if isinstance(left_val, str) or isinstance(right_val, str):
                def js_str(v) -> str:
                    if v is True: return "true"
                    if v is False: return "false"
                    if v is None: return "null"
                    return str(v)
                return js_str(left_val) + js_str(right_val)
            
            self.check_number_operands(node.operator, left_val, right_val)
            return left_val + right_val

        # Subtraction
        if node.operator == "-":
            self.check_number_operands(node.operator, left_val, right_val)
            return left_val - right_val

        # Multiplication
        if node.operator == "*":
            self.check_number_operands(node.operator, left_val, right_val)
            return left_val * right_val

        # Division
        if node.operator == "/":
            self.check_number_operands(node.operator, left_val, right_val)
            if right_val == 0:
                raise RunTimeError("Division by zero")
            return left_val / right_val

        # Modulo
        if node.operator == "%":
            self.check_number_operands(node.operator, left_val, right_val)
            if right_val == 0:
                raise RunTimeError("Modulo by zero")
            return left_val % right_val

        # Exponentiation
        if node.operator == "**":
            self.check_number_operands(node.operator, left_val, right_val)
            return left_val ** right_val

        # Comparisons (<, >, <=, >=)
        if node.operator in ("<", ">", "<=", ">="):
            # Check if both are numbers, or if both are strings
            if (type(left_val) is type(right_val) and 
                    isinstance(left_val, (int, float, str)) and 
                    not isinstance(left_val, bool)):
                pass
            elif (isinstance(left_val, (int, float)) and not isinstance(left_val, bool) and
                  isinstance(right_val, (int, float)) and not isinstance(right_val, bool)):
                pass
            else:
                raise RunTimeError(
                    f"Invalid comparison between {type(left_val).__name__} and {type(right_val).__name__}"
                )

            if node.operator == "<": return left_val < right_val
            if node.operator == ">": return left_val > right_val
            if node.operator == "<=": return left_val <= right_val
            if node.operator == ">=": return left_val >= right_val

        # Strict Equality (===)
        if node.operator == "===":
            if isinstance(left_val, bool) != isinstance(right_val, bool):
                return False
            if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
                return left_val == right_val
            return type(left_val) is type(right_val) and left_val == right_val

        # Loose Equality (==)
        if node.operator == "==":
            return left_val == right_val

        # Inequality (!=)
        if node.operator == "!=":
            return left_val != right_val

        raise RunTimeError(f"Unknown binary operator '{node.operator}'")

    def visit_Literal(self, node) -> any:
        return node.value

    def visit_Identifier(self, node) -> any:
        return self.environment.get(node.name)

    def visit_ExpressionStatement(self, node) -> any:
        return self.evaluate(node.expression)

    def visit_MemberExpression(self, node) -> any:
        obj = self.evaluate(node.object)
        property_name = node.property.name
        
        if isinstance(obj, list):
            if property_name == "length":
                return len(obj)
            elif property_name == "push":
                return lambda *args: obj.extend(args) or len(obj)
            elif property_name == "pop":
                return lambda: obj.pop() if obj else None
            elif property_name == "reverse":
                return lambda: obj.reverse() or obj
            elif property_name == "includes":
                return lambda val: val in obj
            elif property_name == "indexOf":
                def js_index_of(val):
                    try:
                        return obj.index(val)
                    except ValueError:
                        return -1
                return js_index_of
            elif property_name == "concat":
                def js_concat(*args):
                    new_list = list(obj)
                    for arg in args:
                        if isinstance(arg, list):
                            new_list.extend(arg)
                        else:
                            new_list.append(arg)
                    return new_list
                return js_concat
            elif property_name == "join":
                def js_join(separator=","):
                    def item_to_str(item):
                        if item is True: return "true"
                        if item is False: return "false"
                        if item is None: return ""
                        if isinstance(item, list):
                            return ",".join(item_to_str(subitem) for subitem in item)
                        return str(item)
                    return separator.join(item_to_str(item) for item in obj)
                return js_join
        
        if isinstance(obj, str):
            if property_name == "length":
                return len(obj)
            elif property_name == "split":
                def js_split(separator=None):
                    if separator is None:
                        return [obj]
                    if separator == "":
                        return list(obj)
                    return obj.split(separator)
                return js_split
            elif property_name == "join":
                def js_join(arg):
                    if isinstance(arg, list):
                        def item_to_str(item):
                            if item is True: return "true"
                            if item is False: return "false"
                            if item is None: return ""
                            return str(item)
                        return obj.join(item_to_str(item) for item in arg)
                    return obj.join(str(arg))
                return js_join
            elif property_name == "replace":
                def js_replace(search, replacement):
                    return obj.replace(str(search), str(replacement), 1)
                return js_replace
            elif property_name == "substring":
                def js_substring(start=0, end=None):
                    length = len(obj)
                    if start is None or not isinstance(start, (int, float)):
                        start = 0
                    if end is None:
                        end = length
                    elif not isinstance(end, (int, float)):
                        end = length
                    start = int(start)
                    end = int(end)
                    if start < 0: start = 0
                    if end < 0: end = 0
                    if start > length: start = length
                    if end > length: end = length
                    if start > end:
                        start, end = end, start
                    return obj[start:end]
                return js_substring
            elif property_name == "slice":
                def js_slice(start=0, end=None):
                    length = len(obj)
                    if start is None:
                        start = 0
                    else:
                        start = int(start)
                        if start < 0:
                            start = max(0, length + start)
                        else:
                            start = min(length, start)
                    if end is None:
                        end = length
                    else:
                        end = int(end)
                        if end < 0:
                            end = max(0, length + end)
                        else:
                            end = min(length, end)
                    if start >= end:
                        return ""
                    return obj[start:end]
                return js_slice
            elif property_name == "trim":
                return lambda: obj.strip()
            elif property_name == "toUpperCase":
                return lambda: obj.upper()
            elif property_name == "toLowerCase":
                return lambda: obj.lower()
            elif property_name == "includes":
                def js_includes(search, position=0):
                    pos = int(position) if position is not None else 0
                    if pos < 0:
                        pos = 0
                    return str(search) in obj[pos:]
                return js_includes
            elif property_name == "startsWith":
                def js_starts_with(search, position=0):
                    pos = int(position) if position is not None else 0
                    if pos < 0:
                        pos = 0
                    return obj.startswith(str(search), pos)
                return js_starts_with
            elif property_name == "endsWith":
                def js_ends_with(search, end_pos=None):
                    length = len(obj)
                    if end_pos is None:
                        end_pos = length
                    else:
                        end_pos = int(end_pos)
                    if end_pos < 0:
                        end_pos = 0
                    elif end_pos > length:
                        end_pos = length
                    return obj[:end_pos].endswith(str(search))
                return js_ends_with
            elif property_name == "indexOf":
                def js_index_of(search, position=0):
                    pos = int(position) if position is not None else 0
                    if pos < 0:
                        pos = 0
                    return obj.find(str(search), pos)
                return js_index_of

        if hasattr(obj, "members") and isinstance(obj.members, dict):
            if property_name in obj.members:
                return obj.members[property_name]
        elif isinstance(obj, dict):
            if property_name in obj:
                return obj[property_name]
                
        raise RunTimeError(f"Cannot read property '{property_name}' of {obj}")

    def visit_CallExpression(self, node) -> any:
        callee_val = self.evaluate(node.callee)
        args_val = [self.evaluate(arg) for arg in node.arguments]
        
        if isinstance(callee_val, JSFunction):
            return callee_val(self, args_val)
        elif callable(callee_val):
            return callee_val(*args_val)
            
        raise RunTimeError("TypeError: callee is not a function")

    def visit_FunctionDeclaration(self, node) -> None:
        func = JSFunction(node, self.environment)
        self.environment.define(node.id.name, func, is_const=False)
        return None

    def visit_ReturnStatement(self, node) -> None:
        val = None
        if node.argument is not None:
            val = self.evaluate(node.argument)
        raise ReturnValue(val)

    def visit_ArrayLiteral(self, node) -> list[any]:
        return [self.evaluate(el) for el in node.elements]

    def visit_IndexExpression(self, node) -> any:
        obj = self.evaluate(node.object)
        idx = self.evaluate(node.property)
        if isinstance(idx, float) and idx.is_integer():
            idx = int(idx)
        if isinstance(obj, list):
            if not isinstance(idx, int):
                raise RunTimeError("TypeError: Array index must be an integer")
            if 0 <= idx < len(obj):
                return obj[idx]
            return None
        elif isinstance(obj, dict):
            return obj.get(idx, None)
        elif isinstance(obj, str):
            if isinstance(idx, int) and 0 <= idx < len(obj):
                return obj[idx]
            return None
        raise RunTimeError(f"Cannot read property of non-object: {obj}")
