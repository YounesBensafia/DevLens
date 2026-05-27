from pathlib import Path

from devlens.core.metrics import analyze_file

FIXTURES = Path(__file__).parent / "fixtures"


def test_analyze_empty_file():
    result = analyze_file(str(FIXTURES / "empty.py"))
    assert result.error == "empty file"
    assert result.comprehension_score == 0.0


def test_analyze_syntax_error(tmp_path):
    bad = tmp_path / "bad_syntax.py"
    bad.write_text("def foo(:\n    pass\n")
    result = analyze_file(str(bad))
    assert result.error is None
    assert result.cyclomatic_complexity == 0


def test_cc_simple_function(tmp_path):
    src = tmp_path / "simple.py"
    src.write_text("def f():\n    pass\n")
    result = analyze_file(str(src))
    assert result.max_cyclomatic_complexity == 1
    assert len(result.functions) == 1
    assert result.functions[0].name == "f"


def test_cc_conditional(tmp_path):
    src = tmp_path / "conditional.py"
    src.write_text(
        "def decide(x):\n"
        "    if x > 0:\n"
        "        return 'positive'\n"
        "    elif x == 0:\n"
        "        return 'zero'\n"
        "    else:\n"
        "        return 'negative'\n"
    )
    result = analyze_file(str(src))
    assert result.max_cyclomatic_complexity == 3
    assert result.cyclomatic_complexity == 3.0


def test_cc_nested(tmp_path):
    src = tmp_path / "nested.py"
    src.write_text(
        "def nested(a, b, c):\n"
        "    if a:\n"
        "        for i in b:\n"
        "            if i > 0:\n"
        "                while c:\n"
        "                    print(i)\n"
        "    return None\n"
    )
    result = analyze_file(str(src))
    assert result.max_cyclomatic_complexity == 5
    assert result.max_nesting_depth >= 3


def test_docstring_ratio_all():
    result = analyze_file(str(FIXTURES / "well_documented.py"))
    assert result.docstring_ratio == 1.0
    assert result.error is None


def test_docstring_ratio_none():
    result = analyze_file(str(FIXTURES / "no_docs_but_clean.py"))
    assert result.docstring_ratio == 0.0
    assert result.error is None


def test_bad_name_detection():
    result = analyze_file(str(FIXTURES / "spaghetti.py"))
    assert result.bad_name_ratio > 0.3
    assert result.max_cyclomatic_complexity > 5


def test_good_name_detection():
    result = analyze_file(str(FIXTURES / "well_documented.py"))
    assert result.bad_name_ratio < 0.1
    assert result.error is None


def test_comprehension_score_well_documented_is_high():
    result = analyze_file(str(FIXTURES / "well_documented.py"))
    assert result.comprehension_score > 60.0
