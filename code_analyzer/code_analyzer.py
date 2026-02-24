"""
code_analyzer.py — Production-grade Python code analyzer for LLM-driven test generation.

Performs deep static analysis on every .py file in a repository and outputs a structured
JSON report containing everything an LLM needs to generate high-coverage test suites.

Usage:
    CLI:          python code_analyzer.py /path/to/repo --output report.json
    Programmatic: from code_analyzer import analyze_repo; result = analyze_repo("/path/to/repo")

Engines used: ast, symtable, tokenize, importlib, and optionally mypy.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import io
import json
import logging
import os
import re
import symtable
import sys
import textwrap
import tokenize
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("code_analyzer")

# ---------------------------------------------------------------------------
# Stdlib module list (for import classification)
# ---------------------------------------------------------------------------

_STDLIB_TOP_LEVEL: set[str] | None = None


def _get_stdlib_modules() -> set[str]:
    global _STDLIB_TOP_LEVEL
    if _STDLIB_TOP_LEVEL is not None:
        return _STDLIB_TOP_LEVEL
    if sys.version_info >= (3, 10):
        _STDLIB_TOP_LEVEL = sys.stdlib_module_names  # type: ignore[attr-defined]
    else:
        import pkgutil
        _STDLIB_TOP_LEVEL = {m.name for m in pkgutil.iter_modules() if m.module_finder is None}
    return _STDLIB_TOP_LEVEL


_local_package_cache: dict[str, set[str]] = {}


def _get_local_packages(repo_root: Path) -> set[str]:
    """Cache the set of top-level package/module names found in the repo."""
    key = str(repo_root)
    if key in _local_package_cache:
        return _local_package_cache[key]

    exclude = {"node_modules", ".venv", "venv", "__pycache__", ".git", ".tox", ".mypy_cache", "env", "dist", "build"}
    packages: set[str] = set()

    # Top-level .py files
    for f in repo_root.iterdir():
        if f.suffix == ".py" and f.is_file():
            packages.add(f.stem)
        elif f.is_dir() and f.name not in exclude:
            # Directory with __init__.py = package
            if (f / "__init__.py").exists():
                packages.add(f.name)
            # Also recurse one level for nested packages (e.g., backend/app)
            for sub in f.iterdir():
                if sub.is_dir() and sub.name not in exclude and (sub / "__init__.py").exists():
                    packages.add(sub.name)

    _local_package_cache[key] = packages
    return packages


def _classify_import(name: str, repo_root: Path, module_path: Path) -> str:
    top = name.split(".")[0]
    if top in _get_stdlib_modules():
        return "stdlib"

    # Check against cached local packages
    if top in _get_local_packages(repo_root):
        return "local"

    # Check relative to the module's parent (handles relative-style imports)
    if (module_path.parent / top).is_dir() or (module_path.parent / f"{top}.py").is_file():
        return "local"

    # Walk up from module to repo root
    current = module_path.parent
    while current != repo_root and current != current.parent:
        if (current / top).is_dir() or (current / f"{top}.py").is_file():
            return "local"
        current = current.parent

    return "third_party"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ImportInfo:
    name: str
    alias: str | None
    category: str  # stdlib | third_party | local
    is_conditional: bool = False
    line: int = 0


@dataclass
class ModuleVariable:
    name: str
    type_annotation: str | None
    value_repr: str | None
    is_constant: bool
    line: int


@dataclass
class ParameterInfo:
    name: str
    annotation: str | None
    default: str | None
    kind: str  # POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, VAR_POSITIONAL, KEYWORD_ONLY, VAR_KEYWORD


@dataclass
class DocstringInfo:
    raw: str | None
    summary: str | None
    param_descriptions: dict[str, str]
    return_description: str | None
    raised_exceptions: list[str]
    examples: list[str]


@dataclass
class ComplexityMetrics:
    cyclomatic: int
    cognitive: int
    nesting_depth: int
    loc: int


@dataclass
class ControlFlowInfo:
    branch_count: int
    exception_types_raised: list[str]
    exception_types_caught: list[str]
    has_finally: bool
    is_generator: bool
    is_async_generator: bool
    is_coroutine: bool
    has_match_case: bool
    has_for_else: bool
    has_while_else: bool


@dataclass
class DataFlowInfo:
    calls_made: list[str]
    globals_read: list[str]
    globals_written: list[str]
    nonlocals: list[str]
    args_mutated: list[str]
    instance_attrs_read: list[str]
    instance_attrs_written: list[str]
    is_pure: bool


@dataclass
class EdgeCaseHint:
    parameter: str | None
    category: str  # none_input, empty_input, boundary_value, type_mismatch, exception_path, boolean_combo
    description: str


@dataclass
class FunctionInfo:
    qualified_name: str
    name: str
    source: str
    start_line: int
    end_line: int
    parameters: list[ParameterInfo]
    return_annotation: str | None
    return_types_inferred: list[str]
    docstring: DocstringInfo
    decorators: list[str]
    complexity: ComplexityMetrics
    control_flow: ControlFlowInfo
    data_flow: DataFlowInfo
    edge_cases: list[EdgeCaseHint]
    is_method: bool = False
    is_staticmethod: bool = False
    is_classmethod: bool = False
    is_property: bool = False
    is_abstractmethod: bool = False
    nested_functions: list[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    qualified_name: str
    name: str
    source: str
    start_line: int
    end_line: int
    base_classes: list[str]
    docstring: str | None
    init_parameters: list[ParameterInfo]
    instance_attributes: list[dict[str, str | None]]
    class_attributes: list[dict[str, str | None]]
    methods: dict[str, list[FunctionInfo]]  # grouped: public, private, dunder, static, class_, property
    abstract_methods: list[str]
    decorators: list[str]
    is_dataclass: bool
    is_pydantic_model: bool


@dataclass
class ModuleInfo:
    path: str
    import_name: str  # How to import this module (e.g. "app.core.security")
    docstring: str | None
    imports: list[ImportInfo]
    module_variables: list[ModuleVariable]
    functions: list[FunctionInfo]
    classes: list[ClassInfo]
    all_exports: list[str] | None
    has_main_block: bool
    errors: list[str]


@dataclass
class TestGenerationHints:
    suggested_test_order: list[str]
    shared_fixtures_needed: list[str]
    mocking_targets: list[str]
    high_priority_targets: list[dict[str, str]]


@dataclass
class RepositoryReport:
    repository: dict[str, Any]
    modules: list[ModuleInfo]
    test_generation_hints: TestGenerationHints


# ---------------------------------------------------------------------------
# Docstring parser
# ---------------------------------------------------------------------------

def _parse_docstring(raw: str | None) -> DocstringInfo:
    if not raw:
        return DocstringInfo(raw=None, summary=None, param_descriptions={}, return_description=None, raised_exceptions=[], examples=[])

    lines = textwrap.dedent(raw).strip().splitlines()
    summary = lines[0].strip() if lines else None

    params: dict[str, str] = {}
    return_desc: str | None = None
    raises: list[str] = []
    examples: list[str] = []
    in_example = False
    example_buf: list[str] = []

    for line in lines[1:]:
        stripped = line.strip()

        # Google / numpy style
        m_param = re.match(r":param\s+(\w+):\s*(.*)", stripped) or re.match(r"(\w+)\s*\(.*?\):\s*(.*)", stripped)
        if m_param:
            params[m_param.group(1)] = m_param.group(2)
            in_example = False
            continue

        m_return = re.match(r":returns?:\s*(.*)", stripped) or re.match(r"Returns?:\s*(.*)", stripped)
        if m_return:
            return_desc = m_return.group(1)
            in_example = False
            continue

        m_raises = re.match(r":raises?\s+(\w+):\s*(.*)", stripped)
        if m_raises:
            raises.append(m_raises.group(1))
            in_example = False
            continue
        m_raises_google = re.match(r"Raises?:\s*$", stripped) or re.match(r"Raises?:\s+(\w+)", stripped)
        if m_raises_google:
            if m_raises_google.lastindex and m_raises_google.group(1):
                raises.append(m_raises_google.group(1))
            in_example = False
            continue

        if stripped.startswith(">>>") or stripped.startswith("Example"):
            in_example = True

        if in_example:
            example_buf.append(stripped)

    if example_buf:
        examples.append("\n".join(example_buf))

    return DocstringInfo(raw=raw, summary=summary, param_descriptions=params, return_description=return_desc, raised_exceptions=raises, examples=examples)


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _node_source(node: ast.AST, source_lines: list[str]) -> str:
    start = getattr(node, "lineno", 1) - 1
    end = getattr(node, "end_lineno", start + 1)
    return "\n".join(source_lines[start:end])


def _decorator_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_decorator_name(node.value)}.{node.attr}"
    if isinstance(node, ast.Call):
        args_repr = ", ".join(_safe_unparse(a) for a in node.args)
        return f"{_decorator_name(node.func)}({args_repr})"
    return _safe_unparse(node)


def _safe_unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return "<unknown>"


def _get_annotation(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    return _safe_unparse(node)


# ---------------------------------------------------------------------------
# Cyclomatic & cognitive complexity
# ---------------------------------------------------------------------------

def _cyclomatic_complexity(node: ast.AST) -> int:
    """Count decision points + 1."""
    count = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.IfExp)):
            count += 1
        elif isinstance(child, ast.For):
            count += 1
        elif isinstance(child, ast.While):
            count += 1
        elif isinstance(child, ast.ExceptHandler):
            count += 1
        elif isinstance(child, ast.With):
            count += 1
        elif isinstance(child, ast.Assert):
            count += 1
        elif isinstance(child, ast.BoolOp):
            count += len(child.values) - 1
        elif isinstance(child, ast.Match):
            count += len(child.cases)
    return count


def _cognitive_complexity(node: ast.AST, depth: int = 0) -> int:
    """Simplified cognitive complexity: increments for nesting and structural complexity."""
    total = 0
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
            total += 1 + depth
            total += _cognitive_complexity(child, depth + 1)
        elif isinstance(child, ast.Match):
            total += 1 + depth
            total += _cognitive_complexity(child, depth + 1)
        elif isinstance(child, ast.BoolOp):
            total += len(child.values) - 1
            total += _cognitive_complexity(child, depth)
        else:
            total += _cognitive_complexity(child, depth)
    return total


def _max_nesting_depth(node: ast.AST, current: int = 0) -> int:
    max_depth = current
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.ExceptHandler, ast.Match)):
            child_depth = _max_nesting_depth(child, current + 1)
            max_depth = max(max_depth, child_depth)
        else:
            child_depth = _max_nesting_depth(child, current)
            max_depth = max(max_depth, child_depth)
    return max_depth


# ---------------------------------------------------------------------------
# Control flow analysis
# ---------------------------------------------------------------------------

def _analyze_control_flow(node: ast.FunctionDef | ast.AsyncFunctionDef) -> ControlFlowInfo:
    raised: list[str] = []
    caught: list[str] = []
    has_finally = False
    is_generator = False
    is_async_generator = False
    is_coroutine = isinstance(node, ast.AsyncFunctionDef)
    has_match = False
    has_for_else = False
    has_while_else = False
    branch_count = 0

    for child in ast.walk(node):
        if isinstance(child, ast.Raise):
            if child.exc:
                if isinstance(child.exc, ast.Call) and isinstance(child.exc.func, ast.Name):
                    raised.append(child.exc.func.id)
                elif isinstance(child.exc, ast.Call) and isinstance(child.exc.func, ast.Attribute):
                    raised.append(_safe_unparse(child.exc.func))
                elif isinstance(child.exc, ast.Name):
                    raised.append(child.exc.id)
                else:
                    raised.append(_safe_unparse(child.exc))

        elif isinstance(child, ast.ExceptHandler):
            if child.type:
                caught.append(_safe_unparse(child.type))
            else:
                caught.append("BaseException")
            branch_count += 1

        elif isinstance(child, ast.Try):
            if child.finalbody:
                has_finally = True

        elif isinstance(child, (ast.If, ast.IfExp)):
            branch_count += 1

        elif isinstance(child, ast.For):
            branch_count += 1
            if child.orelse:
                has_for_else = True

        elif isinstance(child, ast.While):
            branch_count += 1
            if child.orelse:
                has_while_else = True

        elif isinstance(child, ast.Match):
            has_match = True
            branch_count += len(child.cases)

        elif isinstance(child, ast.Yield):
            is_generator = True
            if is_coroutine:
                is_async_generator = True

        elif isinstance(child, ast.YieldFrom):
            is_generator = True

    return ControlFlowInfo(
        branch_count=branch_count,
        exception_types_raised=list(set(raised)),
        exception_types_caught=list(set(caught)),
        has_finally=has_finally,
        is_generator=is_generator,
        is_async_generator=is_async_generator,
        is_coroutine=is_coroutine,
        has_match_case=has_match,
        has_for_else=has_for_else,
        has_while_else=has_while_else,
    )


# ---------------------------------------------------------------------------
# Data flow analysis
# ---------------------------------------------------------------------------

_MUTATION_METHODS = frozenset({
    "append", "extend", "insert", "remove", "pop", "clear", "sort", "reverse",
    "update", "setdefault", "add", "discard",
})


def _analyze_data_flow(node: ast.FunctionDef | ast.AsyncFunctionDef) -> DataFlowInfo:
    calls: list[str] = []
    globals_read: list[str] = []
    globals_written: list[str] = []
    nonlocals: list[str] = []
    args_mutated: set[str] = set()
    instance_attrs_read: set[str] = set()
    instance_attrs_written: set[str] = set()
    has_side_effects = False

    param_names = {a.arg for a in node.args.args}
    if node.args.vararg:
        param_names.add(node.args.vararg.arg)
    if node.args.kwarg:
        param_names.add(node.args.kwarg.arg)
    for a in node.args.kwonlyargs:
        param_names.add(a.arg)
    for a in node.args.posonlyargs:
        param_names.add(a.arg)

    declared_globals: set[str] = set()
    declared_nonlocals: set[str] = set()

    for child in ast.walk(node):
        # Global/nonlocal declarations
        if isinstance(child, ast.Global):
            declared_globals.update(child.names)
            has_side_effects = True
        elif isinstance(child, ast.Nonlocal):
            declared_nonlocals.update(child.names)
            nonlocals.extend(child.names)
            has_side_effects = True

        # Function calls
        elif isinstance(child, ast.Call):
            call_name = _safe_unparse(child.func)
            calls.append(call_name)

            # Check for mutation via method calls on params
            if isinstance(child.func, ast.Attribute):
                if isinstance(child.func.value, ast.Name) and child.func.value.id in param_names:
                    if child.func.attr in _MUTATION_METHODS:
                        args_mutated.add(child.func.value.id)
                        has_side_effects = True

                # Instance attribute access via method call
                if isinstance(child.func.value, ast.Attribute) and isinstance(child.func.value.value, ast.Name):
                    if child.func.value.value.id == "self":
                        instance_attrs_read.add(child.func.value.attr)

        # Attribute access on self
        elif isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name) and child.value.id == "self":
            instance_attrs_read.add(child.attr)

        # Assignments to self.x or global variables
        elif isinstance(child, ast.Assign):
            for target in child.targets:
                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                    instance_attrs_written.add(target.attr)
                    has_side_effects = True
                elif isinstance(target, ast.Name) and target.id in declared_globals:
                    globals_written.append(target.id)
                elif isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) and target.value.id in param_names:
                    args_mutated.add(target.value.id)
                    has_side_effects = True

        elif isinstance(child, ast.AugAssign):
            if isinstance(child.target, ast.Attribute) and isinstance(child.target.value, ast.Name) and child.target.value.id == "self":
                instance_attrs_written.add(child.target.attr)
                has_side_effects = True
            elif isinstance(child.target, ast.Name) and child.target.id in declared_globals:
                globals_written.append(child.target.id)

    # Globals read (heuristic: names referenced that are in global declarations)
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and child.id in declared_globals:
            if child.id not in globals_written:
                globals_read.append(child.id)

    return DataFlowInfo(
        calls_made=list(set(calls)),
        globals_read=list(set(globals_read)),
        globals_written=list(set(globals_written)),
        nonlocals=list(set(nonlocals)),
        args_mutated=sorted(args_mutated),
        instance_attrs_read=sorted(instance_attrs_read),
        instance_attrs_written=sorted(instance_attrs_written),
        is_pure=not has_side_effects and not calls,  # conservative: any call is impure
    )


# ---------------------------------------------------------------------------
# Edge case inference
# ---------------------------------------------------------------------------

def _infer_edge_cases(func_node: ast.FunctionDef | ast.AsyncFunctionDef, control_flow: ControlFlowInfo) -> list[EdgeCaseHint]:
    hints: list[EdgeCaseHint] = []

    for arg in func_node.args.args + func_node.args.kwonlyargs + func_node.args.posonlyargs:
        name = arg.arg
        if name == "self" or name == "cls":
            continue

        ann = _get_annotation(arg.annotation)

        # None/empty inputs
        hints.append(EdgeCaseHint(parameter=name, category="none_input", description=f"Pass None for '{name}'"))
        hints.append(EdgeCaseHint(parameter=name, category="empty_input", description=f"Pass empty value for '{name}' (empty string, empty list, etc.)"))

        # Boundary values based on type annotation
        if ann:
            ann_lower = ann.lower()
            if "int" in ann_lower or "float" in ann_lower:
                hints.append(EdgeCaseHint(parameter=name, category="boundary_value", description=f"Pass 0, -1, very large number for '{name}'"))
            if "str" in ann_lower:
                hints.append(EdgeCaseHint(parameter=name, category="boundary_value", description=f"Pass empty string, very long string, unicode for '{name}'"))
            if "list" in ann_lower or "set" in ann_lower:
                hints.append(EdgeCaseHint(parameter=name, category="boundary_value", description=f"Pass empty collection, single element, very large collection for '{name}'"))
            if "bool" in ann_lower:
                hints.append(EdgeCaseHint(parameter=name, category="boolean_combo", description=f"Test both True and False for '{name}'"))

        # Type mismatch
        hints.append(EdgeCaseHint(parameter=name, category="type_mismatch", description=f"Pass wrong type for '{name}'"))

    # Exception paths
    for exc_type in control_flow.exception_types_raised:
        hints.append(EdgeCaseHint(parameter=None, category="exception_path", description=f"Trigger {exc_type} raise path"))

    for exc_type in control_flow.exception_types_caught:
        hints.append(EdgeCaseHint(parameter=None, category="exception_path", description=f"Test {exc_type} exception handling path"))

    return hints


# ---------------------------------------------------------------------------
# Symbol table analysis
# ---------------------------------------------------------------------------

def _analyze_symtable(source: str, filename: str) -> dict[str, Any]:
    result: dict[str, Any] = {"free_variables": [], "global_variables": [], "has_closures": False}
    try:
        table = symtable.symtable(source, filename, "exec")
        for child in table.get_children():
            for sym in child.get_symbols():
                if sym.is_free():
                    result["free_variables"].append(sym.get_name())
                    result["has_closures"] = True
                if sym.is_global():
                    result["global_variables"].append(sym.get_name())
    except Exception:
        pass
    return result


# ---------------------------------------------------------------------------
# Tokenize analysis (comments, pragmas)
# ---------------------------------------------------------------------------

def _analyze_tokens(source: str) -> dict[str, Any]:
    result: dict[str, Any] = {"type_ignore_lines": [], "noqa_lines": [], "todo_comments": [], "pragma_comments": []}
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for tok in tokens:
            if tok.type == tokenize.COMMENT:
                comment = tok.string
                line = tok.start[0]
                if "type: ignore" in comment:
                    result["type_ignore_lines"].append(line)
                if "noqa" in comment:
                    result["noqa_lines"].append(line)
                if "TODO" in comment or "FIXME" in comment or "HACK" in comment or "XXX" in comment:
                    result["todo_comments"].append({"line": line, "text": comment.strip("# ").strip()})
                if "pragma" in comment.lower():
                    result["pragma_comments"].append({"line": line, "text": comment.strip("# ").strip()})
    except tokenize.TokenError:
        pass
    return result


# ---------------------------------------------------------------------------
# mypy integration (optional)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Function analyzer
# ---------------------------------------------------------------------------

def _analyze_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    module_name: str,
    class_name: str | None,
    source_lines: list[str],
) -> FunctionInfo:
    # Qualified name
    parts = [module_name]
    if class_name:
        parts.append(class_name)
    parts.append(node.name)
    qualified_name = ".".join(parts)

    # Parameters
    parameters: list[ParameterInfo] = []
    all_args = node.args

    # positional-only
    for i, arg in enumerate(all_args.posonlyargs):
        default_idx = i - (len(all_args.posonlyargs) - len(all_args.defaults))
        default = _safe_unparse(all_args.defaults[default_idx]) if default_idx >= 0 and default_idx < len(all_args.defaults) else None
        parameters.append(ParameterInfo(
            name=arg.arg, annotation=_get_annotation(arg.annotation),
            default=default, kind="POSITIONAL_ONLY",
        ))

    # regular positional/keyword
    num_no_default = len(all_args.args) - len(all_args.defaults)
    for i, arg in enumerate(all_args.args):
        default_idx = i - num_no_default
        default = _safe_unparse(all_args.defaults[default_idx]) if default_idx >= 0 else None
        parameters.append(ParameterInfo(
            name=arg.arg, annotation=_get_annotation(arg.annotation),
            default=default, kind="POSITIONAL_OR_KEYWORD",
        ))

    if all_args.vararg:
        parameters.append(ParameterInfo(
            name=all_args.vararg.arg, annotation=_get_annotation(all_args.vararg.annotation),
            default=None, kind="VAR_POSITIONAL",
        ))

    # keyword-only
    for i, arg in enumerate(all_args.kwonlyargs):
        kw_default = all_args.kw_defaults[i]
        default = _safe_unparse(kw_default) if kw_default else None
        parameters.append(ParameterInfo(
            name=arg.arg, annotation=_get_annotation(arg.annotation),
            default=default, kind="KEYWORD_ONLY",
        ))

    if all_args.kwarg:
        parameters.append(ParameterInfo(
            name=all_args.kwarg.arg, annotation=_get_annotation(all_args.kwarg.annotation),
            default=None, kind="VAR_KEYWORD",
        ))

    # Return annotation
    return_annotation = _get_annotation(node.returns)

    # Inferred return types from return statements
    return_types_inferred: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Return) and child.value:
            ret_repr = _safe_unparse(child.value)
            # Try to classify the return type
            if isinstance(child.value, ast.Constant):
                return_types_inferred.append(type(child.value.value).__name__)
            elif isinstance(child.value, ast.Dict):
                return_types_inferred.append("dict")
            elif isinstance(child.value, ast.List):
                return_types_inferred.append("list")
            elif isinstance(child.value, ast.Tuple):
                return_types_inferred.append("tuple")
            elif isinstance(child.value, ast.Set):
                return_types_inferred.append("set")
            elif isinstance(child.value, ast.Call):
                return_types_inferred.append(f"call:{_safe_unparse(child.value.func)}")
            elif isinstance(child.value, ast.Name):
                return_types_inferred.append(f"var:{child.value.id}")
            else:
                return_types_inferred.append(f"expr:{ret_repr[:50]}")
    return_types_inferred = list(set(return_types_inferred))

    # Docstring
    raw_docstring = ast.get_docstring(node, clean=False)
    docstring = _parse_docstring(raw_docstring)

    # Decorators
    decorators = [_decorator_name(d) for d in node.decorator_list]

    # Source
    source = _node_source(node, source_lines)

    # Line span
    start_line = node.lineno
    end_line = node.end_lineno or node.lineno

    # Complexity
    loc = end_line - start_line + 1
    complexity = ComplexityMetrics(
        cyclomatic=_cyclomatic_complexity(node),
        cognitive=_cognitive_complexity(node),
        nesting_depth=_max_nesting_depth(node),
        loc=loc,
    )

    # Control flow
    control_flow = _analyze_control_flow(node)

    # Data flow
    data_flow = _analyze_data_flow(node)

    # Edge cases
    edge_cases = _infer_edge_cases(node, control_flow)

    # Decorator-based flags
    is_staticmethod = any("staticmethod" in d for d in decorators)
    is_classmethod = any("classmethod" in d for d in decorators)
    is_property = any("property" in d for d in decorators)
    is_abstractmethod = any("abstractmethod" in d for d in decorators)

    # Nested functions
    nested = []
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            nested.append(child.name)

    return FunctionInfo(
        qualified_name=qualified_name,
        name=node.name,
        source=source,
        start_line=start_line,
        end_line=end_line,
        parameters=parameters,
        return_annotation=return_annotation,
        return_types_inferred=return_types_inferred,
        docstring=docstring,
        decorators=decorators,
        complexity=complexity,
        control_flow=control_flow,
        data_flow=data_flow,
        edge_cases=edge_cases,
        is_method=class_name is not None,
        is_staticmethod=is_staticmethod,
        is_classmethod=is_classmethod,
        is_property=is_property,
        is_abstractmethod=is_abstractmethod,
        nested_functions=nested,
    )


# ---------------------------------------------------------------------------
# Class analyzer
# ---------------------------------------------------------------------------

def _analyze_class(
    node: ast.ClassDef,
    module_name: str,
    source_lines: list[str],
) -> ClassInfo:
    qualified_name = f"{module_name}.{node.name}"
    base_classes = [_safe_unparse(b) for b in node.bases]
    docstring = ast.get_docstring(node, clean=False)
    decorators = [_decorator_name(d) for d in node.decorator_list]

    is_dataclass = any("dataclass" in d for d in decorators)
    is_pydantic = any(b in ("BaseModel", "BaseSettings") for b in base_classes)

    # Class attributes
    class_attrs: list[dict[str, str | None]] = []
    instance_attrs: list[dict[str, str | None]] = []
    init_params: list[ParameterInfo] = []

    # Methods grouped
    methods: dict[str, list[FunctionInfo]] = {
        "public": [], "private": [], "dunder": [],
        "static": [], "class_": [], "property": [],
    }
    abstract_methods: list[str] = []

    for child in ast.iter_child_nodes(node):
        # Class-level assignments (class attributes)
        if isinstance(child, ast.Assign):
            for target in child.targets:
                if isinstance(target, ast.Name):
                    class_attrs.append({
                        "name": target.id,
                        "type": None,
                        "value": _safe_unparse(child.value),
                    })
        elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            class_attrs.append({
                "name": child.target.id,
                "type": _get_annotation(child.annotation),
                "value": _safe_unparse(child.value) if child.value else None,
            })

        # Methods
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_info = _analyze_function(child, module_name, node.name, source_lines)

            # Collect __init__ params and instance attrs
            if child.name == "__init__":
                init_params = func_info.parameters
                # Instance attributes from self.x = ... in __init__
                for sub in ast.walk(child):
                    if isinstance(sub, ast.Assign):
                        for target in sub.targets:
                            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                                instance_attrs.append({
                                    "name": target.attr,
                                    "type": None,
                                    "value": _safe_unparse(sub.value),
                                })
                    elif isinstance(sub, ast.AnnAssign):
                        if isinstance(sub.target, ast.Attribute) and isinstance(sub.target.value, ast.Name) and sub.target.value.id == "self":
                            instance_attrs.append({
                                "name": sub.target.attr,
                                "type": _get_annotation(sub.annotation),
                                "value": _safe_unparse(sub.value) if sub.value else None,
                            })

            if func_info.is_abstractmethod:
                abstract_methods.append(child.name)

            # Group
            if func_info.is_staticmethod:
                methods["static"].append(func_info)
            elif func_info.is_classmethod:
                methods["class_"].append(func_info)
            elif func_info.is_property:
                methods["property"].append(func_info)
            elif child.name.startswith("__") and child.name.endswith("__"):
                methods["dunder"].append(func_info)
            elif child.name.startswith("_"):
                methods["private"].append(func_info)
            else:
                methods["public"].append(func_info)

    source = _node_source(node, source_lines)

    return ClassInfo(
        qualified_name=qualified_name,
        name=node.name,
        source=source,
        start_line=node.lineno,
        end_line=node.end_lineno or node.lineno,
        base_classes=base_classes,
        docstring=docstring,
        init_parameters=init_params,
        instance_attributes=instance_attrs,
        class_attributes=class_attrs,
        methods=methods,
        abstract_methods=abstract_methods,
        decorators=decorators,
        is_dataclass=is_dataclass,
        is_pydantic_model=is_pydantic,
    )


# ---------------------------------------------------------------------------
# Module analyzer
# ---------------------------------------------------------------------------

def _analyze_module(file_path: Path, repo_root: Path, import_roots: list[Path] | None = None) -> ModuleInfo:
    rel_path = file_path.relative_to(repo_root)

    # Compute importable module name using detected import roots
    if import_roots:
        import_name = _resolve_import_name(file_path, import_roots)
    else:
        import_name = str(rel_path.with_suffix("")).replace(os.sep, ".").replace("/", ".")
    module_name = import_name

    errors: list[str] = []

    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return ModuleInfo(
            path=str(rel_path), import_name=import_name,
            docstring=None, imports=[], module_variables=[],
            functions=[], classes=[], all_exports=None, has_main_block=False,
            errors=[f"Could not read file: {e}"],
        )

    source_lines = source.splitlines()

    # Parse AST
    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as e:
        return ModuleInfo(
            path=str(rel_path), import_name=import_name,
            docstring=None, imports=[], module_variables=[],
            functions=[], classes=[], all_exports=None, has_main_block=False,
            errors=[f"SyntaxError: {e}"],
        )

    # Module docstring
    mod_docstring = ast.get_docstring(tree, clean=False)

    # Imports
    imports: list[ImportInfo] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(ImportInfo(
                    name=alias.name, alias=alias.asname,
                    category=_classify_import(alias.name, repo_root, file_path),
                    is_conditional=False, line=node.lineno,
                ))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                full_name = f"{mod}.{alias.name}" if mod else alias.name
                imports.append(ImportInfo(
                    name=full_name, alias=alias.asname,
                    category=_classify_import(mod or alias.name, repo_root, file_path),
                    is_conditional=False, line=node.lineno,
                ))

    # Detect conditional imports (inside try/except)
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                if handler.type and _safe_unparse(handler.type) in ("ImportError", "ModuleNotFoundError"):
                    for sub in ast.walk(node):
                        if isinstance(sub, (ast.Import, ast.ImportFrom)):
                            for imp in imports:
                                if imp.line == sub.lineno:
                                    imp.is_conditional = True

    # Module variables
    module_vars: list[ModuleVariable] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    is_const = target.id.isupper() or target.id.startswith("_") and target.id[1:].isupper()
                    module_vars.append(ModuleVariable(
                        name=target.id,
                        type_annotation=None,
                        value_repr=_safe_unparse(node.value)[:200],
                        is_constant=is_const,
                        line=node.lineno,
                    ))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            is_const = node.target.id.isupper()
            module_vars.append(ModuleVariable(
                name=node.target.id,
                type_annotation=_get_annotation(node.annotation),
                value_repr=_safe_unparse(node.value)[:200] if node.value else None,
                is_constant=is_const,
                line=node.lineno,
            ))

    # __all__
    all_exports: list[str] | None = None
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        all_exports = [_safe_unparse(e) for e in node.value.elts]

    # has __main__ block
    has_main = False
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.If):
            test = _safe_unparse(node.test)
            if "__name__" in test and "__main__" in test:
                has_main = True
                break

    # Functions (top-level)
    functions: list[FunctionInfo] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            try:
                functions.append(_analyze_function(node, module_name, None, source_lines))
            except Exception as e:
                errors.append(f"Error analyzing function {node.name}: {e}")

    # Classes
    classes: list[ClassInfo] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            try:
                classes.append(_analyze_class(node, module_name, source_lines))
            except Exception as e:
                errors.append(f"Error analyzing class {node.name}: {e}")

    return ModuleInfo(
        path=str(rel_path).replace("\\", "/"),
        import_name=import_name,
        docstring=mod_docstring,
        imports=imports,
        module_variables=module_vars,
        functions=functions,
        classes=classes,
        all_exports=all_exports,
        has_main_block=has_main,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# Repository-level analysis
# ---------------------------------------------------------------------------

def _detect_testing_framework(repo_root: Path) -> str:
    """Detect which testing framework is used."""
    pyproject = repo_root / "pyproject.toml"
    setup_cfg = repo_root / "setup.cfg"
    requirements = repo_root / "requirements.txt"

    search_files = [pyproject, setup_cfg, requirements]
    # Also check requirements-dev.txt, requirements_test.txt, etc.
    for f in repo_root.glob("requirements*.txt"):
        search_files.append(f)

    for f in search_files:
        if f.exists():
            try:
                content = f.read_text(encoding="utf-8", errors="replace").lower()
                if "pytest" in content:
                    return "pytest"
                if "unittest" in content:
                    return "unittest"
                if "nose" in content:
                    return "nose"
            except Exception:
                pass

    # Check for conftest.py (pytest indicator)
    if any(repo_root.rglob("conftest.py")):
        return "pytest"

    # Check test files for imports
    for test_file in repo_root.rglob("test_*.py"):
        try:
            content = test_file.read_text(encoding="utf-8", errors="replace")
            if "import pytest" in content or "from pytest" in content:
                return "pytest"
            if "import unittest" in content:
                return "unittest"
        except Exception:
            pass

    return "none"


def _find_config_files(repo_root: Path) -> list[str]:
    config_names = [
        "pyproject.toml", "setup.py", "setup.cfg", "tox.ini", "pytest.ini",
        ".flake8", "mypy.ini", ".mypy.ini", "conftest.py", ".pre-commit-config.yaml",
        "Makefile", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    ]
    found = []
    for name in config_names:
        matches = list(repo_root.rglob(name))
        for m in matches:
            found.append(str(m.relative_to(repo_root)).replace("\\", "/"))
    return sorted(set(found))


def _find_test_files(repo_root: Path) -> list[str]:
    test_files = []
    for pattern in ["test_*.py", "*_test.py", "tests.py"]:
        for f in repo_root.rglob(pattern):
            if "node_modules" not in str(f):
                test_files.append(str(f.relative_to(repo_root)).replace("\\", "/"))
    # Also test directories
    for d in repo_root.rglob("tests"):
        if d.is_dir() and "node_modules" not in str(d):
            for f in d.rglob("*.py"):
                rel = str(f.relative_to(repo_root)).replace("\\", "/")
                if rel not in test_files:
                    test_files.append(rel)
    return sorted(set(test_files))


def _build_dependency_graph(modules: list[ModuleInfo]) -> dict[str, list[str]]:
    graph: dict[str, list[str]] = {}
    for mod in modules:
        local_deps = []
        for imp in mod.imports:
            if imp.category == "local":
                local_deps.append(imp.name)
        graph[mod.path] = sorted(set(local_deps))
    return graph


def _generate_test_hints(modules: list[ModuleInfo], test_files: list[str]) -> TestGenerationHints:
    # Suggested test order: topological sort by dependencies (simplified: modules with fewer deps first)
    all_funcs: list[tuple[str, int, bool]] = []  # (qualified_name, complexity, has_test)

    tested_modules = set()
    for tf in test_files:
        # test_foo.py -> foo.py
        base = Path(tf).stem
        if base.startswith("test_"):
            tested_modules.add(base[5:])
        elif base.endswith("_test"):
            tested_modules.add(base[:-5])

    for mod in modules:
        mod_stem = Path(mod.path).stem
        mod_has_test = mod_stem in tested_modules
        for func in mod.functions:
            all_funcs.append((func.qualified_name, func.complexity.cyclomatic, mod_has_test))
        for cls in mod.classes:
            for group_funcs in cls.methods.values():
                for func in group_funcs:
                    all_funcs.append((func.qualified_name, func.complexity.cyclomatic, False))

    # High priority: high complexity + no existing tests
    high_priority = sorted(
        [(name, cc, ht) for name, cc, ht in all_funcs if not ht],
        key=lambda x: -x[1],
    )[:20]

    # Mocking targets: third-party calls
    mocking_targets: set[str] = set()
    for mod in modules:
        for func in mod.functions:
            for call in func.data_flow.calls_made:
                if any(call.startswith(p) for p in ("httpx.", "requests.", "aiohttp.", "urllib.", "boto3.", "redis.", "smtp")):
                    mocking_targets.add(call)
                if "datetime.now" in call or "datetime.utcnow" in call or "time.time" in call:
                    mocking_targets.add(call)
                if any(db_kw in call.lower() for db_kw in ("session", "execute", "query", "commit", "scalar")):
                    mocking_targets.add(call)
        for cls in mod.classes:
            for group_funcs in cls.methods.values():
                for func in group_funcs:
                    for call in func.data_flow.calls_made:
                        if any(call.startswith(p) for p in ("httpx.", "requests.", "aiohttp.", "boto3.")):
                            mocking_targets.add(call)

    # Shared fixtures
    fixtures: set[str] = set()
    for mod in modules:
        for imp in mod.imports:
            if "database" in imp.name.lower() or "db" in imp.name.lower():
                fixtures.add("database_session")
            if "config" in imp.name.lower() or "settings" in imp.name.lower():
                fixtures.add("test_settings")
            if "client" in imp.name.lower() or "httpx" in imp.name.lower():
                fixtures.add("async_http_client")
        for func in mod.functions:
            if func.control_flow.is_coroutine:
                fixtures.add("event_loop")

    return TestGenerationHints(
        suggested_test_order=[name for name, _, _ in all_funcs],
        shared_fixtures_needed=sorted(fixtures),
        mocking_targets=sorted(mocking_targets),
        high_priority_targets=[
            {"name": name, "reason": f"cyclomatic_complexity={cc}, no existing tests"}
            for name, cc, _ in high_priority
        ],
    )


# ---------------------------------------------------------------------------
# Python version detection
# ---------------------------------------------------------------------------

def _detect_python_version(repo_root: Path) -> str:
    """Try to detect target Python version from config files."""
    pyproject = repo_root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8", errors="replace")
            m = re.search(r'python_requires\s*=\s*["\']([^"\']+)["\']', content)
            if m:
                return m.group(1)
            m = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
            if m:
                return m.group(1)
        except Exception:
            pass

    setup_cfg = repo_root / "setup.cfg"
    if setup_cfg.exists():
        try:
            content = setup_cfg.read_text(encoding="utf-8", errors="replace")
            m = re.search(r'python_requires\s*=\s*(.+)', content)
            if m:
                return m.group(1).strip()
        except Exception:
            pass

    # Check for runtime.txt (e.g., Heroku)
    runtime = repo_root / "runtime.txt"
    if runtime.exists():
        try:
            return runtime.read_text().strip()
        except Exception:
            pass

    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


# ---------------------------------------------------------------------------
# Import root detection
# ---------------------------------------------------------------------------

def _detect_import_roots(repo_root: Path, py_files: list[Path]) -> list[Path]:
    """
    Detect the directories that serve as Python import roots.

    Strategy: read actual import statements in the source files and find which
    directory makes those imports resolve.  For example, if a file contains
    ``from app.core.config import settings`` and ``repo_root/backend/app/core/config.py``
    exists, then ``repo_root/backend`` is an import root.

    Falls back to repo_root if nothing more specific is found.
    """
    # 1. Directories containing pyproject.toml / setup.py / setup.cfg are candidates
    candidates: set[Path] = set()
    for marker in ("pyproject.toml", "setup.py", "setup.cfg"):
        for p in repo_root.rglob(marker):
            candidates.add(p.parent)

    # 2. Scan a sample of files for their local imports and test which root resolves them
    import_statements: list[str] = []
    for f in py_files[:40]:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split(".")[0]
                if top not in _get_stdlib_modules():
                    import_statements.append(node.module)

    roots: list[Path] = []
    scored: dict[str, int] = {}
    for cand in candidates | {repo_root}:
        score = 0
        for imp in import_statements:
            parts = imp.split(".")
            resolved = cand / Path(*parts)
            if resolved.with_suffix(".py").is_file() or (resolved / "__init__.py").is_file():
                score += 1
        scored[str(cand)] = score

    if scored:
        best = max(scored, key=lambda k: scored[k])
        roots.append(Path(best))
        # Also include any other candidate that resolves >50% of best's score
        best_score = scored[best]
        if best_score > 0:
            for k, v in scored.items():
                if k != best and v > best_score * 0.5:
                    roots.append(Path(k))

    return roots if roots else [repo_root]


def _resolve_import_name(file_path: Path, import_roots: list[Path]) -> str:
    """
    Given a file path and a list of import roots, return the dotted module name
    that Python would use to import it.
    e.g. /repo/backend/app/core/security.py with root /repo/backend → app.core.security
    """
    for root in sorted(import_roots, key=lambda r: -len(r.parts)):
        try:
            rel = file_path.relative_to(root)
            parts = list(rel.with_suffix("").parts)
            # Drop trailing __init__
            if parts and parts[-1] == "__init__":
                parts.pop()
            if parts:
                return ".".join(parts)
        except ValueError:
            continue
    # Fallback: just the stem (standalone scripts not inside any import root)
    return file_path.stem


# ---------------------------------------------------------------------------
# Worker for parallel analysis
# ---------------------------------------------------------------------------

def _analyze_file_worker(args: tuple[str, str, list[str]]) -> dict[str, Any]:
    """Worker function for ProcessPoolExecutor. Takes (file_path_str, repo_root_str, import_root_strs)."""
    file_path_str, repo_root_str, import_root_strs = args
    file_path = Path(file_path_str)
    repo_root = Path(repo_root_str)
    import_roots = [Path(r) for r in import_root_strs]
    module_info = _analyze_module(file_path, repo_root, import_roots)
    return asdict(module_info)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def analyze_repo(repo_path: str, output_path: str | None = None, verbose: bool = False, parallel: bool = True) -> dict[str, Any]:
    """
    Analyze all Python files in a repository and produce a structured JSON report.

    Args:
        repo_path: Path to the repository root.
        output_path: Optional path to write the JSON report.
        verbose: Enable verbose logging.
        parallel: Use parallel processing for file analysis.

    Returns:
        The analysis report as a dictionary.
    """
    if verbose:
        logger.setLevel(logging.DEBUG)
    elif not logger.handlers:
        logger.setLevel(logging.INFO)

    repo_root = Path(repo_path).resolve()
    if not repo_root.is_dir():
        raise ValueError(f"Not a directory: {repo_root}")

    logger.info("Analyzing repository: %s", repo_root)

    # Discover Python files (exclude common non-source dirs)
    exclude_dirs = {"node_modules", ".venv", "venv", "__pycache__", ".git", ".tox", ".mypy_cache", "env", ".env", "dist", "build", ".eggs"}
    py_files: list[Path] = []
    for f in repo_root.rglob("*.py"):
        # Skip excluded directories
        parts = set(f.relative_to(repo_root).parts)
        if parts & exclude_dirs:
            continue
        py_files.append(f)

    logger.info("Found %d Python files", len(py_files))

    # Detect import roots (where sys.path should point for imports to resolve)
    import_roots = _detect_import_roots(repo_root, py_files)
    logger.info("Detected import roots: %s", [str(r) for r in import_roots])

    # Analyze modules
    modules: list[ModuleInfo] = []

    if parallel and len(py_files) > 5:
        import_root_strs = [str(r) for r in import_roots]
        worker_args = [(str(f), str(repo_root), import_root_strs) for f in py_files]
        with ProcessPoolExecutor(max_workers=min(os.cpu_count() or 4, 8)) as executor:
            futures = {executor.submit(_analyze_file_worker, args): args[0] for args in worker_args}
            for future in as_completed(futures):
                file_name = futures[future]
                try:
                    mod_dict = future.result()
                    modules.append(_module_info_from_dict(mod_dict))
                except Exception as e:
                    logger.error("Failed to analyze %s: %s", file_name, e)
                    rel = str(Path(file_name).relative_to(repo_root)).replace("\\", "/")
                    modules.append(ModuleInfo(
                        path=rel, import_name=rel.replace("/", ".").removesuffix(".py"),
                        docstring=None, imports=[], module_variables=[],
                        functions=[], classes=[], all_exports=None,
                        has_main_block=False, errors=[f"Worker error: {e}"],
                    ))
    else:
        for f in py_files:
            try:
                mod = _analyze_module(f, repo_root, import_roots)
                modules.append(mod)
            except Exception as e:
                logger.error("Failed to analyze %s: %s", f, e)
                rel = str(f.relative_to(repo_root)).replace("\\", "/")
                modules.append(ModuleInfo(
                    path=rel, import_name=rel.replace("/", ".").removesuffix(".py"),
                    docstring=None, imports=[], module_variables=[],
                    functions=[], classes=[], all_exports=None,
                    has_main_block=False, errors=[f"Error: {e}"],
                ))

    # Sort modules by path
    modules.sort(key=lambda m: m.path)

    # Repository-level info
    test_files = _find_test_files(repo_root)
    config_files = _find_config_files(repo_root)
    dependency_graph = _build_dependency_graph(modules)
    testing_framework = _detect_testing_framework(repo_root)
    python_version = _detect_python_version(repo_root)
    import_roots_rel = [str(r.relative_to(repo_root)).replace("\\", "/") if r != repo_root else "." for r in import_roots]

    total_functions = sum(len(m.functions) for m in modules)
    total_classes = sum(len(m.classes) for m in modules)
    for m in modules:
        for c in m.classes:
            for group_funcs in c.methods.values():
                total_functions += len(group_funcs)

    # Symtable + tokenize + bytecode enrichment (done per-module on source)
    for mod in modules:
        file_path = repo_root / mod.path
        if not file_path.exists():
            continue
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        sym_info = _analyze_symtable(source, str(file_path))
        token_info = _analyze_tokens(source)

        # Attach extra info to module errors/metadata (as extra fields in the report)
        if sym_info["has_closures"]:
            mod.errors.append(f"[info] Module uses closures. Free variables: {sym_info['free_variables']}")
        if token_info["todo_comments"]:
            for todo in token_info["todo_comments"]:
                mod.errors.append(f"[todo] Line {todo['line']}: {todo['text']}")

    # Test generation hints
    test_hints = _generate_test_hints(modules, test_files)

    # mypy pass (optional, via subprocess with timeout)
    mypy_results: dict[str, list[str]] = {}
    mypy_available = importlib.util.find_spec("mypy") is not None
    if mypy_available:
        import subprocess
        logger.info("Running mypy analysis (timeout 30s)...")
        try:
            file_list = [str(f) for f in py_files[:50]]
            proc = subprocess.run(
                [sys.executable, "-m", "mypy", "--no-error-summary", "--ignore-missing-imports", "--no-incremental"] + file_list,
                capture_output=True, text=True, timeout=30, cwd=str(repo_root),
            )
            if proc.stdout.strip():
                for line in proc.stdout.strip().splitlines():
                    # Lines look like: path/to/file.py:10: error: ...
                    parts = line.split(":", 1)
                    if len(parts) >= 2:
                        rel = parts[0].replace("\\", "/")
                        mypy_results.setdefault(rel, []).append(line)
        except subprocess.TimeoutExpired:
            logger.warning("mypy timed out after 30s, skipping")
        except Exception as e:
            logger.warning("mypy analysis failed: %s", e)
    else:
        logger.info("mypy not installed, skipping type inference pass")

    # Build final report
    report = {
        "repository": {
            "root_path": str(repo_root),
            "import_roots": import_roots_rel,
            "python_version_detected": python_version,
            "testing_framework": testing_framework,
            "total_modules": len(modules),
            "total_functions": total_functions,
            "total_classes": total_classes,
            "dependency_graph": dependency_graph,
            "existing_test_files": test_files,
            "config_files": config_files,
            "project_structure": [str(f.relative_to(repo_root)).replace("\\", "/") for f in sorted(py_files)],
        },
        "modules": [asdict(m) for m in modules],
        "test_generation_hints": asdict(test_hints),
    }

    if mypy_results:
        report["mypy_analysis"] = mypy_results

    # Write output
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
        logger.info("Report written to %s", out)

    logger.info(
        "Analysis complete: %d modules, %d functions, %d classes",
        len(modules), total_functions, total_classes,
    )

    return report


def _module_info_from_dict(d: dict[str, Any]) -> ModuleInfo:
    """Reconstruct ModuleInfo from a dict (from parallel worker)."""
    return ModuleInfo(
        path=d["path"],
        import_name=d.get("import_name", d["path"].replace("/", ".").removesuffix(".py")),
        docstring=d.get("docstring"),
        imports=[ImportInfo(**i) for i in d.get("imports", [])],
        module_variables=[ModuleVariable(**v) for v in d.get("module_variables", [])],
        functions=[_func_info_from_dict(f) for f in d.get("functions", [])],
        classes=[_class_info_from_dict(c) for c in d.get("classes", [])],
        all_exports=d.get("all_exports"),
        has_main_block=d.get("has_main_block", False),
        errors=d.get("errors", []),
    )


def _func_info_from_dict(d: dict[str, Any]) -> FunctionInfo:
    return FunctionInfo(
        qualified_name=d["qualified_name"],
        name=d["name"],
        source=d["source"],
        start_line=d["start_line"],
        end_line=d["end_line"],
        parameters=[ParameterInfo(**p) for p in d.get("parameters", [])],
        return_annotation=d.get("return_annotation"),
        return_types_inferred=d.get("return_types_inferred", []),
        docstring=DocstringInfo(**d["docstring"]) if isinstance(d.get("docstring"), dict) else _parse_docstring(None),
        decorators=d.get("decorators", []),
        complexity=ComplexityMetrics(**d["complexity"]) if isinstance(d.get("complexity"), dict) else ComplexityMetrics(0, 0, 0, 0),
        control_flow=ControlFlowInfo(**d["control_flow"]) if isinstance(d.get("control_flow"), dict) else ControlFlowInfo(0, [], [], False, False, False, False, False, False, False),
        data_flow=DataFlowInfo(**d["data_flow"]) if isinstance(d.get("data_flow"), dict) else DataFlowInfo([], [], [], [], [], [], [], True),
        edge_cases=[EdgeCaseHint(**e) for e in d.get("edge_cases", [])],
        is_method=d.get("is_method", False),
        is_staticmethod=d.get("is_staticmethod", False),
        is_classmethod=d.get("is_classmethod", False),
        is_property=d.get("is_property", False),
        is_abstractmethod=d.get("is_abstractmethod", False),
        nested_functions=d.get("nested_functions", []),
    )


def _class_info_from_dict(d: dict[str, Any]) -> ClassInfo:
    methods = {}
    for group, funcs in d.get("methods", {}).items():
        methods[group] = [_func_info_from_dict(f) for f in funcs]
    return ClassInfo(
        qualified_name=d["qualified_name"],
        name=d["name"],
        source=d["source"],
        start_line=d["start_line"],
        end_line=d["end_line"],
        base_classes=d.get("base_classes", []),
        docstring=d.get("docstring"),
        init_parameters=[ParameterInfo(**p) for p in d.get("init_parameters", [])],
        instance_attributes=d.get("instance_attributes", []),
        class_attributes=d.get("class_attributes", []),
        methods=methods,
        abstract_methods=d.get("abstract_methods", []),
        decorators=d.get("decorators", []),
        is_dataclass=d.get("is_dataclass", False),
        is_pydantic_model=d.get("is_pydantic_model", False),
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a Python repository for LLM-driven test generation.",
    )
    parser.add_argument("repo_path", help="Path to the repository root")
    parser.add_argument("--output", "-o", default="report.json", help="Output JSON file path (default: report.json)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel file processing")

    args = parser.parse_args()
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(name)s %(levelname)s: %(message)s")
    analyze_repo(
        repo_path=args.repo_path,
        output_path=args.output,
        verbose=args.verbose,
        parallel=not args.no_parallel,
    )


if __name__ == "__main__":
    main()
