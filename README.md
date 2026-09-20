<div align="center">

# 🍲 Better Mealie MCP

<p>
  <img src="https://img.shields.io/badge/tools-264-blue" alt="264 tools">
  <a href="https://github.com/jlowin/fastmcp"><img src="https://img.shields.io/badge/Built%20with-FastMCP-purple" alt="Built with FastMCP"></a>
  <img src="https://img.shields.io/badge/python-3.14%2B-blue" alt="Python 3.14+">
  <img src="https://img.shields.io/badge/Mealie-v3.26.0-brightgreen" alt="Mealie v3.26.0">
</p>
<p>
  <a href="https://github.com/djwmarcx/better-mealie-mcp/actions/workflows/pages.yml"><img src="https://img.shields.io/github/actions/workflow/status/djwmarcx/better-mealie-mcp/pages.yml?branch=main&label=setup%20wizard" alt="Setup wizard deploy"></a>
  <a href="https://github.com/djwmarcx/better-mealie-mcp/actions/workflows/update-spec.yml"><img src="https://img.shields.io/github/actions/workflow/status/djwmarcx/better-mealie-mcp/update-spec.yml?label=spec%20sync" alt="Spec sync"></a>
  <a href="https://github.com/djwmarcx/better-mealie-mcp/releases"><img src="https://img.shields.io/github/v/release/djwmarcx/better-mealie-mcp?sort=semver&label=release" alt="Latest release"></a>
  <a href="https://github.com/djwmarcx/better-mealie-mcp/blob/main/.github/renovate.json5"><img src="https://img.shields.io/badge/Renovate-enabled-brightgreen?logo=renovatebot&logoColor=white" alt="Renovate enabled"></a>
</p>

<em>An MCP server exposing <strong>every</strong> <a href="https://mealie.io">Mealie</a> API endpoint —<br>
all 250+ operations, none excluded. Manage recipes, meal plans, shopping lists,<br>
households and more from any AI assistant, in natural language.</em>

</div>

---

