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
import ast
from typing import Callable, Dict, Iterable, List, Sequence, Set, Tuple, TypeVar

TYPING_IMPORTS = {"Any", "Dict", "Iterable", "Iterator", "List", "Optional", "Sequence", "Set", "Tuple"}
TYPING_IMPORTS.update({"Callable", "TypeVar"})
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


ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div)


def is_pure_expr(node: ast.AST) -> bool:
    if isinstance(node, ast.Name):
        return True
    if isinstance(node, ast.Call):
        if not is_pure_expr(node.func):
            return False
        return all(is_pure_expr(arg) for arg in node.args) and all(is_pure_expr(kw.value) for kw in node.keywords)
    if isinstance(node, ast.Attribute):
        return is_pure_expr(node.value)
    if isinstance(node, ast.Tuple):
        return all(is_pure_expr(elt) for elt in node.elts)
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, ast.BinOp):
        return isinstance(node.op, ALLOWED_BINOPS) and is_pure_expr(node.left) and is_pure_expr(node.right)
    if isinstance(node, ast.Compare):
        return is_pure_expr(node.left) and all(is_pure_expr(comp) for comp in node.comparators)
    if isinstance(node, ast.BoolOp):
        return all(is_pure_expr(value) for value in node.values)
    if isinstance(node, ast.Subscript):
        return is_pure_expr(node.value) and is_pure_expr(node.slice)
    if isinstance(node, ast.UnaryOp):
        return is_pure_expr(node.operand)
    if isinstance(node, ast.ListComp):
        if not is_pure_expr(node.elt):
            return False
        for comp in node.generators:
            if comp.is_async:
                return False
            if not is_pure_expr(comp.iter):
                return False
            if comp.ifs and not all(is_pure_expr(test) for test in comp.ifs):
                return False
        return True
    if isinstance(node, ast.GeneratorExp):
        if not is_pure_expr(node.elt):
            return False
        for comp in node.generators:
            if comp.is_async:
                return False
            if not is_pure_expr(comp.iter):
                return False
            if comp.ifs and not all(is_pure_expr(test) for test in comp.ifs):
                return False
        return True
    if isinstance(node, ast.Lambda):
        if node.args.defaults or node.args.kw_defaults:
            return False
        if node.args.vararg or node.args.kwarg:
            return False
        return is_pure_expr(node.body)
    return False


def _validate_guard_if(stmt: ast.If, source_path: Path, violations: List[str]) -> None:
    current = stmt
    while True:
        if len(current.body) != 1 or not isinstance(current.body[0], ast.Return):
            violations.append(f"{source_path}:{current.lineno}: guard if must immediately return")
            return
        ret_stmt = current.body[0]
        if ret_stmt.value is not None and not is_pure_expr(ret_stmt.value):
            violations.append(f"{source_path}:{ret_stmt.lineno}: guard return expression contains disallowed constructs")
            return
        if not current.orelse:
            return
        if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
            current = current.orelse[0]
            continue
        if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.Return):
            ret_stmt = current.orelse[0]
            if ret_stmt.value is not None and not is_pure_expr(ret_stmt.value):
                violations.append(f"{source_path}:{ret_stmt.lineno}: guard return expression contains disallowed constructs")
            return
        violations.append(f"{source_path}:{current.lineno}: guard if else branch must return directly")
        return


