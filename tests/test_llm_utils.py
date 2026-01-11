import pytest
import json
from src.llm_utils import LLMUtils

def test_parse_json_response_with_markdown():
    utils = LLMUtils()
    response = """
    Here is the data:
    ```json
    {"name": "Test Uni", "score": 80}
    ```
    """
    parsed = utils.parse_json_response(response)
    assert parsed["name"] == "Test Uni"
    assert parsed["score"] == 80

def test_parse_json_response_plain():
    utils = LLMUtils()
    response = '{"key": "value"}'
    parsed = utils.parse_json_response(response)
    assert parsed["key"] == "value"

def test_parse_json_response_invalid():
    utils = LLMUtils()
    response = "This is not JSON"
    parsed = utils.parse_json_response(response)
    assert "error" in parsed
    assert parsed["raw"] == response
