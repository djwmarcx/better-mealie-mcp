# syntax=docker/dockerfile:1
# Better Mealie MCP — production image.
# Multi-stage: uv resolves deps, slim Python runs them.

# --- Build stage ---
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Dependencies first (cached independently of source changes)
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Project itself, installed as a real wheel (--no-editable) so the venv is
# self-contained — the runtime stage copies only /app/.venv.
COPY better_mealie_mcp/ ./better_mealie_mcp/
COPY openapi.json MEALIE_VERSION ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

# --- Runtime stage ---
FROM python:3.14-slim

LABEL org.opencontainers.image.title="Better Mealie MCP" \
      org.opencontainers.image.description="MCP server exposing every Mealie API endpoint via FastMCP" \
      org.opencontainers.image.source="https://github.com/djwmarcx/better-mealie-mcp"

RUN groupadd -r mcpuser && useradd -r -g mcpuser -m mcpuser

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    # containers must bind beyond loopback for -p port mapping to work
    MCP_HOST=0.0.0.0

USER mcpuser
EXPOSE 8000

# stdio by default (docker run -i --rm ...); pass `--http 8000` for HTTP.
ENTRYPOINT ["better-mealie-mcp"]
