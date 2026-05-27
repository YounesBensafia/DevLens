import pytest

from devlens.core.llm_judge import parse_llm_response, build_llm_prompt


def test_parse_valid_json():
    response = (
        '{"function_names_clear": true, "undocumented_side_effects": false, '
        '"junior_friendly": true, "single_responsibility": true, '
        '"magic_values": false, "explanation": "Clean code."}'
    )
    result = parse_llm_response(response)
    assert result.function_names_clear is True
    assert result.undocumented_side_effects is False
    assert result.junior_friendly is True
    assert result.single_responsibility is True
    assert result.magic_values is False
    assert result.llm_score > 90.0
    assert result.explanation == "Clean code."


def test_parse_with_markdown_fence():
    response = (
        "```json\n"
        '{"function_names_clear": false, "undocumented_side_effects": true, '
        '"junior_friendly": false, "single_responsibility": false, '
        '"magic_values": true, "explanation": "Hard to follow."}\n'
        "```"
    )
    result = parse_llm_response(response)
    assert result.function_names_clear is False
    assert result.undocumented_side_effects is True
    assert result.junior_friendly is False
    assert result.single_responsibility is False
    assert result.magic_values is True
    assert result.llm_score < 30.0


def test_parse_garbage_text():
    result = parse_llm_response("this is not json at all")
    assert result.llm_score == 50.0
    assert result.function_names_clear is True
    assert result.explanation == "Could not parse LLM response."


def test_parse_missing_fields():
    response = '{"function_names_clear": false}'
    result = parse_llm_response(response)
    assert result.function_names_clear is False
    assert result.junior_friendly is True
    assert result.llm_score == pytest.approx(76.7, abs=0.1)


def test_build_llm_prompt_includes_source():
    source = "def hello(): pass"
    prompt = build_llm_prompt(source, "/dev/null/test.py")
    assert "def hello(): pass" in prompt
    assert "test.py" in prompt
    assert "function_names_clear" in prompt
