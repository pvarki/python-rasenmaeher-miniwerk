# AGENTS.md — python-miniwerk

## Purpose
Minimal KRAFTWERK emulation for the Deploy App (RASENMAEHER) stack. miniwerk is the very
first service to start in the compose stack. It orchestrates TLS certificate provisioning
(Let's Encrypt in production, mkcert locally) and writes a per-product JSON manifest to
shared Docker volumes so every downstream service knows its domain, certificates, and secrets.
Nothing else can start until miniwerk is healthy.

## Stack & Key Technologies
- **Language:** Python 3.11
- **Framework:** Custom async (aiohttp-based)
- **Key libs:** libpvarki, cryptography, certbot / mkcert
- **Testing:** pytest, tox (65% minimum coverage)
- **Linting:** pre-commit, pylint
- **Container:** Docker multi-target (devel_shell, tox, production)
- **Port:** 80 (internal cert delivery)

## Development Setup
```bash
export DOCKER_BUILDKIT=1
# Linux:
export DOCKER_SSHAGENT="-v $SSH_AUTH_SOCK:$SSH_AUTH_SOCK -e SSH_AUTH_SOCK"
# macOS:
# export DOCKER_SSHAGENT="-v /run/host-services/ssh-auth.sock:/run/host-services/ssh-auth.sock -e SSH_AUTH_SOCK=/run/host-services/ssh-auth.sock"

docker build --ssh default --target devel_shell -t miniwerk:devel_shell .
docker create --name miniwerk_devel -v $(pwd):/app -p 80:80 \
  -it $(echo $DOCKER_SSHAGENT) miniwerk:devel_shell
docker start -i miniwerk_devel

# Key env vars:
# MW_LE_EMAIL       — Let's Encrypt account email
# MW_LE_TEST=true   — Use LE staging (local dev); false for production
# MW_MKCERT=true    — Use mkcert instead of LE (fully local, no DNS needed)
# MW_PRODUCTS       — Space-separated list of product names to provision
```

## Running Tests
```bash
# Via tox (CI)
docker build --ssh default --target tox -t miniwerk:tox .
docker run --rm -it -v $(pwd):/app $(echo $DOCKER_SSHAGENT) miniwerk:tox

# Direct pytest inside devel_shell
pytest tests/ -v --cov=miniwerk --cov-fail-under=65

# Pre-commit
pre-commit install --install-hooks
pre-commit run --all-files
```

## Code Conventions
- Async-first: use `aiohttp` / `asyncio`, not `requests`
- Follow pylint rules from root `pylintrc`

## Architecture Notes
**Startup order:** miniwerk MUST be healthy before cfssl, postgres, keycloak, or any product
service starts. The compose health-check dependency chain enforces this.

**Certificate modes:**
- `MW_MKCERT=true` — Fully local; uses mkcert to generate self-signed certs. No DNS required.
  Used for unit/integration testing.
- `MW_LE_TEST=true` — Let's Encrypt staging. Requires real DNS but uses LE test CA (untrusted).
  Use this for manual integration testing against real DNS.
- `MW_LE_TEST=false` (production) — Real Let's Encrypt certificates. Requires all DNS records
  to be pointing at the server before miniwerk starts.

**Kraftwerk manifest pattern:** For each product in `MW_PRODUCTS`, miniwerk writes a JSON file
to `/pvarki/kraftwerk-rasenmaeher-init.json` inside the product's shared volume. The format:
```json
{"dns": "product.yourdomain.fi", "products": {"tak": "tak.yourdomain.fi"}}
```

**Certificate outputs:**
- Let's Encrypt certs → `le_certs:/le_certs` Docker volume
- CA public cert → `ca_public:/ca_public/ca_chain.pem` (read by all services)

**Domains provisioned:** miniwerk handles: `domain`, `kc.domain`, `tak.domain`, `bl.domain`,
`mtx.domain`, `mtls.domain`, and all `mtls.*` variants.

## Common Agent Pitfalls
1. **miniwerk MUST complete before anything else.** If you see other services crashing on
   startup with cert or manifest errors, wait for miniwerk to reach a healthy state first.
   Do not remove or weaken the health-check dependency in the compose file.
2. **`MW_MKCERT=true` is for local dev only.** Never use mkcert-generated certs in a
   production deployment — clients will not trust them.
3. **Changing `MW_PRODUCTS` requires a volume wipe.** If you add or remove a product from
   the list, existing manifests in the old volumes will conflict. Run `down -v` to wipe before
   bringing back up.
4. **Buildkit is required.** The Docker build will silently fail or produce an incorrect image
   without `DOCKER_BUILDKIT=1`. Always set it.
5. **On macOS the SSH agent socket path differs.** Use
   `/run/host-services/ssh-auth.sock` on macOS vs `$SSH_AUTH_SOCK` on Linux.

## Related Repos
- https://github.com/pvarki/docker-rasenmaeher-integration (orchestration root)
- https://github.com/pvarki/python-pvarki-cfssl (consumes the CA certs miniwerk prepares)
- https://github.com/pvarki/python-rasenmaeher-api (reads the kraftwerk manifest)