Built with [FastMCP](https://github.com/jlowin/fastmcp) `from_openapi`: tools are
generated straight from Mealie's OpenAPI spec, so the server stays in sync with
Mealie and nothing is hand-maintained. See [TOOLS.md](./TOOLS.md) for the full
tool list.

## 💬 What can you do with it?

| You say | What happens |
|---------|--------------|
| *"Add a chicken tikka masala recipe from this URL"* | Scrapes and imports the recipe |
| *"What can I cook with what's in my pantry?"* | Searches recipes by your ingredients |
| *"Plan my dinners for next week"* | Creates meal-plan entries |
| *"Build a shopping list for those meals"* | Generates a consolidated shopping list |
| *"Tag all my soups as 'winter'"* | Bulk-updates recipe tags |

## 🧙 Setup Wizard

<h3 align="center">

[**→ Open the Setup Wizard**](https://djwmarcx.github.io/better-mealie-mcp/)

</h3>

<p align="center">
  <a href="https://djwmarcx.github.io/better-mealie-mcp/">
    <img src="public/options-tree.png" alt="Setup options — Install, Client, Transport, Auth" width="900">
  </a>
</p>

Don't hand-write JSON. The wizard walks you through every choice and emits a
ready-to-paste config for **your** combination:

- **Install** — Docker image or from source.
- **Client** — Claude Code, Claude Desktop, Cursor, VS Code, Gemini CLI, or
  ChatGPT (it knows each one's config shape).
- **Connection** — stdio or HTTP, API token or username/password.
- **Limit tools** *(optional)* — trim the 259 tools to just the groups you need,
  for leaner context or clients that cap tool counts. Start from a **pack**
  (*Cooking*, *Meal planning*, *Sharing & browse*, *Admin & users*) or pick
  groups individually; tap a group's ⓘ to see every tool inside it. Your choice
  is baked into the generated config as `MEALIE_INCLUDE_TAGS`.

## 🚀 Setup

**Docker (GHCR image):**

```bash
docker pull ghcr.io/djwmarcx/better-mealie-mcp
docker run -i --rm \
  -e MEALIE_BASE_URL=http://host.docker.internal:9925 \
  -e MEALIE_API_TOKEN=... \
  ghcr.io/djwmarcx/better-mealie-mcp            # stdio; add `--http 8000` for HTTP
```

Images are published on each release, tagged `<mealie-version>` and `latest`.
Inside a container, `localhost` is the container — point `MEALIE_BASE_URL` at
`host.docker.internal` (macOS/Windows) or your host's LAN IP (Linux).

**From source:**

```bash
git clone https://github.com/djwmarcx/better-mealie-mcp
cd better-mealie-mcp
uv sync                     # install deps
cp .env.example .env        # then edit .env with your Mealie URL + token
```

Auth (set in `.env` or the environment):

| Var | Meaning |
|-----|---------|
| `MEALIE_BASE_URL` | Mealie base URL (default `http://localhost:9925`) |
| `MEALIE_API_TOKEN` | Long-lived API token (**preferred**) — Mealie → Profile → Manage API Tokens |
| `MEALIE_USERNAME` / `MEALIE_PASSWORD` | Alternative: logs in at startup to fetch a token |
| `MEALIE_TIMEOUT` | Per-request timeout, seconds (default 60) |
| `MEALIE_VERIFY_SSL` | Verify TLS cert; `false` to accept self-signed (default true) |
| `MCP_SERVER_NAME` | MCP name advertised to clients (default `Mealie`) |
| `MCP_AUTH_MODE` | HTTP endpoint auth: `none` *(default)* \| `key` \| `oauth` \| `authentik` \| `both` (= Authentik token or API key). No effect in stdio mode |
| `MCP_AUTH_TOKEN` | API key for `key`/`both`: reject every request to `/mcp` without `Authorization: Bearer <token>` |
| `MCP_PUBLIC_BASE_URL` | Public HTTPS URL (clients' view) needed by `oauth`/`both`/`authentik` for discovery metadata |
| `MCP_AUTH_ISSUER` | Authentik OIDC issuer URL (required for `authentik`/`both`), e.g. `https://auth.example/application/o/mealie/` |
| `MCP_AUTH_AUDIENCE` | Authentik token `aud` to require (optional, typically the provider's client id) |
| `MCP_AUTH_SCOPES` | Authentik scopes a token must carry (optional, comma-separated) |
| `MCP_AUTH_DISCOVERY_URL` | Override Authentik's OIDC discovery document URL (optional) |
| `MEALIE_INCLUDE_TAGS` | Expose **only** these API groups, comma-separated (e.g. `recipes,organizers,foods`). Fewer tools = leaner context / fits clients that cap tool counts |
| `MEALIE_EXCLUDE_TAGS` | Expose everything **except** these groups (e.g. `admin,households`) |
| `MEALIE_SLIM_SCHEMAS` | Trim redundant schema noise — default `true` (see modes below) |
| `MEALIE_SLIM_AGGRESSIVE` | Also collapse nullable `anyOf` unions — default `false` |
| `MEALIE_VALIDATE_OUTPUT` | Emit per-tool output schemas + validate results — default `false` |

Groups are the first path segment of the API (`recipes`, `households`, `admin`,
`organizers`, `users`, `explore`, `foods`, `units`, …). Unset = every tool.
`INCLUDE` wins if both are set. See [TOOLS.md](./TOOLS.md) for the current
groups and what's in each, or let the
[Setup Wizard](https://djwmarcx.github.io/better-mealie-mcp/) pick them — its
group picker (with one-click **packs** like *Cooking* or *Meal planning*) fills
`MEALIE_INCLUDE_TAGS` for you.

### Context size (schema detail)

Every tool this server exposes ships its JSON schema to the model on **every**
request — that "idle context" is pure overhead until a tool is actually called.
With all 259 tools the full schemas are ~240k tokens, so the server trims them.
Three preset modes (all endpoints stay callable — only the *schema detail* the
model sees changes):

| Mode | Env | Idle context | What it does |
|------|-----|-------------:|--------------|
| **Lean** *(default)* | *(none — the default)* | **~61k tok** | Drops redundant `title`s (FastAPI auto-generates them from field names) and echoed `default`s, and omits output/response schemas. No loss of callable capability. |
| **Leanest** | `MEALIE_SLIM_AGGRESSIVE=true` | **~51k tok** | Everything Lean does, **plus** collapses nullable `anyOf:[{X},{null}]` unions to `X` (drops the explicit "null allowed" hint). |
| **Full** | `MEALIE_SLIM_SCHEMAS=false`<br>`MEALIE_VALIDATE_OUTPUT=true` | **~240k tok** | Complete, untrimmed input **and** output schemas, with client-side result validation. Use only if your client relies on structured-output schemas. |

Everything the model needs to make a **correct** call (`format`, real
`description`s, required fields) is kept in every mode. Combine with tag
filtering above to shrink further — the
[Setup Wizard](https://djwmarcx.github.io/better-mealie-mcp/) shows a live token
estimate for your exact combination.

## ▶️ Run

```bash
uv run better-mealie-mcp             # stdio transport (for MCP clients)
uv run better-mealie-mcp --http 8000 # streamable-http on 127.0.0.1:8000
uv run server.py                     # same server, back-compat entry
fastmcp run fastmcp.json             # via FastMCP project config (stdio)
fastmcp run fastmcp-http.json        # via FastMCP project config (http)
```

In `--http` mode the bind address comes from `MCP_HOST` (default `127.0.0.1`;
the Docker image sets `0.0.0.0` so `-p` port mapping works).

**HTTP auth:** `MCP_AUTH_MODE` picks the mechanism (default `none`, no effect on
stdio):

- `none` — open endpoint (trusted/local setups only; this is also the default
  when `MCP_AUTH_MODE` is unset — auth is opt-in)
- `key` — require `Authorization: Bearer <MCP_AUTH_TOKEN>` on every request to
  `/mcp` (401 without it). Clients send the token in headers config — e.g.
  Claude/Cursor `"headers": {"Authorization": "Bearer <token>"}` — or, in the
  FastMCP Python client, `Client("http://host:8000/mcp", auth="<token>")`.
- `oauth` — run a built-in OAuth 2.1 authorization server (dynamic client
  registration + PKCE) so ChatGPT/Claude/etc. can use their standard "sign in"
  connector flow against `/mcp`. No external identity provider needed. **Open**
  (auto-approves) — see the warning below.
- `authentik` — validate access tokens issued by **your** Authentik server
  (OIDC + JWKS), so only your Authentik users can call `/mcp`. Usually the best
  fit when an Authentik instance is already in front of Mealie.
- `both` — accept an Authentik token **or** the pre-shared API key: Authentik
  for interactive clients, the key for scripts/services.

`oauth` / `authentik` / `both` require `MCP_PUBLIC_BASE_URL` (public HTTPS URL
the client reaches you on) so discovery metadata and redirect URIs resolve;
`authentik` / `both` require `MCP_AUTH_ISSUER`; `key` / `both` require
`MCP_AUTH_TOKEN` — setting just the token does nothing unless the mode asks for
it. All modes work behind a reverse proxy (set `MCP_HOST=0.0.0.0`, proxy
terminates TLS).

### Authentik mode (`authentik`)

Replace the built-in auto-approving OAuth server with a real identity provider.
Set `MCP_AUTH_MODE=authentik`, `MCP_PUBLIC_BASE_URL`, and
`MCP_AUTH_ISSUER` (the OIDC issuer of the Authentik OAuth2/OIDC provider for
your app, e.g. `https://auth.example/application/o/mealie/`). Optionally pin the
expected token `MCP_AUTH_AUDIENCE` (usually the provider's client id) and
required `MCP_AUTH_SCOPES`.

The server then validates the RS256 signature, expiry, issuer, audience and
scopes of every bearer token against Authentik's JWKS (fetched from
`MCP_AUTH_ISSUER/.well-known/openid-configuration`; override with
`MCP_AUTH_DISCOVERY_URL`), and advertises RFC 9728 protected-resource metadata
at `/.well-known/oauth-protected-resource` so spec-aware clients discover
Authentik automatically. Sign up a new OAuth2/OIDC provider:
Authentik → Applications → you app → Provide → OIDC, note its client id/secret,
and configure that application in your AI tool's connector settings instead of
this server.

> **Tip:** if the access token your AI tool receives does not include the
> client id in `aud`, omit `MCP_AUTH_AUDIENCE` (issuer + signature are usually
> enough).

`both` reuses this exact setup — set `MCP_AUTH_MODE=both` and additionally
provide `MCP_AUTH_TOKEN` to also accept the pre-shared key (e.g. for
scripts/tools that can't run the connector flow).

> **Warning:** the built-in OAuth server auto-approves every authorization
> request, so anyone who can reach `/authorize` gets a token. Only expose the
> `oauth` mode on a URL that is not publicly reachable — put it behind VPN/auth
> gateways — or use `key`/`both` for public deployments.

## 🧪 Test against a local Mealie (Docker)

```bash
docker run -d --name mealie -p 9925:9000 \
  -e ALLOW_SIGNUP=true -e BASE_URL=http://localhost:9925 -e TZ=UTC \
  ghcr.io/mealie-recipes/mealie:latest
```

Default admin login: `changeme@example.com` / `MyPassword`.

## 📝 Notes

- **Exposing every endpoint is a lot of tools — a lot of idle context.** Most
  clients handle it fine. If yours caps tool counts or you want a leaner
  context, trim the toolset with `MEALIE_INCLUDE_TAGS` / `MEALIE_EXCLUDE_TAGS`
  (see [Setup](#-setup)) or the wizard's group picker.

### Versioning

**This MCP's version mirrors the Mealie version its spec targets** — MCP
`3.20.1` ⇒ Mealie `v3.20.1`. The server advertises it to clients, and
[VERSIONS.md](./VERSIONS.md) maps every release to its Mealie version and date.

MCP-only changes (features/fixes with no Mealie version change) ship as a
**revision** of the same Mealie version: the [`REVISION`](./REVISION) counter
bumps and the release/image tag gains a `-r<n>` suffix — e.g. `v3.20.1-r2`
(`-r1` is the base and carries no suffix). A new Mealie version resets the
counter. `:latest` always points at the newest build.

`openapi.json` is a vendored copy of Mealie's spec. The
[`update-spec`](.github/workflows/update-spec.yml) workflow runs daily and
**auto-tracks the latest stable Mealie release** (`mealie:latest`): it boots that
image, reads its real version from `/api/app/about`
([`MEALIE_VERSION`](./MEALIE_VERSION)), pulls `/openapi.json`, regenerates
[TOOLS.md](./TOOLS.md) + counts, and — **only when the spec actually changed** —
bumps the version and **opens a pull request** (main is protected, so every
change lands via PR). When that PR merges,
[`release-on-spec`](.github/workflows/release-on-spec.yml) cuts a
[release](https://github.com/djwmarcx/better-mealie-mcp/releases) (spec attached,
notes listing added/removed tools). Volatile server-clock defaults are stripped
so an unchanged run is a true no-op.

To freeze on one release instead of tracking latest, set `MEALIE_TAG_DEFAULT` in
the workflow to a specific tag (e.g. `v3.20.1`), or run it manually with a
`mealie_tag` input (`latest`, `nightly`, or any tag).
- A few endpoints (`list_auth_oauth*`) return 500 unless OIDC is configured on
  the Mealie side — that's Mealie behavior, not the server.

## 📄 License

[MIT License](./LICENSE)
