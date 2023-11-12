"""Test the config class"""
import logging

import pytest

from miniwerk.config import MWConfig, KeyType

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
    assert cfg.keytype is KeyType.ECDSA


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


def test_sub_config_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test with modified config of product settings via env"""
    with monkeypatch.context() as mpatch:
        mpatch.setenv("MW_RASENMAEHER__API_PORT", "4439")
        mpatch.setenv("MW_KEYTYPE", "rsa")
        cfg = MWConfig()  # type: ignore[call-arg]
        LOGGER.debug("cfg={}".format(cfg))
        assert cfg.rasenmaeher.api_port == 4439  # pylint: disable=E1101  # false positive
        assert cfg.keytype is KeyType.RSA
