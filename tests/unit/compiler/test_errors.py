"""Tests for CompilerError."""
import pytest

from extrudely.compiler.errors import CompilerError


def test_create_error():
    err = CompilerError("unsupported_plane", "SK001", "Bad plane")
    assert err.error_type == "unsupported_plane"
    assert err.location == "SK001"
    assert err.message == "Bad plane"
    assert "unsupported_plane" in str(err)

def test_is_exception():
    err = CompilerError("empty_geometry", "SK002", "No geometry")
    assert isinstance(err, Exception)

def test_can_raise_and_catch():
    with pytest.raises(CompilerError):
        raise CompilerError("test_error", "F001", "test message")
