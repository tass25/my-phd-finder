import pytest
from src.tools import WebSearch
from unittest.mock import MagicMock
import duckduckgo_search

def test_web_search_mocked():
    import unittest.mock
    with unittest.mock.patch("duckduckgo_search.DDGS") as mock_ddgs:
        mock_instance = mock_ddgs.return_value.__enter__.return_value
        mock_instance.text.return_value = [
            {"title": "Result 1", "href": "http://example.com/1", "body": "Snippet 1"}
        ]
        
        search = WebSearch()
        results = search.search("test query")
        print(f"Results: {results}")
        assert len(results) == 1

if __name__ == "__main__":
    try:
        test_web_search_mocked()
        print("Test passed!")
    except Exception as e:
        import traceback
        traceback.print_exc()
