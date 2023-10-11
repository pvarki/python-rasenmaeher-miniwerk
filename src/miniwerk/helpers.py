"""Helpers"""
import logging
import asyncio
from pathlib import Path
import subprocess  # nosec


from .jwt import PRIVDIR_MODE

LOGGER = logging.getLogger(__name__)


def certs_copy(copydir: Path, sourcedir: Path) -> None:
    """Copy certs"""
    copydir.mkdir(parents=True, exist_ok=True)
    copydir.chmod(PRIVDIR_MODE)
    for fpth in sourcedir.iterdir():
        if not fpth.name.endswith(".pem"):
            LOGGER.debug("Skipping {}".format(fpth))
            continue
        absfpth = fpth.resolve(strict=True)
        LOGGER.debug("{} resolved to {}".format(fpth, absfpth))
        tgtpth = copydir / fpth.name
        tgtpth.write_bytes(absfpth.read_bytes())
        LOGGER.info("Wrote {}".format(tgtpth))


async def call_cmd(cmd: str) -> int:
    """Do the boilerplate for calling cmd and reporting output/return code"""
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

    return process.returncode


def mkcert_ca_cert() -> Path:
    """get mkcert root CA cert"""
    caroot = Path(subprocess.check_output("mkcert -CAROOT", shell=True).decode("utf-8").strip())  # nosec
    return caroot / "rootCA.pem"
