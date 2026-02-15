import pytest
from unittest.mock import patch, Mock, mock_open
from reader_html import ReaderHTML


@patch("reader_html.requests.get")
def test_make_request_success(mock_get):
    mock_response = Mock()
    mock_response.text = "<html>ok</html>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    reader = ReaderHTML("https://test.com/")
    result = reader._make_request("hello world")

    mock_get.assert_called_once_with("https://test.com/hello_world")
    assert result == "<html>ok</html>"


@patch("reader_html.Path.open", new_callable=mock_open, read_data="<html>local</html>")
def test_read_local_success(mock_file):
    reader = ReaderHTML("https://test.com/", use_local_html_file_instead=True)
    result = reader._read_local("hello world")

    assert result == "<html>local</html>"


def test_read_data_no_phrase():
    reader = ReaderHTML("https://test.com/")
    with pytest.raises(ValueError):
        reader.read_data()



