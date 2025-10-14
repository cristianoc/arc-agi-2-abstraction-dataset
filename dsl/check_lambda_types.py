#!/usr/bin/env python3
"""
Extract typed-operation declarations and lambda representations from
ARC abstraction notes, synthesise Python stubs, and run mypy against
the generated module.  This flags mismatches such as undefined helpers,
incorrect arity, or missing arguments in the pseudo-code.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple

TYPING_IMPORTS = {"Any", "Dict", "Iterable", "Iterator", "List", "Optional", "Sequence", "Set", "Tuple"}
BUILTIN_MAP = {
    "Bool": "bool",
    "Boolean": "bool",
    "Int": "int",
    "Integer": "int",
    "Float": "float",
    "Str": "str",
    "String": "str",
}
SPECIAL_ALIAS_MAP = {
    "Segment": "Tuple[Any, ...]",
    "Axis": "Tuple[int, int]",
    "AxisColumn": "int",
}

SIG_PATTERN = re.compile(r"- `([^`]+)`")
LAMBDA_PATTERN = re.compile(r"## Lambda Representation.*?```(?:python)?\n(.*?)```", re.S | re.I)
TOKEN_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def collect_abstraction_files(paths: Sequence[str]) -> List[Path]:
    files: List[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            files.extend(sorted(path.rglob("abstractions.md")))
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError(f"No such file or directory: {path}")
    return files


def normalize_type(expr: str) -> str:
    expr = expr.strip()
    if not expr:
        return "Any"

    # Handle parenthetical groups.
    if expr.startswith("(") and expr.endswith(")"):
        expr = expr[1:-1].strip()
        if not expr:
            return "Any"
        return normalize_type(expr)

    if expr.startswith("List "):
        return f"List[{normalize_type(expr[5:])}]"
    if expr.startswith("Set "):
        return f"Set[{normalize_type(expr[4:])}]"
    if expr.startswith("Optional "):
        return f"Optional[{normalize_type(expr[9:])}]"
    if expr.startswith("Sequence "):
        return f"Sequence[{normalize_type(expr[9:])}]"
    if expr.startswith("Iterable "):
        return f"Iterable[{normalize_type(expr[9:])}]"
    if expr.startswith("Iterator "):
        return f"Iterator[{normalize_type(expr[9:])}]"
    if expr.startswith("Dict "):
        rest = expr[5:]
        if "->" in rest:
            key_str, value_str = rest.split("->", 1)
            return f"Dict[{normalize_type(key_str)}, {normalize_type(value_str)}]"
    if expr.startswith("Tuple "):
        rest = expr[6:]
        parts = [normalize_type(part.strip()) for part in rest.split(",")]
        return f"Tuple[{', '.join(parts)}]"

    if "," in expr:
        parts = [normalize_type(part.strip()) for part in expr.split(",")]
        return f"Tuple[{', '.join(parts)}]"

    return expr.replace(" ", "")


def extract_type_tokens(type_str: str) -> Set[str]:
    return set(TOKEN_PATTERN.findall(type_str))


def parse_typed_operations(text: str) -> Tuple[Dict[str, Tuple[List[str], str]], Set[str]]:
    section_start = text.find("## DSL Structure")
    if section_start == -1:
        return {}, set()

    typed_ops: Dict[str, Tuple[List[str], str]] = {}
    tokens: Set[str] = set()

    for match in SIG_PATTERN.finditer(text, section_start):
        signature = match.group(1)
        if ":" not in signature:
            continue
        name_part, rest = signature.split(":", 1)
        func_name = name_part.strip()
        if not func_name:
            continue

        domain_codomain = [part.strip() for part in rest.split("->")]
        if len(domain_codomain) < 2:
            continue

        domain_parts = domain_codomain[:-1]
        arg_types: List[str] = []
        for domain in domain_parts:
            if not domain:
                continue
            # Split on the cartesian product symbol.
            factors = [piece.strip() for piece in domain.split("×")]
            for factor in factors:
                if factor:
                    normalized = normalize_type(factor)
                    arg_types.append(normalized)
                    tokens.update(extract_type_tokens(normalized))

        codomain = domain_codomain[-1]
        normalized_return = normalize_type(codomain)
        tokens.update(extract_type_tokens(normalized_return))

        typed_ops[func_name] = (arg_types, normalized_return)

    return typed_ops, tokens


def parse_lambda_block(text: str) -> Tuple[str, Set[str]]:
    match = LAMBDA_PATTERN.search(text)
    if not match:
        return "", set()
    code = match.group(1).strip()
    if not code:
        return "", set()
    tokens = set(TOKEN_PATTERN.findall(code))
    return code, tokens


def build_stub_module(
    func_signatures: Dict[str, Tuple[List[str], str]],
    identifiers: Set[str],
    lambda_code: str,
) -> str:
    header_lines = [
        "from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Set, Tuple",
        "",
    ]

    alias_lines: List[str] = []
    for token in sorted(identifiers):
        if token in TYPING_IMPORTS:
            continue
        if token in {"from", "import", "def", "return", "if", "elif", "else", "for", "while"}:
            continue
        if token in {"True", "False", "None"}:
            continue
        if token in SPECIAL_ALIAS_MAP:
            alias_lines.append(f"{token} = {SPECIAL_ALIAS_MAP[token]}")
        elif token in BUILTIN_MAP:
            alias_lines.append(f"{token} = {BUILTIN_MAP[token]}")
        elif token[0].isupper():
            alias_lines.append(f"{token} = Any")

    if alias_lines:
        header_lines.extend(alias_lines)
        header_lines.append("")

    stub_lines: List[str] = []
    for name, (arg_types, return_type) in sorted(func_signatures.items()):
        params = ", ".join(f"arg{i}: {arg_types[i]}" for i in range(len(arg_types)))
        stub_lines.append(f"def {name}({params}) -> {return_type}:")
        stub_lines.append("    raise NotImplementedError")
        stub_lines.append("")

    module_parts = header_lines + stub_lines
    if lambda_code:
        module_parts.append(lambda_code)
        module_parts.append("")

    return "\n".join(module_parts)


def run_mypy_on_modules(modules: Dict[Path, str]) -> Tuple[int, str]:
    with tempfile.TemporaryDirectory(prefix="dsl_lambda_typecheck_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        file_paths: List[Path] = []
        for source_path, code in modules.items():
            parent = source_path.parent.name or "root"
            dest = tmp_path / f"{parent}_{source_path.stem}_lambda_stub.py"
            dest.write_text(code)
            file_paths.append(dest)

        cmd = ["mypy", "--hide-error-context", "--no-color-output"] + [str(p) for p in file_paths]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        output = proc.stdout + proc.stderr
        return proc.returncode, output


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description="Type-check lambda representations against declared DSL signatures.")
    parser.add_argument("paths", nargs="+", help="Abstraction files or directories to analyse.")
    args = parser.parse_args(argv)

    abstraction_files = collect_abstraction_files(args.paths)
    if not abstraction_files:
        print("No abstraction files found.", file=sys.stderr)
        return 1

    modules: Dict[Path, str] = {}

    for file_path in abstraction_files:
        text = file_path.read_text()
        typed_ops, type_tokens = parse_typed_operations(text)
        lambda_code, lambda_tokens = parse_lambda_block(text)

        if not typed_ops or not lambda_code:
            continue

        identifiers = type_tokens | lambda_tokens
        module_source = build_stub_module(typed_ops, identifiers, lambda_code)
        modules[file_path] = module_source

    if not modules:
        print("No lambda representations found in the provided files.", file=sys.stderr)
        return 1

    exit_code, output = run_mypy_on_modules(modules)
    sys.stdout.write(output)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
