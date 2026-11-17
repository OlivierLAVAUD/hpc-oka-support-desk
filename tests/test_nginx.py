# Nginx configuration tests
# Copyright 2026 UCit
# Licensed under the Apache License, Version 2.0

import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NGINX = ROOT / "nginx"


# --- SSL for OKA ---

@pytest.mark.parametrize("config", ["oka.nginx.conf"])
def test_nginx_oka_ssl_directive_present(config: str):
    """Verify SSL directives are present in OKA config."""
    config_path = NGINX / config
    config_text = config_path.read_text()
    assert "ssl_certificate" in config_text, "Missing ssl_certificate directive"
    assert "ssl_protocols" in config_text, "Missing ssl_protocols directive"
    assert "443 ssl" in config_text, "Missing 443 ssl directive"


# --- proxy_timeout for stream ---

@pytest.mark.parametrize("config", ["viz.stream.conf"])
def test_nginx_viz_proxy_timeout(config: str):
    """Verify proxy_timeout is present in visualization stream config."""
    config_path = NGINX / config
    config_text = config_path.read_text()
    assert "proxy_timeout" in config_text, "Missing proxy_timeout directive"
    # Should have 1h for stream connections
    assert "1h" in config_text, "Missing 1h proxy_timeout for stream"


# --- proxy_buffering off for preparatory MCP ---

@pytest.mark.parametrize("config", ["mcp.sse.conf"])
def test_nginx_mcp_proxy_buffering_off(config: str):
    """Verify proxy_buffering off is present in preparatory MCP config."""
    config_path = NGINX / config
    config_text = config_path.read_text()
    assert "proxy_buffering off" in config_text, (
        "Missing proxy_buffering off directive for preparatory MCP"
    )
    assert "proxy_read_timeout" in config_text, (
        "Missing proxy_read_timeout directive for preparatory MCP"
    )


# --- Critical directives presence tests ---

@pytest.mark.parametrize(
    "config, directive",
    [
        ("oka.nginx.conf", "ssl_certificate"),
        ("oka.nginx.conf", "ssl_protocols"),
        ("viz.stream.conf", "proxy_timeout"),
        ("mcp.sse.conf", "proxy_buffering off"),
        ("mcp.sse.conf", "proxy_read_timeout"),
    ],
)
def test_nginx_critical_directives_present(config: str, directive: str):
    """Verify critical nginx directives are present in each config."""
    config_path = NGINX / config
    config_text = config_path.read_text()
    assert directive in config_text, f"Missing {directive} in {config}"
