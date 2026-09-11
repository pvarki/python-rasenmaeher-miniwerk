"""pytest automagics"""

import logging
from collections.abc import Generator
from pathlib import Path

import pytest
from libadvian.logging import init_logging
from libadvian.testhelpers import monkeysession, nice_tmpdir_ses  # noqa: F401  # pytest fixtures

from miniwerk.config import MWConfig

init_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.fixture(autouse=True, scope="session", params=["ecdsa", "rsa"])
def default_env(
    request: pytest.FixtureRequest, monkeysession: pytest.MonkeyPatch, nice_tmpdir_ses: str
) -> Generator[None, None, None]:
    """Setup some default environment variables"""
    MWConfig._singleton = None  # Make sure we do not have previous singleton
    datadir = Path(nice_tmpdir_ses) / "data"
    manifests_path = Path(nice_tmpdir_ses) / "pvarkishares"
    with monkeysession.context() as mpatch:
        mpatch.setenv("CI", "true")
        mpatch.setenv("MW_MANIFESTS_BASE", str(manifests_path))
        mpatch.setenv("MW_DATA_PATH", str(datadir))
        mpatch.setenv("MW_DOMAIN", "pytest.pvarki.fi")
        mpatch.setenv("MW_LE_EMAIL", "example@example.com")
        mpatch.setenv("MW_KEYTYPE", request.param)

        yield None
