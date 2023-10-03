"""Handle manifests"""
import logging
import json
import uuid
from pathlib import Path

from libadvian.binpackers import uuid_to_b64

from .config import MWConfig
from .jwt import get_issuer

LOGGER = logging.getLogger(__name__)


async def create_rasenmaeher_manifest() -> Path:
    """create manifest for RASENMAEHER"""
    config = MWConfig.singleton()
    manifest_path = config.manifests_path / "kraftwerk-rasenmaeher-init.json"
    manifest_dir = manifest_path.parent
    manifest_dir.mkdir(parents=True, exist_ok=True)
    if manifest_path.exists():
        LOGGER.info("{} already exists, not overwriting".format(manifest_path))
        return manifest_path
    manifest = {
        "dns": config.domain,
        "products": {
            "fake": {
                "api": f"https://fake.{config.domain}:{config.product_https_port}/",
                "uri": f"https://fake.{config.domain}:5443/",  # Not actually there
                "certcn": f"fake.{config.domain}",
            }
        },
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


async def create_fakeproduct_manifest() -> Path:
    """create manisfest for fakeproduct"""
    config = MWConfig.singleton()
    manifest_path = config.manifests_path / "kraftwerk-init.json"
    manifest_dir = manifest_path.parent
    manifest_dir.mkdir(parents=True, exist_ok=True)
    if manifest_path.exists():
        LOGGER.info("{} already exists, not overwriting".format(manifest_path))
        return manifest_path

    issuer = await get_issuer()
    issuer.config.lifetime = 3600 * 24  # 24h
    token = issuer.issue(
        {
            "sub": "fakeproduct",
            "csr": True,
            "nonce": uuid_to_b64(uuid.uuid4()),
        }
    )
    rm_port = config.rm_https_port
    if rm_port != 443:
        rm_uri = f"https://{config.domain}:{rm_port}/"
    else:
        rm_uri = f"https://{config.domain}/"
    mtls_uri = rm_uri.replace("https://", "https://mtls.")
    manifest = {
        "rasenmaeher": {
            "init": {"base_uri": rm_uri, "csr_jwt": token},
            "mtls": {"base_uri": mtls_uri},
        },
        "product": {"dns": f"fake.{config.domain}"},
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path
