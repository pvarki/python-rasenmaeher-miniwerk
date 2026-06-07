"""Test manifest creation"""

import json
import logging
from pathlib import Path

import pytest

from miniwerk.config import MWConfig
from miniwerk.jwt import get_verifier
from miniwerk.manifests import create_all_product_manifests, create_rasenmaeher_manifest

LOGGER = logging.getLogger(__name__)


def check_jwt_pubkey(pth: Path) -> None:
    """Check JWT pubkey has been copied"""
    pubkeypth = pth.parent / "publickeys" / "kraftwerk.pub"
    assert pubkeypth.exists()


@pytest.mark.asyncio
async def test_rm_manifest() -> None:
    """Check RASENMAEHER manifest creation"""
    config = MWConfig.singleton()
    pth = await create_rasenmaeher_manifest()
    check_jwt_pubkey(pth)
    manifest = json.loads(pth.read_text(encoding="utf-8"))
    LOGGER.debug(f"manifest={manifest}")
    assert manifest["dns"] == config.domain
    assert "fake" in manifest["products"]
    assert "tak" in manifest["products"]
    assert "certcn" in manifest["products"]["tak"]
    assert manifest["products"]["tak"]["certcn"] == "tak.pytest.pvarki.fi"


@pytest.mark.asyncio
async def test_fakeproduct_manifest() -> None:
    """Check fakeproduct manifest"""
    config = MWConfig.singleton()
    pth = next(cand for cand in await create_all_product_manifests() if "/fake/" in str(cand))
    check_jwt_pubkey(pth)
    manifest = json.loads(pth.read_text(encoding="utf-8"))
    LOGGER.debug(f"manifest={manifest}")
    verifier = await get_verifier()
    claims = verifier.decode(manifest["rasenmaeher"]["init"]["csr_jwt"])
    LOGGER.debug(f"claims={claims}")
    assert claims["csr"]
    assert claims["nonce"]
    assert f"mtls.{config.domain}" in manifest["rasenmaeher"]["mtls"]["base_uri"]


@pytest.mark.asyncio
async def test_takanalyzer_manifest() -> None:
    """Check takanalyzer gets an identity (CSR JWT) + manifest with takanalyzer hosts"""
    config = MWConfig.singleton()
    pth = next(cand for cand in await create_all_product_manifests() if "/takanalyzer/" in str(cand))
    check_jwt_pubkey(pth)
    manifest = json.loads(pth.read_text(encoding="utf-8"))
    LOGGER.debug(f"manifest={manifest}")
    verifier = await get_verifier()
    claims = verifier.decode(manifest["rasenmaeher"]["init"]["csr_jwt"])
    LOGGER.debug(f"claims={claims}")
    assert claims["csr"]
    assert claims["sub"] == f"takanalyzer.{config.domain}"
    assert manifest["product"]["dns"] == f"takanalyzer.{config.domain}"
    assert f"takanalyzer.{config.domain}" in manifest["product"]["api"]
    assert f"takanalyzer.{config.domain}" in manifest["product"]["uri"]
