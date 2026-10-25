#!/usr/bin/env bash
# Smoke-test a built Docker image: the server imports, the console script
# speaks MCP over stdio, and the ENTRYPOINT serves MCP over HTTP.
#
# Usage:  scripts/smoke_image.sh <image>
#
# Offline: a placeholder token means no Mealie instance is needed (the server
# builds its tools from the vendored spec and only calls Mealie per tool use).
# Used by the docker-test and publish workflows; runnable locally too.
set -euo pipefail

IMAGE="${1:?usage: $0 <image>}"
TOKEN="smoke-test-placeholder"
NAME="bmm-smoke-$$"
PORT="${SMOKE_PORT:-18000}"

trap 'docker rm -f "$NAME" >/dev/null 2>&1 || true' EXIT

echo "== 1/3 import + stdio session via the console script"
# Spawns `better-mealie-mcp` (what ENTRYPOINT runs) as a real stdio MCP
# server and lists its tools through a proper client handshake.
docker run --rm -e MEALIE_API_TOKEN="$TOKEN" -e PYTHONWARNINGS=ignore \
  --entrypoint python "$IMAGE" -c '
import asyncio, os, sys
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

async def main():
    transport = StdioTransport(command="better-mealie-mcp", args=[], env=dict(os.environ))
    async with Client(transport) as client:
        info = client.server_info
        tools = await client.list_tools()
    assert info and info.name, "no server identity from the handshake"
    print(f"python {sys.version.split()[0]}: {info.name} {info.version}, {len(tools)} tools")
    assert tools, "server exposed no tools"

asyncio.run(main())
'

echo "== 2/3 HTTP mode via ENTRYPOINT (--http)"
docker run -d --name "$NAME" -p "127.0.0.1:$PORT:8000" \
  -e MEALIE_API_TOKEN="$TOKEN" -e PYTHONWARNINGS=ignore "$IMAGE" --http 8000 >/dev/null

INIT='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}'
resp=""
for _ in $(seq 1 60); do
  if resp="$(curl -sf -X POST "http://127.0.0.1:$PORT/mcp" \
      -H 'Content-Type: application/json' \
      -H 'Accept: application/json, text/event-stream' \
      -d "$INIT")"; then
    break
  fi
  if [ "$(docker inspect -f '{{.State.Running}}' "$NAME" 2>/dev/null)" != "true" ]; then
    echo "container exited early:" >&2
    docker logs "$NAME" >&2 || true
    exit 1
  fi
  sleep 1
done

if ! grep -q '"serverInfo"' <<<"$resp"; then
  echo "no MCP initialize response over HTTP; container logs:" >&2
  docker logs "$NAME" >&2 || true
  exit 1
fi
grep -o '"serverInfo":{[^}]*}' <<<"$resp"

echo "== 3/3 runs as non-root"
user="$(docker run --rm --entrypoint id "$IMAGE" -un)"
echo "user: $user"
[ "$user" != "root" ] || { echo "image runs as root" >&2; exit 1; }

echo "smoke test passed: $IMAGE"
