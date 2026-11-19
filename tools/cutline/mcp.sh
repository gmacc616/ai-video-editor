#!/usr/bin/env bash
# Call one Cutline MCP tool over HTTP (works without registering the MCP server in Claude Code).
#   bash tools/cutline/mcp.sh <tool> '<json args>'     tools: vendor/cutline/docs/mcp-tools.md
U=http://localhost:${CUTLINE_PORT:-4100}/mcp; H=(-H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream')
SID=$(curl -s -D - -o /dev/null "${H[@]}" $U -d '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}' | grep -i mcp-session-id | cut -d' ' -f2 | tr -d '\r')
S=(); [ -n "$SID" ] && S=(-H "mcp-session-id: $SID")
curl -s "${H[@]}" "${S[@]}" $U -d '{"jsonrpc":"2.0","method":"notifications/initialized"}' >/dev/null
curl -s "${H[@]}" "${S[@]}" $U -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"$1\",\"arguments\":$2}}" | sed 's/^data: //' | grep '^{' | jq -c '.result.structuredContent // .result.content[0].text // .error' | head -c 1200; echo
