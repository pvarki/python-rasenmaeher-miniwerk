"""Test mkcert wrapper"""

import logging

import pytest

from miniwerk.config import MWConfig
from miniwerk.mkcwrap import call_mkcert

LOGGER = logging.getLogger(__name__)


def check_common_args(args: list[str], config: MWConfig) -> None:
    """Common checks"""
    LOGGER.debug(f"args={args}")
    assert " ".join(config.fqdns) in args


@pytest.mark.parametrize("ktype", ["ecdsa", "rsa"])
@pytest.mark.asyncio
async def test_rsa_config(ktype: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test with modified config"""
    with monkeypatch.context() as mpatch:
        mpatch.setenv("MW_KEYTYPE", ktype)
        config = MWConfig()  # type: ignore[call-arg]
        LOGGER.debug(f"config={config}")
        assert config.ci is True
        _, args = await call_mkcert(config)
        check_common_args(args, config)
        if ktype == "rsa":
            assert "--ecdsa" not in args
        if ktype == "ecdsa":
            assert "--ecdsa" in args
