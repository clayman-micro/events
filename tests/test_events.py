from events import __version__


def test_version():
    """Test current app version."""
    assert __version__ == '0.1.0'  # act
