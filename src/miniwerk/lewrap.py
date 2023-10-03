"""Wrap letsencrypt"""
from typing import List, Tuple
import logging
import asyncio

from .config import MWConfig

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
    LOGGER.debug("Calling create_subprocess_shell(({})".format(cmd))
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out = await asyncio.wait_for(process.communicate(), timeout=60)
    LOGGER.info(out)
    assert isinstance(process.returncode, int)  # at this point it is, keep mypy happy

    return process.returncode, args
