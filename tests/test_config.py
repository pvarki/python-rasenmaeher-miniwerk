"""Test the config class"""
import logging

from miniwerk.config import MWConfig

LOGGER = logging.getLogger(__name__)


def test_defaults() -> None:
    """Test the config defaults"""
    cfg = MWConfig()  # type: ignore[call-arg]
    LOGGER.debug("cfg={}".format(cfg))
    assert cfg.ci is True
    assert cfg.domain == "pytest.pvarki.fi"
    assert cfg.subdomains == "mtls"
    assert cfg.products == "fake,tak"
    assert str(cfg.data_path) != "/data/persistent"
    assert cfg.le_email == "example@example.com"
    LOGGER.debug("cfg.fqdns={}".format(cfg.fqdns))
    assert set(cfg.fqdns) == {
        "mtls.tak.pytest.pvarki.fi",
        "tak.pytest.pvarki.fi",
        "mtls.fake.pytest.pvarki.fi",
        "fake.pytest.pvarki.fi",
        "mtls.pytest.pvarki.fi",
        "pytest.pvarki.fi",
    }


def test_singleton() -> None:
    """Test the singleton fetcher"""
    assert MWConfig._singleton is None  # pylint: disable=W0212
    cfg = MWConfig.singleton()
    # Check for the classvar
    assert MWConfig._singleton is not None  # pylint: disable=W0212
    assert cfg.ci is True
    assert cfg.domain == "pytest.pvarki.fi"
    # Remove the side-effect
    MWConfig._singleton = None  # pylint: disable=W0212
