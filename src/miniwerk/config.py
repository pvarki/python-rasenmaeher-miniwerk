"""Configuration"""
from __future__ import annotations
from typing import ClassVar, Optional
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MWConfig(BaseSettings):
    """Config for MiniWerk"""

    # Things you must or should define
    domain: str = Field(description="Domain under which we operate")
    le_email: str = Field(description="email given to letsencrypt")
    le_test: bool = Field(default=True, description="Use LE staging/test env")

    subdomains: str = Field(
        default="fake,mtls", description="Comma separated list of extra subdomains to get certs for"
    )
    le_path: Path = Field(default="/le_certs", description="Where to copy letsencrypt certs and keys")
    data_path: Path = Field(default="/data/persistent", description="Where do we keep our data")
    manifests_path: Path = Field(default="/pvarki", description="Path for manifests etc")
    rm_https_port: int = Field(default=443, description="Port for RASENMAEHERs https")
    product_https_port: int = Field(default=4625, description="Port for product integration api")

    model_config = SettingsConfigDict(env_prefix="mw_", env_file=".env", extra="ignore")
    _singleton: ClassVar[Optional[MWConfig]] = None

    @classmethod
    def singleton(cls) -> MWConfig:
        """Return singleton"""
        if not MWConfig._singleton:
            MWConfig._singleton = MWConfig()  # type: ignore[call-arg]
        return MWConfig._singleton
