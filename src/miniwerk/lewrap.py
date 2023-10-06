"""Wrap letsencrypt"""
from typing import List, Tuple
import logging
from pathlib import Path

from .config import MWConfig
from .helpers import certs_copy, call_cmd

LOGGER = logging.getLogger(__name__)


async def call_certbot(config: MWConfig) -> Tuple[int, List[str]]:
    """Construct Certbot command and call the entrypoint, returns the args for easier unit testing"""
    args: List[str] = [
        "certonly",
        "--non-interactive",
        "--standalone",
        "--expand",
        "--keep-until-expiring",
        "--config-dir",
        str(config.le_config_path),
        "--work-dir",
        str(config.le_work_path),
        "--cert-name",
        config.le_cert_name,
        "--agree-tos",
        "--no-eff-email",
        "-m",
        config.le_email,
        "--domains",
        ",".join(config.fqdns),
    ]
    if config.le_test:
        args.append("--staging")

    if config.ci:
        LOGGER.info("Running under CI, not actually calling certbot")
        return 0, args

    cmd = "certbot " + " ".join(args)
    return await call_cmd(cmd), args


async def get_le_certs() -> Path:
    """Get certs from LE, copy them to the configured path, return configured path"""
    config = MWConfig.singleton()
    retcode, _ = await call_certbot(config)
    if retcode != 0:
        raise RuntimeError("Certbot returned error")
    copydir = config.le_copy_path / config.le_cert_name
    certs_copy(copydir, config.le_cert_dir)
    return copydir
