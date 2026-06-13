# MiniJS

A lightweight JavaScript runtime implemented in Python.

MiniJS provides a minimal JavaScript execution environment built from first principles. The runtime includes a lexer, parser, abstract syntax tree (AST), interpreter, and runtime system capable of executing a subset of JavaScript.

## Supported Features

* Variable declarations (`let`, `const`)
* Conditional statements (`if`, `else`)
* Loops (`for`, `while`)
* Functions
* Arrays
* Strings
* `console.log`
* Basic `Math` support

## Installation

```bash
git clone https://github.com/Nitin-bhatt46/mini-js-runtime.git

cd mini_js

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

## Usage

```bash
python main.py example.js
```

Example:

```javascript
const message = "Hello, MiniJS";

console.log(message);
```

## Testing

```bash
pytest
```

## Architecture

```text
Source
  │
  ▼
Lexer
  │
  ▼
Parser
  │
  ▼
AST
  │
  ▼
Interpreter
  │
  ▼
Runtime
```

## Project Structure

```text
mini_js/
├── lexer/
├── parser/
├── interpreter/
├── runtime/
├── tests/
├── main.py
└── requirements.txt
```

## Goals

MiniJS is intended as an educational implementation of a JavaScript runtime. The project focuses on clarity and simplicity rather than complete JavaScript compatibility.

## Contributing

Contributions are welcome. Please open an issue to discuss major changes before submitting a pull request.

## License

MIT

## Author

Nitin Bhatt