def validate_lambda_purity(lambda_code: str, source_path: Path) -> List[str]:
    violations: List[str] = []
    try:
        tree = ast.parse(lambda_code, filename=str(source_path))
    except SyntaxError as exc:
        violations.append(f"{source_path}: failed to parse lambda block ({exc})")
        return violations

    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            violations.append(f"{source_path}:{getattr(node, 'lineno', '?')}: disallowed top-level statement {type(node).__name__}")
            continue
        if node.decorator_list:
            violations.append(f"{source_path}:{node.lineno}: decorators are not allowed in lambda summaries")
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                if stmt.decorator_list:
                    violations.append(f"{source_path}:{stmt.lineno}: decorators are not allowed in helper definitions")
                    continue
                for inner in stmt.body:
                    if isinstance(inner, ast.Assign):
                        if len(inner.targets) != 1:
                            violations.append(f"{source_path}:{inner.lineno}: multiple assignment targets not allowed")
                            continue
                        target = inner.targets[0]
                        if isinstance(target, ast.Name):
                            allowed_target = True
                        elif isinstance(target, (ast.Tuple, ast.List)):
                            allowed_target = all(isinstance(elt, ast.Name) for elt in target.elts)
                        else:
                            allowed_target = False
                        if not allowed_target:
                            violations.append(f"{source_path}:{inner.lineno}: helper assignments must target names or tuples of names")
                        elif not is_pure_expr(inner.value):
                            violations.append(f"{source_path}:{inner.lineno}: helper assignment uses disallowed expression")
                    elif isinstance(inner, ast.Return):
                        if inner.value is not None and not is_pure_expr(inner.value):
                            violations.append(f"{source_path}:{inner.lineno}: helper return expression contains disallowed constructs")
                    else:
                        violations.append(f"{source_path}:{inner.lineno}: disallowed helper statement type {type(inner).__name__}")
                continue
            if isinstance(stmt, ast.Assign):
                if len(stmt.targets) != 1:
                    violations.append(f"{source_path}:{stmt.lineno}: multiple assignment targets not allowed")
                    continue
                target = stmt.targets[0]
                if isinstance(target, ast.Name):
                    allowed_target = True
                elif isinstance(target, (ast.Tuple, ast.List)):
                    allowed_target = all(isinstance(elt, ast.Name) for elt in target.elts)
                else:
                    allowed_target = False
                if not allowed_target:
                    violations.append(f"{source_path}:{stmt.lineno}: assignments must target names or tuples of names")
                elif not is_pure_expr(stmt.value):
                    violations.append(f"{source_path}:{stmt.lineno}: assignment uses disallowed expression")
            elif isinstance(stmt, ast.If):
                _validate_guard_if(stmt, source_path, violations)
            elif isinstance(stmt, ast.Return):
                if stmt.value is not None and not is_pure_expr(stmt.value):
                    violations.append(f"{source_path}:{stmt.lineno}: return expression contains disallowed constructs")
            else:
                violations.append(f"{source_path}:{stmt.lineno}: disallowed statement type {type(stmt).__name__}")
    return violations


def build_stub_module(
    func_signatures: Dict[str, Tuple[List[str], str]],
    identifiers: Set[str],
    lambda_code: str,
) -> str:
    header_lines = [
        "from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Sequence, Set, Tuple, TypeVar",
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

    helper_lines = [
        "TGrid = TypeVar('TGrid')",
        "TItem = TypeVar('TItem')",
        "",
        "def fold_repaint(initial: TGrid, items: List[TItem], update: Callable[[TGrid, TItem], TGrid]) -> TGrid:",
        "    raise NotImplementedError",
        "",
    ]

    stub_lines: List[str] = []
    for name, (arg_types, return_type) in sorted(func_signatures.items()):
        params = ", ".join(f"arg{i}: {arg_types[i]}" for i in range(len(arg_types)))
        stub_lines.append(f"def {name}({params}) -> {return_type}:")
        stub_lines.append("    raise NotImplementedError")
        stub_lines.append("")

    module_parts = header_lines + helper_lines + stub_lines
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
    purity_violations: List[str] = []

    for file_path in abstraction_files:
        text = file_path.read_text()
        typed_ops, type_tokens = parse_typed_operations(text)
        lambda_code, lambda_tokens = parse_lambda_block(text)

        if not typed_ops or not lambda_code:
            continue

        purity_violations.extend(validate_lambda_purity(lambda_code, file_path))

        identifiers = type_tokens | lambda_tokens
        module_source = build_stub_module(typed_ops, identifiers, lambda_code)
        modules[file_path] = module_source

    if not modules:
        print("No lambda representations found in the provided files.", file=sys.stderr)
        return 1

    if purity_violations:
        for message in purity_violations:
            print(f"purity violation: {message}", file=sys.stderr)
        return 1

    exit_code, output = run_mypy_on_modules(modules)
    sys.stdout.write(output)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
