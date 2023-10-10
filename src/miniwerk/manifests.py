"""Handle manifests"""
from typing import cast, List, Dict
import logging
import json
import uuid
from pathlib import Path

from libadvian.binpackers import uuid_to_b64

from .config import MWConfig, ProductSettings
from .jwt import get_issuer

LOGGER = logging.getLogger(__name__)


async def create_rasenmaeher_manifest() -> Path:
    """create manifest for RASENMAEHER"""
    config = MWConfig.singleton()
    manifest_path = config.manifests_base / "rasenmaeher" / "kraftwerk-rasenmaeher-init.json"
    manifest_dir = manifest_path.parent
    manifest_dir.mkdir(parents=True, exist_ok=True)
    if manifest_path.exists():
        LOGGER.info("{} already exists, not overwriting".format(manifest_path))
        return manifest_path
    manifest = {
        "dns": config.domain,
        "products": cast(Dict[str, Dict[str, str]], {}),
    }
    for productname in config.product_manifest_paths.keys():
        product_config = getattr(config, productname, None)
        if not product_config:
            LOGGER.error("No config for {}".format(productname))
            continue
        product_config = cast(ProductSettings, product_config)
        manifest["products"][productname] = {  # type: ignore[index]   # false positive
            "api": f"https://{productname}.{config.domain}:{product_config.api_port}/",
            "uri": f"https://{productname}.{config.domain}:5443/notthere",  # Not actually there
            "certcn": f"{productname}.{config.domain}",
        }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    LOGGER.info("Wrote {}".format(manifest_path))
    return manifest_path


async def create_product_manifest(productname: str) -> Path:
    """create manisfest for given product"""
    config = MWConfig.singleton()
    manifest_path = config.manifests_base / productname / "kraftwerk-init.json"
    manifest_dir = manifest_path.parent
    manifest_dir.mkdir(parents=True, exist_ok=True)
    if manifest_path.exists():
        LOGGER.info("{} already exists, not overwriting".format(manifest_path))
        return manifest_path

    issuer = await get_issuer()
    issuer.config.lifetime = 3600 * 24  # 24h
    token = issuer.issue(
        {
            "sub": f"{productname}.{config.domain}",
            "csr": True,
            "nonce": uuid_to_b64(uuid.uuid4()),
        }
    )
    rm_port = config.rasenmaeher.api_port
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
        "product": {"dns": f"{productname}.{config.domain}"},
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    LOGGER.info("Wrote {}".format(manifest_path))
    return manifest_path


async def create_all_product_manifests() -> List[Path]:
    """Handle all products"""
    config = MWConfig.singleton()
    ret = []
    for productname in config.product_manifest_paths.keys():
        product_config = getattr(config, productname, None)
        if not product_config:
            LOGGER.error("No config for {}".format(productname))
            continue
        ret.append(await create_product_manifest(productname))
    return ret
