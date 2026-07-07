"""
Model guides — the native language of each generation model.
Sourced from real practitioner experience, not official docs.
"""

from __future__ import annotations
import json
from pathlib import Path

_DATA_DIR = Path(__file__).parent / "data" / "guides"


def get_guide(model: str) -> dict:
    """Load guide for a model. Returns dict with full native-language guide."""
    path = _DATA_DIR / f"{model}.json"
    if not path.exists():
        raise ValueError(f"No guide found for model '{model}'. Available: {list_guides()}")
    with open(path) as f:
        return json.load(f)


def list_guides() -> list[str]:
    return sorted(p.stem for p in _DATA_DIR.glob("*.json"))


def get_guide_text(model: str) -> str:
    """Return the guide as formatted text for use in MCP resources or Gemini system prompts."""
    guide = get_guide(model)
    lines = [
        f"# {guide['display_name']} Prompt Guide",
        f"*Model: {guide['model']} | Medium: {guide['medium']}*",
        "",
        "## Overview",
        guide.get("overview", ""),
        "",
        "## Scoring dimensions",
    ]
    for dim, info in guide.get("dimensions", {}).items():
        lines.append(f"\n### {dim.replace('_', ' ').title()}")
        lines.append(f"Weight: {info.get('weight', '?')} | Impact: {info.get('impact', '?')}")
        lines.append(info.get("description", ""))
        if info.get("best_terms"):
            lines.append(f"Best terms: {', '.join(info['best_terms'])}")

    lines += ["", "## Power patterns"]
    for pat in guide.get("power_patterns", []):
        lines.append(f"- {pat}")

    lines += ["", "## Anti-patterns (avoid these)"]
    for ap in guide.get("antipatterns", []):
        lines.append(f"- {ap}")

    lines += ["", "## Example prompts", "", "### Strong (generates well)"]
    for ex in guide.get("examples", {}).get("strong", []):
        lines.append(f'"{ex}"')

    lines += ["", "### Weak (common mistakes)"]
    for ex in guide.get("examples", {}).get("weak", []):
        lines.append(f'"{ex}"')

    return "\n".join(lines)
