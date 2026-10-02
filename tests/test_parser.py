"""Tests for parsing LIBERO evaluation logs."""

import pytest
from src.parser import extract_balanced, parse_result_file


def test_extract_balanced_simple():
    text = "abc {'key': 'value'} def"
    result = extract_balanced(text, 0, "{", "}")
    assert result == "{'key': 'value'}"


def test_extract_balanced_nested():
    text = "x {'a': {'b': 1}} y"
    result = extract_balanced(text, 0, "{", "}")
    assert result == "{'a': {'b': 1}}"


def test_extract_balanced_missing():
    text = "no braces here"
    result = extract_balanced(text, 0, "{", "}")
    assert result is None


def test_extract_balanced_with_string():
    text = "prefix {'path': 'D:/x/y'} suffix"
    result = extract_balanced(text, 0, "{", "}")
    assert result == "{'path': 'D:/x/y'}"