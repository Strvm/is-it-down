from __future__ import annotations

import ast
from pathlib import Path

SRC_ROOT = Path("src")


class _LocalControlFlowVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.has_non_none_return = False
        self.has_yield = False

    def visit_Return(self, node: ast.Return) -> None:  # noqa: N802
        if node.value is not None:
            self.has_non_none_return = True

    def visit_Yield(self, node: ast.Yield) -> None:  # noqa: N802
        self.has_yield = True

    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:  # noqa: N802
        self.has_yield = True

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        return


def _iter_functions(tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _function_args(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    args: list[str] = []
    for arg in list(node.args.posonlyargs) + list(node.args.args) + list(node.args.kwonlyargs):
        if arg.arg in {"self", "cls"}:
            continue
        args.append(arg.arg)

    if node.args.vararg is not None:
        args.append(f"*{node.args.vararg.arg}")
    if node.args.kwarg is not None:
        args.append(f"**{node.args.kwarg.arg}")
    return args


def _is_none_annotation(annotation: ast.expr | None) -> bool:
    if annotation is None:
        return False
    if isinstance(annotation, ast.Name) and annotation.id == "None":
        return True
    if isinstance(annotation, ast.Constant) and annotation.value is None:
        return True
    return False


def _analyze_local_flow(node: ast.FunctionDef | ast.AsyncFunctionDef) -> _LocalControlFlowVisitor:
    visitor = _LocalControlFlowVisitor()
    for stmt in node.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            continue
        visitor.visit(stmt)
    return visitor


def _missing_docstring_issues() -> list[str]:
    issues: list[str] = []
    for file_path in sorted(SRC_ROOT.rglob("*.py")):
        source = file_path.read_text()
        tree = ast.parse(source)
        relative = file_path.as_posix()

        if ast.get_docstring(tree) is None:
            issues.append(f"{relative}: missing module docstring")

        for node in tree.body:
            if isinstance(node, ast.ClassDef) and ast.get_docstring(node) is None:
                issues.append(f"{relative}:{node.lineno}: class `{node.name}` missing docstring")

        for node in _iter_functions(tree):
            docstring = ast.get_docstring(node)
            if docstring is None:
                issues.append(f"{relative}:{node.lineno}: function `{node.name}` missing docstring")
                continue

            doc = f"\n{docstring}\n"
            args = _function_args(node)
            if args and "\nArgs:\n" not in doc:
                issues.append(f"{relative}:{node.lineno}: function `{node.name}` missing Args section")

            flow = _analyze_local_flow(node)
            expects_yields = flow.has_yield
            expects_returns = (not expects_yields) and (
                flow.has_non_none_return or (node.returns is not None and not _is_none_annotation(node.returns))
            )
            if expects_yields and "\nYields:\n" not in doc:
                issues.append(f"{relative}:{node.lineno}: function `{node.name}` missing Yields section")
            if expects_returns and "\nReturns:\n" not in doc:
                issues.append(f"{relative}:{node.lineno}: function `{node.name}` missing Returns section")

    return issues


def test_src_docstrings_follow_google_sections() -> None:
    issues = _missing_docstring_issues()
    assert not issues, "Google docstring validation failed:\n" + "\n".join(issues)
