"""Tests for shared utilities."""

from __future__ import annotations

import pytest

from vchasno._utils import UNSET, collect_params, collect_update, validate_id


class TestCollectParams:
    def test_drops_none(self):
        assert collect_params(a=None, b=1) == {"b": 1}

    def test_drops_unset(self):
        assert collect_params(a=UNSET, b=1) == {"b": 1}

    def test_keeps_values(self):
        assert collect_params(a="x", b=0, c=False) == {"a": "x", "b": 0, "c": False}

    def test_empty(self):
        assert collect_params() == {}


class TestCollectUpdate:
    def test_preserves_none(self):
        assert collect_update(a=None, b=UNSET) == {"a": None}

    def test_drops_unset_only(self):
        assert collect_update(a=UNSET) == {}

    def test_keeps_false_and_zero(self):
        assert collect_update(a=False, b=0) == {"a": False, "b": 0}


class TestValidateId:
    def test_valid_uuid(self):
        assert validate_id("abc-123_DEF") == "abc-123_DEF"

    def test_rejects_path_traversal(self):
        with pytest.raises(ValueError):
            validate_id("../../etc/passwd")

    def test_rejects_slashes(self):
        with pytest.raises(ValueError):
            validate_id("abc/def")

    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            validate_id("")
