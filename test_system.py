import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analyzer import analyze_code


def test_valid_code():
    result = analyze_code("def add(a, b):\n    return a + b\n")
    assert result["valid"] is True
    assert result["metrics"]["functions"] == 1
    assert result["metrics"]["lines_of_code"] == 2


def test_invalid_code():
    result = analyze_code("def broken(:\n    pass")
    assert result["valid"] is False
    assert "Syntax error" in result["error"]


def test_complex_code_generates_issue():
    source = '''def check(x):\n    if x > 0:\n        if x > 1:\n            if x > 2:\n                if x > 3:\n                    return True\n    return False\n'''
    result = analyze_code(source)
    assert result["valid"] is True
    assert result["metrics"]["max_nesting"] >= 4
    assert len(result["issues"]) >= 1


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
