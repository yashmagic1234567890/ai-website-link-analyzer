import pytest

from app.utils.url_validator import validate_url


def test_valid_website():
    assert validate_url("https://example.com") == "https://example.com"


def test_block_localhost():
    with pytest.raises(ValueError, match="Localhost URLs are not allowed"):
        validate_url("http://localhost")


def test_block_private_ip():
    with pytest.raises(ValueError, match="Private or reserved IP addresses are not allowed"):
        validate_url("http://192.168.1.1")


def test_block_unsupported_scheme():
    with pytest.raises(ValueError, match="Only HTTP and HTTPS URLs are allowed"):
        validate_url("ftp://example.com")


def test_block_nonstandard_port():
    with pytest.raises(ValueError, match="Only ports 80 and 443 are allowed"):
        validate_url("https://example.com:8080")