"""Test the LW wrapper (what little we can)"""
from typing import List
import logging

import pytest

from miniwerk.lewrap import call_certbot
from miniwerk.config import MWConfig

LOGGER = logging.getLogger(__name__)


def check_common_args(args: List[str], config: MWConfig) -> None:
    """Common checks"""
    LOGGER.debug("args={}".format(args))
    assert ",".join(config.fqdns) in args
    assert "--no-eff-email" in args
    assert "--agree-tos" in args
    assert "--cert-name" in args
    assert args[0] == "certonly"
    assert config.le_email in args
    assert "rasenmaeher" in args


@pytest.mark.asyncio
async def test_default_config() -> None:
    """Test with default config"""
    config = MWConfig()  # type: ignore[call-arg]
    LOGGER.debug("config={}".format(config))
    assert config.ci is True
    _, args = await call_certbot(config)
    check_common_args(args, config)
    assert "--staging" in args


@pytest.mark.asyncio
async def test_live_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test with modified config"""
    with monkeypatch.context() as mpatch:
        mpatch.setenv("MW_LE_TEST", "false")
        config = MWConfig()  # type: ignore[call-arg]
        LOGGER.debug("config={}".format(config))
        assert config.ci is True
        _, args = await call_certbot(config)
        check_common_args(args, config)
        assert "--staging" not in args
