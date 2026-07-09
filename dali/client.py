"""
HTTP client for the Dali hosted API at dali.getlulu.dev.

All intelligence (scoring, enhancement, Memgraph graph) runs server-side.
This module handles auth token injection and request formatting.

Tokens: get yours at dali.getlulu.dev (GitHub OAuth login, free tier).
"""

from __future__ import annotations
import os
import httpx
from typing import Optional

DALI_API_BASE = os.environ.get("DALI_API_URL", "https://dali.getlulu.dev")
_DEFAULT_TIMEOUT = 30.0


def _headers(token: Optional[str] = None) -> dict:
    h = {"Content-Type": "application/json", "User-Agent": "dali-mcp/0.5.4"}
    tok = token or os.environ.get("DALI_TOKEN")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def call(endpoint: str, payload: dict, token: Optional[str] = None) -> dict:
    """POST to the Dali API. Returns the parsed JSON response."""
    url = f"{DALI_API_BASE.rstrip('/')}/{endpoint.lstrip('/')}"
    try:
        with httpx.Client(timeout=_DEFAULT_TIMEOUT) as http:
            resp = http.post(url, json=payload, headers=_headers(token))
            resp.raise_for_status()
            return resp.json()
    except httpx.TimeoutException:
        return {"error": "Request timed out. Dali API may be under load — retry in a moment."}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return {
                "error": "Unauthorized. Set DALI_TOKEN or run: dali auth login",
                "auth_url": f"{DALI_API_BASE}/auth/github",
            }
        if e.response.status_code == 429:
            return {
                "error": "Rate limit reached. Free tier: 100 calls/month.",
                "upgrade_url": f"{DALI_API_BASE}/pricing",
            }
        return {"error": f"API error {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"error": f"Could not reach Dali API: {e}"}


def get_call(endpoint: str, token: Optional[str] = None) -> dict:
    """GET from the Dali API. Returns the parsed JSON response."""
    url = f"{DALI_API_BASE.rstrip('/')}/{endpoint.lstrip('/')}"
    try:
        with httpx.Client(timeout=_DEFAULT_TIMEOUT) as http:
            resp = http.get(url, headers=_headers(token))
            resp.raise_for_status()
            return resp.json()
    except httpx.TimeoutException:
        return {"error": "Request timed out. Dali API may be under load — retry in a moment."}
    except httpx.HTTPStatusError as e:
        return {"error": f"API error {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"error": f"Could not reach Dali API: {e}"}

