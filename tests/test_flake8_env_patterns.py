import argparse
import ast

from flake8_env_patterns import Plugin


def _results(s: str, patterns: list[str]) -> set[str]:
    tree = ast.parse(s)
    options = argparse.Namespace(env_variable_patterns=patterns)
    Plugin.parse_options(options)
    plugin = Plugin(tree=tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_trivial_case():
    assert _results("", [".*"]) == set()


def test_forbid_env_variables_via_subscript():
    code = """os.environ["S3_SOMETHING"]"""
    expected = {"1:11 FEP001 environment variable does not match any allowed pattern"}
    assert _results(code, ["AWS_.*"]) == expected


def test_forbid_env_variables_via_get():
    code = """os.environ.get("S3_SOMETHING")"""
    expected = {"1:15 FEP001 environment variable does not match any allowed pattern"}
    assert _results(code, ["AWS_.*"]) == expected


def test_forbid_env_variables_via_getenv():
    code = """os.getenv("S3_SOMETHING")"""
    expected = {"1:10 FEP001 environment variable does not match any allowed pattern"}
    assert _results(code, ["AWS_.*"]) == expected


def test_allow_matching_env_variables_via_subscript():
    code = """os.environ["AWS_ACCESS_KEY_ID"]"""
    expected = set()
    assert _results(code, ["AWS_.*"]) == expected


def test_allow_matching_env_variables_via_get():
    code = """os.environ.get("AWS_ACCESS_KEY_ID")"""
    expected = set()
    assert _results(code, ["AWS_.*"]) == expected


def test_allow_matching_env_variables_via_getenv():
    code = """os.getenv["AWS_ACCESS_KEY_ID"]"""
    expected = set()
    assert _results(code, ["AWS_.*"]) == expected
