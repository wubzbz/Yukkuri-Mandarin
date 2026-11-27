import dataclasses

import pytest

from yukkurimandarin.settings import DEFAULT_CONFIG, NonHanziModes


def test_default_config():
    assert DEFAULT_CONFIG.database is None
    assert DEFAULT_CONFIG.non_hanzi is None


def test_non_hanzi_modes_fallback():
    modes = NonHanziModes(global_mode="keep")
    assert modes.en_mode == "keep"
    assert modes.ja_mode == "keep"
    assert modes.pc_mode == "keep"
    assert modes.other_mode == "keep"


def test_non_hanzi_modes_override():
    modes = NonHanziModes(pc_mode="replace", pc_replace="X")
    assert modes.pc_mode == "replace"
    assert modes.pc_replace == "X"
    assert modes.en_mode == "ignore"
    assert modes.en_replace == ""


def test_config_replace():
    config = dataclasses.replace(DEFAULT_CONFIG, database="mine.db")
    assert config.database == "mine.db"
    assert DEFAULT_CONFIG.database is None


def test_config_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        DEFAULT_CONFIG.database = "x"  # type: ignore[misc]
