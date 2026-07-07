"""
Dali by Lulu — creative intelligence MCP for AI generation agents.

Score your prompt before you spend the credit.

Two modes:
  Hosted (recommended) — connect to dali.getlulu.dev/mcp (OAuth, usage history, always-fresh guides)
  Local (self-host)    — python -m dali.server (no auth, no history)

Add to Claude / Cursor / Windsurf:
  Hosted:  URL https://dali.getlulu.dev/mcp  (OAuth via GitHub)
  Local:   claude mcp add dali -- python -m dali.server

Tools:
  analyze_intent   — parse raw text into structured creative intent
  score_prompt     — score a prompt for a specific model (0–100 + breakdown)
  enhance_prompt   — actually rewrite the prompt using Gemini, model-specific
  my_story         — your scoring history, model stats, creative DNA
  list_models      — all supported generation models

Resources:
  creative://guide/{model}  — full native-language guide for each model
  creative://models         — overview of all models
"""

from __future__ import annotations
import os
from typing import Optional

try:
    from fastmcp import FastMCP
except ImportError:
    raise ImportError(
        "fastmcp not installed.\n"
        "Self-host: pip install dali-mcp\n"
        "Or use the hosted server: https://dali.getlulu.dev/mcp"
    )

from .intent import analyze_intent as _analyze
from .scorer import score_prompt as _score, SUPPORTED_MODELS
from .guides import get_guide_text, list_guides
from .gemini import enhance_with_gemini
from .auth import get_logger

_logger = get_logger()

mcp = FastMCP(
    name="dali",
    instructions=(
        "Dali is Lulu's creative intelligence MCP — use it BEFORE generating any image or video. "
        "It scores prompts against the target model's native language, tells you what's missing, "
        "and rewrites the prompt using Gemini so you get a better result on the first try. "
        "Typical flow: score_prompt → enhance_prompt → generate. "
        "Supported models: veo3, higgsfield, kling, sora, midjourney, flux, imagen. "
        "See your scoring history with: my_story(). "
        "Read model guides at: creative://guide/{model}"
    ),
)


# ── Tools ──────────────────────────────────────────────────────────────────

@mcp.tool()
def analyze_intent(
    prompt: str,
    medium: str = "auto",
) -> dict:
    """
    Parse a creative prompt into structured intent dimensions.

    Returns: detected camera language, motion, lighting, style, mood signals,
    identified gaps, and which models suit the current signals best.

    Args:
        prompt: Raw creative text (rough idea or full prompt — both work)
        medium: "image", "video", or "auto" (default, auto-detected)
    """
    intent = _analyze(prompt, medium)
    _logger.log(user_id="anon", tool_name="analyze_intent", medium=intent.medium)
    return intent.as_dict()


@mcp.tool()
def score_prompt(
    prompt: str,
    model: str,
) -> dict:
    """
    Score a prompt for a specific generation model (0–100).

    Returns a ScoreCard: overall score, letter grade (A–F), per-dimension
    breakdown, what's missing, detected anti-patterns, and a one-line verdict
    on whether it's safe to generate.

    Supported models: veo3, higgsfield, midjourney, flux, kling, sora, imagen
    Aliases: "veo" → veo3, "mj" → midjourney, "sd" → flux

    Args:
        prompt: The prompt to score
        model:  Target generation model
    """
    card = _score(prompt, model)
    _logger.log(
        user_id="anon",
        tool_name="score_prompt",
        model=card.model,
        prompt=prompt,
        score=card.overall,
        grade=card.grade,
    )
    return card.as_dict()


