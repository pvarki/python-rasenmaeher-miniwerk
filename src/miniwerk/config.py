"""Configuration"""
from __future__ import annotations
from typing import ClassVar, Optional, List, Dict
from pathlib import Path
from enum import StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KeyType(StrEnum):
    """Valid key types for certbot/mkcert"""

    RSA = "rsa"
    ECDSA = "ecdsa"


class ProductSettings(BaseSettings):
    """Configs for each product"""

    api_host: str = Field(description="API hostname (prefix)", default="")
    api_port: int = Field(description="port for the API")
    api_base: str = Field(description="base url for the API", default="/")
    user_host: str = Field(description="user hostname (prefix)", default="")
    user_port: int = Field(description="port for the normal users")
    user_base: str = Field(description="base url for normal users", default="/")

    model_config = SettingsConfigDict(extra="ignore")


class MWConfig(BaseSettings):
    """Config for MiniWerk"""

    # Things you must or should define
    domain: str = Field(description="Domain under which we operate")
    le_email: str = Field(description="email given to letsencrypt")
    le_test: bool = Field(default=True, description="Use LE staging/test env")
    subdomains: str = Field(default="mtls", description="Comma separated list of extra subdomains to get certs for")
    products: str = Field(
        default="fake,tak,bl,rmmtx",
        description="Comma separated list of products to create manifests and get subdomains for",
    )
    fake: ProductSettings = Field(
        description="Setting for fakeproduct integration API",
        default_factory=lambda: ProductSettings(api_host="fake", user_host="fake", api_port=4626, user_port=4626),
    )
    tak: ProductSettings = Field(
        description="Setting for TAK integration API",
        default_factory=lambda: ProductSettings(api_host="tak", user_host="tak", api_port=4626, user_port=8443),
    )
    rasenmaeher: ProductSettings = Field(
        description="Setting for RASENMAEHER API", default_factory=lambda: ProductSettings(api_port=443, user_port=443)
    )
    bl: ProductSettings = Field(
        description="Setting for BattleLog integration API",
        default_factory=lambda: ProductSettings(api_host="bl", user_host="bl", api_port=4626, user_port=4626),
    )
    rmmtx: ProductSettings = Field(
        description="Setting for MediaMTX integration API",
        default_factory=lambda: ProductSettings(api_host="rmmtx", user_host="rmmtx", api_port=4626, user_port=4626),
    )

    le_cert_name: str = Field(default="rasenmaeher", description="--cert-name for LE, used to determine directory name")
    le_copy_path: Path = Field(default="/le_certs", description="Where to copy letsencrypt certs and keys")
    data_path: Path = Field(default="/data/persistent", description="Where do we keep our data")
    manifests_base: Path = Field(
        default="/pvarkishares", description="Path for manifests etc, each product gets a subdir"
    )

    mkcert: bool = Field(default=False, description="Use mkcert instead of certbot")
    ci: bool = Field(default=False, alias="CI", description="Are we running in CI")
    keytype: KeyType = Field(default="ecdsa", description="Which key types to use, rsa or ecdsa (default)")
    model_config = SettingsConfigDict(env_prefix="mw_", env_file=".env", extra="ignore", env_nested_delimiter="__")
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
        for proddomain in [f"{prod.strip()}.{self.domain}" for prod in (str(self.products).split(",") + ["kc"])]:
            ret.append(proddomain)
            ret += [f"{subd.strip()}.{proddomain}" for subd in str(self.subdomains).split(",")]
        ret.append(self.domain)
        return ret

    @property
    def product_manifest_paths(self) -> Dict[str, Path]:
        """Paths for product manifests keyed by product"""
        return {prod.strip(): self.manifests_base / prod.strip() for prod in str(self.products).split(",")}
