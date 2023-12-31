"""pytest automagics"""
from typing import Generator
import logging
from pathlib import Path

import pytest
from libadvian.logging import init_logging
from libadvian.testhelpers import nice_tmpdir_ses, monkeysession  # pylint: disable=W0611


init_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


# pylint: disable=W0621
@pytest.fixture(autouse=True, scope="session")
def default_env(monkeysession: pytest.MonkeyPatch, nice_tmpdir_ses: str) -> Generator[None, None, None]:
    """Setup some default environment variables"""
    datadir = Path(nice_tmpdir_ses) / "data"
    manifests_path = Path(nice_tmpdir_ses) / "pvarkishares"
    with monkeysession.context() as mpatch:
        mpatch.setenv("CI", "true")
        mpatch.setenv("MW_MANIFESTS_BASE", str(manifests_path))
        mpatch.setenv("MW_DATA_PATH", str(datadir))
        mpatch.setenv("MW_DOMAIN", "pytest.pvarki.fi")
        mpatch.setenv("MW_LE_EMAIL", "example@example.com")
        yield None
