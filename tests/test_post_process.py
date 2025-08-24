import pytest

import yukkurimandarin.post_process as t

@pytest.mark.parametrize("input, expected", [
    ("'ゆっく/り_シていってね。", "ゆっくりしていってね。")
])
def test_post_process(input, expected):
    assert t.post_process(input, True) == expected