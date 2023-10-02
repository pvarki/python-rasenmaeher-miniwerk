"""Wrap letsencrypt"""
from typing import List
import logging

from certbot.main import main as certbot_main

from .config import MWConfig

LOGGER = logging.getLogger(__name__)


def call_certbot(config: MWConfig) -> List[str]:
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
        return args

    LOGGER.debug("Calling certbot_main({})".format(args))
    # FIXME: This overrides root logger level to debug (whyyyy)
    #        we probably are better off just launching a shell afterall
    certbot_main(args)
    return args
