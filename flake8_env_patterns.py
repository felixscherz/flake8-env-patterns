import ast
import importlib.metadata
import re
from typing import Any
from typing import Generator
from typing import Type

from flake8.options.manager import OptionManager
from flake8.options.manager import argparse

DEFAULT_ENV_VARIABLE_PATTERNS = [".*"]
PROBLEM_MESSAGE = "FEP001 environment variable does not match any allowed pattern"


class Visitor(ast.NodeVisitor):
    def __init__(self, patterns: list[str]) -> None:
        self.problems: list[tuple[int, int]] = []
        self.patterns = [re.compile(p) for p in patterns]

    def is_allowed(self, name: str) -> bool:
        return any((p.match(name) for p in self.patterns))

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        if (
            isinstance(node.value, ast.Attribute)
            and node.value.attr == "environ"
            and isinstance(node.slice, ast.Constant)
        ):
            if not self.is_allowed(node.slice.value):
                self.problems.append((node.slice.lineno, node.slice.col_offset))

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and isinstance(node.func.value, ast.Attribute)
            and node.func.value.attr == "environ"
        ):
            if isinstance(node.args[0], ast.Constant):
                if not self.is_allowed(node.args[0].value):
                    self.problems.append((node.args[0].lineno, node.args[0].col_offset))
            ...
        if isinstance(node.func, ast.Attribute) and node.func.attr == "getenv":
            if isinstance(node.args[0], ast.Constant):
                if not self.is_allowed(node.args[0].value):
                    self.problems.append((node.args[0].lineno, node.args[0].col_offset))

        self.generic_visit(node)


class Plugin:
    name = __name__
    version = importlib.metadata.version(__name__)
    patterns: list[str] = DEFAULT_ENV_VARIABLE_PATTERNS

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree

    @classmethod
    def add_options(cls, manager: OptionManager):
        manager.add_option(
            long_option_name="--env-variable-patterns",
            metavar="patterns",
            default=DEFAULT_ENV_VARIABLE_PATTERNS,
            comma_separated_list=True,
            parse_from_config=True,
            help="Comma-separated list of regex patterns for allowed environment variables.",
        )

    @classmethod
    def parse_options(cls, options: argparse.Namespace):
        cls.patterns = options.env_variable_patterns

    def run(self) -> Generator[tuple[int, int, str, Type[Any]], None, None]:
        visitor = Visitor(patterns=self.patterns)
        visitor.visit(self._tree)
        for line, col in visitor.problems:
            yield line, col, PROBLEM_MESSAGE, type(self)
