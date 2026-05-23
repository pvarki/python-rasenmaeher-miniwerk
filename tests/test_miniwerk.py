"""Package level tests"""

from miniwerk import __version__


def test_version() -> None:
    """Make sure version matches expected"""
    assert __version__ == "1.8.2+260524"
