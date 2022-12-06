import os
import pytest
from src.common.utils import resp_fetcher

@pytest.mark.parametrize("word",['betray', 'head', 'convert'])
def test_resp_fetcher(word):
    resp_fetcher(word)

    