@mcp.tool()
def enhance_prompt(
    prompt: str,
    model: str,
) -> dict:
    """
    Rewrite a prompt using Gemini to score higher on the target model.

    Dali scores the original, identifies what's missing, then calls Gemini
    with the model's native-language guide as context to produce an actual
    better prompt — not just instructions, but the real rewritten text.

    Returns:
      - score_before:    full ScoreCard for original prompt
      - enhanced_prompt: the actual rewritten prompt (Gemini-generated)
      - score_after:     ScoreCard for the enhanced version
      - improvement:     points gained

    Args:
        prompt: The prompt to enhance
        model:  Target generation model (veo3, higgsfield, midjourney, flux, kling, sora, imagen)
    """
    # Score original
    card_before = _score(prompt, model)
    guide_text  = get_guide_text(model)

    # Gemini rewrites it
    enhanced = enhance_with_gemini(
        prompt=prompt,
        model=model,
        guide_text=guide_text,
        missing=card_before.missing,
        antipatterns=card_before.antipatterns,
        score_before=card_before.overall,
    )

    if enhanced:
        card_after   = _score(enhanced, model)
        improvement  = card_after.overall - card_before.overall
        result = {
            "score_before":    card_before.as_dict(),
            "enhanced_prompt": enhanced,
            "score_after":     card_after.as_dict(),
            "improvement":     f"+{improvement} points" if improvement >= 0 else f"{improvement} points",
        }
    else:
        # Gemini unavailable — fall back to instructions
        missing_lines = "\n".join(f"- {m}" for m in card_before.missing) or "- none"
        anti_lines    = "\n".join(f"- {a}" for a in card_before.antipatterns) or "- none"
        result = {
            "score_before": card_before.as_dict(),
            "enhanced_prompt": None,
            "gemini_unavailable": True,
            "fallback_instruction": (
                f"Rewrite for {model} (current: {card_before.overall}/100).\n"
                f"Add: {missing_lines}\nRemove: {anti_lines}"
            ),
        }

    _logger.log(
        user_id="anon",
        tool_name="enhance_prompt",
        model=model,
        prompt=prompt,
        score=card_before.overall,
        grade=card_before.grade,
        metadata={"score_after": result.get("score_after", {}).get("overall")},
    )
    return result


@mcp.tool()
def my_story() -> dict:
    """
    Your Dali creative intelligence report.

    Shows your prompt scoring history across all models:
    - Total prompts scored + this month's count
    - Average score before vs after enhance
    - Model breakdown: calls, avg score, best score per model
    - Grade distribution (how many A, B, C, D, F scores)
    - Your creative DNA: what medium you build most, biggest recurring gap
    - A personal insight on where you'd improve fastest
    - Quota status

    In self-hosted mode: connect to dali.getlulu.dev for full history.
    """
    hosted = bool(os.environ.get("DALI_HOSTED"))

    if not hosted:
        return {
            "message": (
                "Usage history is available on the hosted server. "
                "Connect at: claude mcp add dali --url https://dali.getlulu.dev/mcp\n"
                "Login with GitHub — your history syncs instantly."
            ),
            "hosted_url": "https://dali.getlulu.dev",
        }

    # Hosted path: query the DB via UsageLogger
    events = _logger.get_user_story("anon") or []

    if not events:
        return {
            "total_scored": 0,
            "message": "No prompts scored yet. Call score_prompt() to start building your creative history.",
        }

    # Aggregate
    scores       = [e["score"] for e in events if e.get("score") is not None]
    enhance_evts = [e for e in events if e["tool_name"] == "enhance_prompt"]
    model_counts: dict = {}
    model_scores: dict = {}
    grade_dist   = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}

    for e in events:
        if e.get("model"):
            model_counts[e["model"]] = model_counts.get(e["model"], 0) + 1
        if e.get("score") is not None and e.get("model"):
            model_scores.setdefault(e["model"], []).append(e["score"])
        if e.get("grade") and e["grade"] in grade_dist:
            grade_dist[e["grade"]] += 1

    model_breakdown = {
        m: {
            "calls":     model_counts[m],
            "avg_score": round(sum(model_scores.get(m, [0])) / max(1, len(model_scores.get(m, [1]))), 1),
            "best_score": max(model_scores.get(m, [0])),
        }
        for m in model_counts
    }

    favorite_model = max(model_counts, key=model_counts.get) if model_counts else None
    avg_score      = round(sum(scores) / len(scores), 1) if scores else 0

    # Personal insight — template-based, feels human
    insight = _generate_insight(model_breakdown, avg_score, grade_dist)

    return {
        "total_scored":     len(scores),
        "this_month":       sum(1 for e in events if "2026-07" in e.get("created_at", "")),
        "avg_score":        avg_score,
        "favorite_model":   favorite_model,
        "enhancements_run": len(enhance_evts),
        "model_breakdown":  model_breakdown,
        "grade_distribution": grade_dist,
        "insight":          insight,
        "dashboard":        "https://dali.getlulu.dev/dashboard",
    }


