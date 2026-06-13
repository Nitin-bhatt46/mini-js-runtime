# MiniJS

A lightweight JavaScript Runtime written entirely in Python.

## Features

Supports:

* let
* const
* if/else
* for loops
* while loops
* functions
* arrays
* strings
* console.log()
* Math object

## Requirements

Python 3.10+

## Installation

```bash
gh repo clone Nitin-bhatt46/mini-js-runtime

cd mini_js

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```

## Running

```bash
python main.py example.js
```

## Running Tests

```bash
pytest
```

## Architecture

Lexer
→ Parser
→ AST
→ Interpreter
→ Runtime

## Author

Nitin Bhatt
