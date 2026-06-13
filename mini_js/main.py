import sys
import argparse
from mini_js.lexer import Lexer, LexerError
from mini_js.parser import Parser, ParserError
from mini_js.interpreter import Interpreter, RunTimeError

def format_tokens(tokens) -> str:
    """Formats a list of tokens into a pretty-printed table string."""
    header = f"{'Type':<15} | {'Value':<25} | {'Line':<6} | {'Column':<6}"
    separator = "-" * len(header)
    rows = []
    for token in tokens:
        val = repr(token.value)
        if len(val) > 25:
            val = val[:22] + "..."
        rows.append(f"{token.type.name:<15} | {val:<25} | {token.line:<6} | {token.column:<6}")
    return "\n".join([header, separator] + rows)

def print_error_with_caret(error_type: str, message: str, line: int, column: int, source_code: str):
    """Prints a styled compilation error with a source code preview and a caret indicator."""
    print(f"\033[91m{error_type}: {message} (line {line}, col {column})\033[0m", file=sys.stderr)
    lines = source_code.splitlines()
    if 1 <= line <= len(lines):
        error_line = lines[line - 1]
        print(f"  {error_line}", file=sys.stderr)
        
        # Build caret spacing matching tabs in the original line
        spacing = []
        for char in error_line[:column - 1]:
            if char == "\t":
                spacing.append("\t")
            else:
                spacing.append(" ")
        print(f"  {''.join(spacing)}^", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        description="MiniJS Compiler & Interpreter CLI (Phase 3)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mini_js/main.py --code "let a = 5; let b = 10; console.log(a + b);"
  python mini_js/main.py --ast --code "let x = 42;"
  python mini_js/main.py path/to/file.js
"""
    )
    parser.add_argument(
        "file", 
        nargs="?", 
        help="JavaScript file to execute. If not provided, reads from stdin."
    )
    parser.add_argument(
        "-c", "--code", 
        help="Direct JavaScript code string to execute."
    )
    parser.add_argument(
        "-t", "--tokens",
        action="store_true",
        help="Only display tokenized output instead of executing."
    )
    parser.add_argument(
        "-a", "--ast",
        action="store_true",
        help="Only display the AST representation JSON instead of executing."
    )
    
    args = parser.parse_args()
    
    source_code = ""
    
    if args.code is not None:
        source_code = args.code
    elif args.file is not None:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                source_code = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if not sys.stdin.isatty():
            source_code = sys.stdin.read()
        else:
            # Interactive mode with no args: run the default demonstration execution
            print("No input provided. Running default MiniJS execution...\n")
            source_code = 'let a = 5;\nlet b = 10;\nconsole.log(a + b);'
            print("Source Code:")
            print("---")
            print(source_code)
            print("---\n")

    if not source_code.strip():
        print("No source code to process.", file=sys.stderr)
        sys.exit(0)

    # Lexing Phase
    try:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
    except LexerError as e:
        print_error_with_caret("LexerError", e.message, e.line, e.column, source_code)
        sys.exit(1)

    if args.tokens:
        print(format_tokens(tokens))
        sys.exit(0)

    # Parsing Phase
    try:
        parser_inst = Parser(tokens)
        ast = parser_inst.parse()
    except ParserError as e:
        print_error_with_caret("ParserError", e.message, e.line, e.column, source_code)
        sys.exit(1)

    if args.ast:
        print(repr(ast))
        sys.exit(0)

    # Interpreting Phase
    try:
        interpreter = Interpreter()
        interpreter.evaluate(ast)
    except RunTimeError as e:
        print(f"\033[91mRuntime Error: {e.message}\033[0m", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
