<div align="center">

# 🍲 Better Mealie MCP

<p>
  <img src="https://img.shields.io/badge/tools-259-blue" alt="259 tools">
  <a href="https://github.com/jlowin/fastmcp"><img src="https://img.shields.io/badge/Built%20with-FastMCP-purple" alt="Built with FastMCP"></a>
  <img src="https://img.shields.io/badge/python-3.13%2B-blue" alt="Python 3.13+">
  <img src="https://img.shields.io/badge/Mealie-v3.20.1-brightgreen" alt="Mealie v3.20.1">
</p>
<p>
  <a href="https://github.com/djwmarcx/better-mealie-mcp/actions/workflows/pages.yml"><img src="https://img.shields.io/github/actions/workflow/status/djwmarcx/better-mealie-mcp/pages.yml?branch=main&label=setup%20wizard" alt="Setup wizard deploy"></a>
  <a href="https://github.com/djwmarcx/better-mealie-mcp/actions/workflows/update-spec.yml"><img src="https://img.shields.io/github/actions/workflow/status/djwmarcx/better-mealie-mcp/update-spec.yml?label=spec%20sync" alt="Spec sync"></a>
  <a href="https://github.com/djwmarcx/better-mealie-mcp/releases"><img src="https://img.shields.io/github/v/release/djwmarcx/better-mealie-mcp?sort=semver&label=release" alt="Latest release"></a>
  <a href="https://github.com/djwmarcx/better-mealie-mcp/blob/main/.github/renovate.json5"><img src="https://img.shields.io/badge/Renovate-enabled-brightgreen?logo=renovatebot&logoColor=white" alt="Renovate enabled"></a>
</p>

<em>An MCP server exposing <strong>every</strong> <a href="https://mealie.io">Mealie</a> API endpoint —<br>
all 259 operations, none excluded. Manage recipes, meal plans, shopping lists,<br>
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

Generate the exact config for your AI client (Claude Code, Claude Desktop,
Cursor, VS Code, ChatGPT, Gemini CLI, …) with the interactive wizard:

> **→ [Open the Setup Wizard](https://djwmarcx.github.io/better-mealie-mcp/)**
> (source: [`setup-wizard.html`](./setup-wizard.html), deployed to GitHub Pages)

Or set it up manually below.

## 🚀 Setup

```bash
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

## ▶️ Run

```bash
uv run server.py                 # stdio transport (for MCP clients)
uv run server.py --http 8000     # streamable-http on 127.0.0.1:8000
fastmcp run fastmcp.json         # via FastMCP project config (stdio)
fastmcp run fastmcp-http.json    # via FastMCP project config (http)
```

## 🔌 Use with Claude

Claude Code CLI:

```bash
claude mcp add better-mealie-mcp -s user \
  -e MEALIE_BASE_URL=http://localhost:9925 -e MEALIE_API_TOKEN=... \
  -- uv run --directory /path/to/better-mealie-mcp server.py
```

Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "better-mealie-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/better-mealie-mcp", "server.py"],
      "env": {
        "MEALIE_BASE_URL": "http://localhost:9925",
        "MEALIE_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

## 🧪 Test against a local Mealie (Docker)

```bash
docker run -d --name mealie -p 9925:9000 \
  -e ALLOW_SIGNUP=true -e BASE_URL=http://localhost:9925 -e TZ=UTC \
  ghcr.io/mealie-recipes/mealie:latest
```

Default admin login: `changeme@example.com` / `MyPassword`.

## 🏷️ Tool naming

Mealie's `operationId`s bury the semantics in a path echo
(`create_one_api_recipes_post`), so names are derived from **HTTP method + path**
instead — descriptive and collision-free:

| Endpoint | Tool |
|----------|------|
| `GET /api/recipes` | `list_recipes` |
| `POST /api/recipes` | `create_recipes` |
| `GET /api/recipes/{slug}` | `get_recipes_by_slug` |
| `PUT /api/recipes/{slug}` | `update_recipes_by_slug` |
| `DELETE /api/recipes/{slug}` | `delete_recipes_by_slug` |

When a path parameter name also appears in the request body (e.g. `slug`),
FastMCP disambiguates the path parameter with a `__path` suffix (`slug__path`).

## 📝 Notes

- **259 tools is a lot of idle context.** Most clients handle it, but if yours
  caps tool counts or you want a leaner context, use FastMCP's tool-search or
  filter by tag — ask and it can be wired in.
### Versioning

**This MCP's version mirrors the Mealie version its spec targets** — MCP
`3.20.1` ⇒ Mealie `v3.20.1`. The server advertises it to clients, and
[VERSIONS.md](./VERSIONS.md) maps every release to its Mealie version and date.

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
