import pytest
from typing import Callable
from unittest.mock import mock_open
from urls import get_valid_http_urls_from_file


@pytest.fixture(params=[
    ("https://test.com\nhttp://site.ru", ["https://test.com", "http://site.ru"]),
    ("ftp://invalid.com\njust text", []),
    ("", []),
])
def file_content_case(request):
    return request.param


def mock_open_with_content(content: str) -> Callable:
    return mock_open(read_data=content)


def test_get_valid_urls_success(monkeypatch, file_content_case):
    content, expected = file_content_case
    m_open = mock_open_with_content(content)
    monkeypatch.setattr("builtins.open", m_open)

    result = get_valid_http_urls_from_file("fake.txt")
    assert result == expected


def mock_open_raising_error(error: Exception) -> Callable:
    m = mock_open()
    m.side_effect = error
    return m


@pytest.mark.parametrize("error_to_raise, expected_exception, match_regex", [
    (FileNotFoundError(), FileNotFoundError, None),
    (OSError("Disk failure"), IOError, r"Failed to read file: Disk failure"),
])
def test_get_valid_urls_errors(monkeypatch, error_to_raise, expected_exception, match_regex):
    m_open = mock_open_raising_error(error_to_raise)
    monkeypatch.setattr("builtins.open", m_open)

    with pytest.raises(expected_exception, match=match_regex):
        get_valid_http_urls_from_file("error_file.txt")


def custom_mock_open_with_content(content: str) -> Callable:
    class MockFile:
        def __init__(self, *args, **kwargs):
            self.lines = iter(content.splitlines(keepends=True))

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def __iter__(self):
            return self

        def __next__(self):
            return next(self.lines)

    return MockFile


def custom_mock_open_raising_error(error: Exception) -> Callable:
    def mock_file_error(*args, **kwargs):
        raise error

    return mock_file_error


def test_custom_mocks(monkeypatch):
    monkeypatch.setattr("builtins.open", custom_mock_open_with_content("https://ok.ru"))
    assert get_valid_http_urls_from_file("path") == ["https://ok.ru"]

    error_msg = "Permission denied"
    monkeypatch.setattr("builtins.open", custom_mock_open_raising_error(OSError(error_msg)))
    with pytest.raises(IOError, match=f"Failed to read file: {error_msg}"):
        get_valid_http_urls_from_file("path")
