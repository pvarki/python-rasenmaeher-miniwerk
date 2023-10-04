"""Test manifest creation"""
import logging
import json

import pytest

from miniwerk.config import MWConfig
from miniwerk.jwt import get_verifier
from miniwerk.manifests import create_fakeproduct_manifest, create_rasenmaeher_manifest

LOGGER = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_rm_manifest() -> None:
    """Check RASENMAEHER manifest creation"""
    config = MWConfig.singleton()
    pth = await create_rasenmaeher_manifest()
    manifest = json.loads(pth.read_text(encoding="utf-8"))
    LOGGER.debug("manifest={}".format(manifest))
    assert manifest["dns"] == config.domain


@pytest.mark.asyncio
async def test_fakeproduct_manifest() -> None:
    """Check fakeproduct manifest"""
    config = MWConfig.singleton()
    pth = await create_fakeproduct_manifest()
    manifest = json.loads(pth.read_text(encoding="utf-8"))
    LOGGER.debug("manifest={}".format(manifest))
    verifier = await get_verifier()
    claims = verifier.decode(manifest["rasenmaeher"]["init"]["csr_jwt"])
    LOGGER.debug("claims={}".format(claims))
    assert claims["csr"]
    assert claims["nonce"]
    assert f"mtls.{config.domain}" in manifest["rasenmaeher"]["mtls"]["base_uri"]
