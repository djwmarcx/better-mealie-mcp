#!/usr/bin/env bash
# Smoke-test a built Docker image: the server imports, the console script
# speaks MCP over stdio, the ENTRYPOINT serves MCP over HTTP, both report the
# expected version, and the container runs as non-root.
#
# Usage:  scripts/smoke_image.sh <image> [expected-version]
#
# expected-version defaults to the repo's MEALIE_VERSION minus the leading "v"
# (what the server advertises). Offline: a placeholder token means no Mealie
# instance is needed (tools are built from the vendored spec; Mealie is only
# called per tool use). Used by the docker-test and publish workflows.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="${1:?usage: $0 <image> [expected-version]}"
EXPECTED="${2:-$(tr -d 'v[:space:]' < "$ROOT/MEALIE_VERSION")}"
TOKEN="smoke-test-placeholder"
NAME="bmm-smoke-$$"

trap 'docker rm -f "$NAME" >/dev/null 2>&1 || true' EXIT

echo "== 1/3 import + stdio session via the console script"
# Spawns `better-mealie-mcp` (what ENTRYPOINT runs) as a real stdio MCP
# server and lists its tools through a proper client handshake. Bounded so a
# hung server fails the run instead of stalling it.
docker run --rm -e MEALIE_API_TOKEN="$TOKEN" -e PYTHONWARNINGS=ignore \
  -e EXPECTED="$EXPECTED" --entrypoint python "$IMAGE" -c '
import asyncio, os, sys
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

async def main():
    transport = StdioTransport(command="better-mealie-mcp", args=[], env=dict(os.environ))
    async with Client(transport) as client:
        info = client.server_info
        tools = await client.list_tools()
    print(f"python {sys.version.split()[0]}: {info.name} {info.version}, {len(tools)} tools")
    expected = os.environ["EXPECTED"]
    assert info.version == expected, f"version {info.version!r}, expected {expected!r}"
    assert tools, "server exposed no tools"

asyncio.run(asyncio.wait_for(main(), timeout=180))
'

echo "== 2/3 HTTP mode via ENTRYPOINT (--http)"
# Random free host port, so a busy port can't break local runs.
docker run -d --name "$NAME" -p 127.0.0.1::8000 \
  -e MEALIE_API_TOKEN="$TOKEN" -e PYTHONWARNINGS=ignore "$IMAGE" --http 8000 >/dev/null
PORT="$(docker port "$NAME" 8000/tcp | head -n1 | sed 's/.*://')"

INIT='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}'
resp=""
for _ in $(seq 1 90); do
  if resp="$(curl -sf --max-time 5 -X POST "http://127.0.0.1:$PORT/mcp" \
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

info="$(grep -o '"serverInfo":{[^}]*}' <<<"$resp" || true)"
if [ -z "$info" ]; then
  echo "no MCP initialize response over HTTP; container logs:" >&2
  docker logs "$NAME" >&2 || true
  exit 1
fi
echo "$info"
grep -q "\"version\":\"$EXPECTED\"" <<<"$info" \
  || { echo "HTTP server version mismatch, expected $EXPECTED" >&2; exit 1; }

echo "== 3/3 runs as non-root"
user="$(docker run --rm --entrypoint id "$IMAGE" -un)"
echo "user: $user"
[ "$user" != "root" ] || { echo "image runs as root" >&2; exit 1; }

echo "smoke test passed: $IMAGE (version $EXPECTED)"
