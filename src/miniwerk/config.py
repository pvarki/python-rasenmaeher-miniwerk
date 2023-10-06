"""Configuration"""
from __future__ import annotations
from typing import ClassVar, Optional, List
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

    le_cert_name: str = Field(default="rasenmaeher", description="--cert-name for LE, used to determine directory name")
    le_copy_path: Path = Field(default="/le_certs", description="Where to copy letsencrypt certs and keys")
    data_path: Path = Field(default="/data/persistent", description="Where do we keep our data")
    manifests_path: Path = Field(default="/pvarki", description="Path for manifests etc")
    rm_https_port: int = Field(default=443, description="Port for RASENMAEHERs https")
    product_https_port: int = Field(default=4625, description="Port for product integration api")

    mkcert: bool = Field(default=False, description="Use mkcert instead of certbot")
    ci: bool = Field(default=False, alias="CI", description="Are we running in CI")
    model_config = SettingsConfigDict(env_prefix="mw_", env_file=".env", extra="ignore")
    _singleton: ClassVar[Optional[MWConfig]] = None

    @classmethod
    def singleton(cls) -> MWConfig:
        """Return singleton"""
        if not MWConfig._singleton:
            MWConfig._singleton = MWConfig()  # type: ignore[call-arg]
        return MWConfig._singleton

    @property
    def le_config_path(self) -> Path:
        """LE configuration dir"""
        return self.data_path / "le" / "conf"

    @property
    def mkcert_path(self) -> Path:
        """mkcert certs dir"""
        return self.data_path / "mkcert"

    @property
    def le_work_path(self) -> Path:
        """LE work dir (doesn't seem to actually hold anything persistent)"""
        return self.data_path / "le" / "work"

    @property
    def le_cert_dir(self) -> Path:
        """The "live" dir for the cert we have, remember the "file" here are symlinks"""
        return self.le_config_path / "live" / self.le_cert_name

    @property
    def mk_cert_dir(self) -> Path:
        """The "live" dir for the cert we have"""
        return self.mkcert_path / self.le_cert_name

    @property
    def fqdns(self) -> List[str]:
        """Main domain and all subdomains and FQDNs"""
        ret = [f"{subd.strip()}.{self.domain}" for subd in str(self.subdomains).split(",")]
        ret.append(self.domain)
        return ret
