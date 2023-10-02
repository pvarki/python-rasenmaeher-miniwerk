"""CLI entrypoints for miniwerk"""
import logging

import click
from libadvian.logging import init_logging

from miniwerk import __version__
from miniwerk.config import MWConfig
from miniwerk.lewrap import call_certbot

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
def get_certs() -> None:
    """Get and/or renew certs based on configuration"""
    call_certbot(MWConfig.singleton())


def miniwerk_cli() -> None:
    """cli entrypoint"""
    init_logging(logging.WARNING)
    cligrp()  # pylint: disable=no-value-for-parameter
