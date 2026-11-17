# Nginx — Reverse Proxy & Stream Interfaces

This directory contains Nginx configurations illustrating the interfaces
a Support Engineer UCit encounters on the OKA platform.

## Interfaces

### 1. OKA HTTPS Reverse Proxy (`oka.nginx.conf`)
- **Role**: Secure reverse proxy for OKA platform access via HTTPS
- **Status**: Active
- **Mission**: Support UCit - OKA platform access
- **Test**: Verify SSL directives present (`ssl_certificate`, `ssl_protocols`)
- **Link**: Enables `https://oka.support.universite-cite.fr` access to OKA platform

### 2. Visualization Stream (`viz.stream.conf`)
- **Role**: TCP/UDP proxy for remote 2D/3D visualization (VNC, DCV)
- **Status**: Active
- **Module**: `stream` - Nginx module for non-HTTP protocols
- **Mission**: TICKET-008 - Remote visualization portal (TurboVNC/noVNC)
- **Test**: Verify `proxy_timeout` and `proxy_buffering off` for stream connections
- **Link**: Enables access to remote visualization portals (TurboVNC, Windows)

### 3. MCP SSE (préparatoire) (`mcp.sse.conf`)
- **Role**: Preparatory configuration for future SSE server
- **Status**: Préparatoire - ne prétend pas que le serveur MCP existe
- **Critical directive**: `proxy_buffering off`, `proxy_read_timeout`
- **Mission**: Future LLM-based support automation
- **Test**: Verify `proxy_buffering off` and `proxy_read_timeout` present
- **Link**: Documents what will be needed when MCP exists (SSE events, real-time updates)
- **Note**: This is preparatory only - no MCP server is deployed

## How to Test

```bash
# Verify OKA SSL configuration
nginx -t -c nginx/oka.nginx.conf

# Verify visualization stream
nginx -t -c nginx/viz.stream.conf

# Verify MCP preparatory config
nginx -t -c nginx/mcp.sse.conf

# Run syntax check
uv run pytest tests/ -k "nginx" --co
```
