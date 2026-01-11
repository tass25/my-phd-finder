import traceback
from tests.test_tools import test_web_search_mocked
from unittest.mock import MagicMock

class Mocker:
    def patch(self, path):
        import unittest.mock
        return unittest.mock.patch(path)

try:
    mocker = Mocker()
    test_web_search_mocked(mocker)
    print("Test passed!")
except Exception as e:
    print("Test failed!")
    traceback.print_exc()
