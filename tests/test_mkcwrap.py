"""Test mkcert wrapper"""
from typing import List
import logging

import pytest

from miniwerk.mkcwrap import call_mkcert
from miniwerk.config import MWConfig

LOGGER = logging.getLogger(__name__)


def check_common_args(args: List[str], config: MWConfig) -> None:
    """Common checks"""
    LOGGER.debug("args={}".format(args))
    assert " ".join(config.fqdns) in args


@pytest.mark.asyncio
async def test_default_config() -> None:
    """Test with default config"""
    config = MWConfig()  # type: ignore[call-arg]
    LOGGER.debug("config={}".format(config))
    assert config.ci is True
    _, args = await call_mkcert(config)
    check_common_args(args, config)
    assert "--ecdsa" in args


@pytest.mark.asyncio
async def test_rsa_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test with modified config"""
    with monkeypatch.context() as mpatch:
        mpatch.setenv("MW_KEYTYPE", "rsa")
        config = MWConfig()  # type: ignore[call-arg]
        LOGGER.debug("config={}".format(config))
        assert config.ci is True
        _, args = await call_mkcert(config)
        check_common_args(args, config)
        assert "--ecdsa" not in args
