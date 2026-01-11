import pytest
from src.tools import WebSearch, RankingCalculator
from unittest.mock import MagicMock

def test_web_search_mocked(mocker):
    # Mocking duckduckgo_search at the point of use
    mock_ddgs_class = mocker.patch("src.tools.DDGS")
    mock_instance = mock_ddgs_class.return_value.__enter__.return_value
    mock_instance.text.return_value = [
        {"title": "Result 1", "href": "http://example.com/1", "body": "Snippet 1"},
        {"title": "Result 2", "href": "http://example.com/2", "body": "Snippet 2"}
    ]
    
    search = WebSearch()
    results = search.search("test query")
    
    assert len(results) == 2
    assert results[0]["title"] == "Result 1"
    assert results[0]["link"] == "http://example.com/1"

def test_ranking_calculator_llm(mocker):
    # Mocking LLMUtils
    mock_llm = mocker.patch("src.llm_utils.llm")
    mock_llm.generate_response.return_value = '{"score": 95, "reasoning": "Strong match"}'
    mock_llm.parse_json_response.return_value = {"score": 95, "reasoning": "Strong match"}
    
    ranker = RankingCalculator()
    result = ranker.calculate_match("Student profile", "Target description")
    
    assert result["score"] == 95
    assert "Strong match" in result["reasoning"]
