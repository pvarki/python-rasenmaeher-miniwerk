"""CLI entrypoints for miniwerk"""
from typing import Any
import logging
import asyncio

import click
from libadvian.logging import init_logging

from miniwerk import __version__
from miniwerk.config import MWConfig
from miniwerk.lewrap import call_certbot
from miniwerk.manifests import create_rasenmaeher_manifest, create_fakeproduct_manifest

LOGGER = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
@click.option("-l", "--loglevel", help="Python log level, 10=DEBUG, 20=INFO, 30=WARNING, 40=CRITICAL", default=30)
@click.option("-v", "--verbose", count=True, help="Shorthand for info/debug loglevel (-v/-vv)")
def cligrp(loglevel: int, verbose: int) -> None:
    """Minimal KRAFTWERK amulation to be able to run a RASENMAEHER+products deployment on any VM"""
    if verbose == 1:
        loglevel = 20
    if verbose >= 2:
        loglevel = 10
    init_logging(loglevel)
    LOGGER.setLevel(loglevel)


@cligrp.command(name="config")
def dump_config() -> None:
    """Show the resolved config as JSON"""
    click.echo(MWConfig.singleton().model_dump_json())


@cligrp.command(name="certs")
@click.pass_context
def get_certs(ctx: Any) -> None:
    """Get and/or renew certs based on configuration"""

    async def call() -> int:
        """Do the call"""
        retcode, _ = await call_certbot(MWConfig.singleton())
        return retcode

    ctx.exit(asyncio.get_event_loop().run_until_complete(call()))


@cligrp.command(name="manifests")
@click.pass_context
def create_manifests(ctx: Any) -> None:
    """Create manifests"""

    async def call() -> int:
        """Do the call"""
        await create_rasenmaeher_manifest()
        await create_fakeproduct_manifest()
        return 0

    ctx.exit(asyncio.get_event_loop().run_until_complete(call()))


@cligrp.command(name="init")
@click.pass_context
def do_full_init(ctx: Any) -> None:
    """Create manifests, get certs, everything that is needed"""

    async def call() -> int:
        """Do the call"""
        await create_rasenmaeher_manifest()
        await create_fakeproduct_manifest()
        retcode, _ = await call_certbot(MWConfig.singleton())
        return retcode

    ctx.exit(asyncio.get_event_loop().run_until_complete(call()))


def miniwerk_cli() -> None:
    """cli entrypoint"""
    init_logging(logging.WARNING)
    cligrp()  # pylint: disable=no-value-for-parameter
