"""
Auth + usage middleware for the hosted Dali MCP server.
Validates bearer tokens against the Lulu API, logs every tool call.
"""

from __future__ import annotations
import os
import hashlib
import httpx
from typing import Optional

LULU_API_URL  = os.environ.get("LULU_API_URL",  "https://api.getlulu.dev")
SUPABASE_URL  = os.environ.get("DALI_SUPABASE_URL",  "")
SUPABASE_KEY  = os.environ.get("DALI_SUPABASE_SERVICE_KEY", "")


def _hash_prompt(prompt: str) -> str:
    """Store only a hash of the prompt — never raw text (privacy)."""
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]


class DaliAuth:
    """Validates OAuth tokens issued at dali.getlulu.dev after GitHub login."""

    def __init__(self):
        self._cache: dict[str, dict] = {}

    def validate(self, token: str) -> Optional[dict]:
        if token in self._cache:
            return self._cache[token]
        try:
            resp = httpx.get(
                f"{LULU_API_URL}/dali/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5,
            )
            if resp.status_code == 200:
                user = resp.json()
                self._cache[token] = user
                return user
        except Exception:
            pass
        return None

    def check_quota(self, user_id: str) -> tuple[bool, int, int]:
        """Returns (allowed, used, limit)."""
        try:
            resp = httpx.get(
                f"{LULU_API_URL}/dali/quota/{user_id}",
                timeout=5,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["allowed"], data["used"], data["limit"]
        except Exception:
            pass
        return True, 0, 100  # fail open during auth service outages


class UsageLogger:
    """Logs every Dali tool call to Supabase for analytics + billing."""

    def __init__(self):
        self._enabled = bool(SUPABASE_URL and SUPABASE_KEY)

    def log(
        self,
        user_id: str,
        tool_name: str,
        model: Optional[str] = None,
        prompt: Optional[str] = None,
        score: Optional[int] = None,
        grade: Optional[str] = None,
        medium: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        if not self._enabled:
            return
        try:
            row = {
                "user_id":     user_id,
                "tool_name":   tool_name,
                "model":       model,
                "prompt_hash": _hash_prompt(prompt) if prompt else None,
                "score":       score,
                "grade":       grade,
                "medium":      medium,
                "metadata":    metadata or {},
            }
            httpx.post(
                f"{SUPABASE_URL}/rest/v1/dali_events",
                headers={
                    "apikey":        SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type":  "application/json",
                    "Prefer":        "return=minimal",
                },
                json=row,
                timeout=3,
            )
        except Exception:
            pass  # never block tool calls on logging failures

    def get_user_story(self, user_id: str) -> Optional[dict]:
        """Fetch usage history for my_story tool."""
        if not self._enabled:
            return None
        try:
            resp = httpx.get(
                f"{SUPABASE_URL}/rest/v1/dali_events"
                f"?user_id=eq.{user_id}&order=created_at.desc&limit=200",
                headers={
                    "apikey":        SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                },
                timeout=5,
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None


_auth   = DaliAuth()
_logger = UsageLogger()


def get_auth() -> DaliAuth:
    return _auth


def get_logger() -> UsageLogger:
    return _logger
