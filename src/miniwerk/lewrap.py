"""Wrap letsencrypt"""
from typing import List, Tuple
import logging
import asyncio
from pathlib import Path

from .config import MWConfig
from .jwt import PRIVDIR_MODE

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
    out, err = await asyncio.wait_for(process.communicate(), timeout=60)
    if err:
        LOGGER.warning(err)
    LOGGER.info(out)
    assert isinstance(process.returncode, int)  # at this point it is, keep mypy happy
    if process.returncode != 0:
        LOGGER.error("{} returned nonzero code: {} (process: {})".format(cmd, process.returncode, process))
        LOGGER.error(err)
        LOGGER.error(out)

    return process.returncode, args


async def get_certs() -> Path:
    """Get certs from LE, copy them to the configured path, return configured path"""
    config = MWConfig.singleton()
    retcode, _ = await call_certbot(config)
    if retcode != 0:
        raise RuntimeError("Certbot returned error")
    copydir = config.le_copy_path / config.le_cert_name
    copydir.mkdir(parents=True, exist_ok=True)
    copydir.chmod(PRIVDIR_MODE)
    for fpth in config.le_cert_dir.iterdir():
        if not fpth.name.endswith(".pem"):
            LOGGER.debug("Skipping {}".format(fpth))
            continue
        absfpth = fpth.resolve(strict=True)
        LOGGER.debug("{} resolved to {}".format(fpth, absfpth))
        tgtpth = copydir / fpth.name
        tgtpth.write_bytes(absfpth.read_bytes())
        LOGGER.info("Wrote {}".format(tgtpth))
    return copydir