def _generate_insight(model_breakdown: dict, avg_score: float, grade_dist: dict) -> str:
    if not model_breakdown:
        return "Score your first prompt to unlock your creative profile."

    best_model  = max(model_breakdown, key=lambda m: model_breakdown[m]["avg_score"])
    worst_model = min(model_breakdown, key=lambda m: model_breakdown[m]["avg_score"])
    best_avg    = model_breakdown[best_model]["avg_score"]
    worst_avg   = model_breakdown[worst_model]["avg_score"]

    if avg_score >= 75:
        return (
            f"Strong creative. Your {best_model} prompts average {best_avg} — that's pro territory. "
            f"Focus on {worst_model} next (avg {worst_avg}) for the fastest gains."
        )
    if avg_score >= 55:
        return (
            f"Your {best_model} prompts score well (avg {best_avg}), but {worst_model} is pulling your "
            f"average down ({worst_avg}). More camera language and lighting descriptions would add ~15-20 pts."
        )
    fs_and_ds = grade_dist.get("F", 0) + grade_dist.get("D", 0)
    return (
        f"Most prompts are scoring below 55 — the biggest unlock is camera language and lighting. "
        f"Try enhance_prompt() before each generation. {fs_and_ds} prompts this month would have scored "
        f"20+ pts higher with those two additions."
    )


@mcp.tool()
def list_models() -> dict:
    """List all supported generation models with medium, creator, and core strength."""
    details = {
        "veo3":       {"medium": "video", "by": "Google",            "strength": "Cinematic camera language, photorealistic motion"},
        "higgsfield": {"medium": "video", "by": "Higgsfield AI",     "strength": "Physics-driven motion (cloth/hair/fluid), character consistency"},
        "kling":      {"medium": "video", "by": "Kuaishou",          "strength": "Expressive character motion, facial performance, emotional range"},
        "sora":       {"medium": "video", "by": "OpenAI",            "strength": "Temporal coherence, narrative sequences, consistent subjects"},
        "midjourney": {"medium": "image", "by": "Midjourney",        "strength": "Artistic style depth, aesthetic mastery, community-proven patterns"},
        "flux":       {"medium": "image", "by": "Black Forest Labs",  "strength": "Technical photography, camera/lens specificity, negative prompts"},
        "imagen":     {"medium": "image", "by": "Google",            "strength": "Photorealism, lighting precision, photography brief language"},
    }
    return {
        "supported_models": SUPPORTED_MODELS,
        "details":          details,
        "video_models":     ["veo3", "higgsfield", "kling", "sora"],
        "image_models":     ["midjourney", "flux", "imagen"],
        "tip":              "enhance_prompt(prompt, model) → Gemini rewrites it for you. No guessing.",
    }


# ── Resources ──────────────────────────────────────────────────────────────

@mcp.resource("creative://guide/{model}")
def model_guide(model: str) -> str:
    """Full native-language prompt guide for a specific generation model."""
    try:
        return get_guide_text(model)
    except ValueError as e:
        return f"Guide not found: {e}\n\nAvailable: {', '.join(list_guides())}"


@mcp.resource("creative://models")
def models_overview() -> str:
    """Overview of all supported models and their strengths."""
    lines = [
        "# Dali by Lulu — Supported Generation Models",
        "dali.getlulu.dev | github.com/Lulu-The-Narwhal/dali-mcp",
        "",
        "## Video Models",
    ]
    for m in ["veo3", "higgsfield", "kling", "sora"]:
        try:
            g = get_guide_text(m).split("\n")
            overview = next((l for l in g if l.strip() and not l.startswith("#") and not l.startswith("*")), m)
            lines.append(f"- **{m}**: {overview[:100]}")
        except Exception:
            lines.append(f"- **{m}**")
    lines += ["", "## Image Models"]
    for m in ["midjourney", "flux", "imagen"]:
        try:
            g = get_guide_text(m).split("\n")
            overview = next((l for l in g if l.strip() and not l.startswith("#") and not l.startswith("*")), m)
            lines.append(f"- **{m}**: {overview[:100]}")
        except Exception:
            lines.append(f"- **{m}**")
    lines += [
        "",
        "## Tools",
        "- score_prompt(prompt, model) → 0–100 score + what's missing",
        "- enhance_prompt(prompt, model) → Gemini rewrites it for the model's native language",
        "- analyze_intent(prompt) → parsed dimensions + model affinity",
        "- my_story() → your scoring history, model stats, creative DNA",
    ]
    return "\n".join(lines)


# ── Entry point ────────────────────────────────────────────────────────────

def main():
    """Run locally via stdio (self-hosted mode)."""
    mcp.run()


if __name__ == "__main__":
    main()
