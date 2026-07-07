"""
Dali by Lulu — creative intelligence MCP for AI generation agents.

Score your prompt before you spend the credit.

This is the open-source MCP client. Tool definitions live here.
Intelligence (scoring engine, Gemini enhancement, V3 graph brain) runs
on the hosted server at dali.getlulu.dev.

Connect (recommended):
  claude mcp add dali --url https://dali.getlulu.dev/mcp

Self-hosted (calls Dali API, requires a free token):
  pip install dali-mcp
  export DALI_TOKEN=<your token from dali.getlulu.dev>
  claude mcp add dali -- python -m dali.server

Tools:
  analyze_intent       — parse raw text into structured creative intent
  score_prompt         — score a prompt 0–100 for a specific model
  enhance_prompt       — Gemini-powered rewrite in the model's native language
  creative_patterns    — community graph: A-grade patterns for this model (V3)
  community_benchmark  — how your prompt compares to community top scorers (V3)
  my_story             — your scoring history, model stats, creative DNA
  list_models          — all supported generation models

Resources:
  creative://guide/{model}  — full native-language guide for each model
  creative://models         — overview of all models
"""

from __future__ import annotations
import os

try:
    from fastmcp import FastMCP
except ImportError:
    raise ImportError(
        "fastmcp not installed. Run: pip install dali-mcp\n"
        "Or use the hosted server: https://dali.getlulu.dev/mcp"
    )

from .client import call

mcp = FastMCP(
    name="dali",
    instructions=(
        "Dali is creative intelligence for AI generation. Use it BEFORE generating any image or video.\n\n"
        "PROACTIVE WORKFLOW (always follow this):\n"
        "1. User expresses any image/video generation intent → IMMEDIATELY call score_prompt(prompt, model)\n"
        "2. Grade A or B (score ≥ 70) → proceed with the prompt\n"
        "3. Grade C, D, or F (score < 70) → call enhance_prompt(prompt, model) to get a rewrite brief, "
        "then YOU write the enhanced prompt using the brief's native_language_rules + structure_template. "
        "Then call score_prompt on your version to verify.\n"
        "4. NEVER generate without scoring first\n\n"
        "TOOLS:\n"
        "- analyze_intent(prompt) — parse intent signals before scoring\n"
        "- score_prompt(prompt, model) — grade 0–100 with what's missing\n"
        "- enhance_prompt(prompt, model) — AI rewrite in the model's native language\n"
        "- creative_patterns(model) — community A-grade patterns from the graph brain\n"
        "- community_benchmark(prompt, model) — compare vs top scorers\n"
        "- my_story() — personal scoring history and creative DNA\n"
        "- list_models() — all supported models\n\n"
        "SUPPORTED MODELS: veo3, seedance, kling, runway, wan, minimax, higgsfield, sora, flux, midjourney, ideogram, firefly, imagen\n"
        "ALIASES: veo→veo3, mj→midjourney, sd→flux, gen4→runway, hailuo→minimax, wan27→wan\n\n"
        "RESOURCES: creative://guide/{model} — full native-language guide\n\n"
        "INSTALL GUIDE: dali.getlulu.dev/install"
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
    return call("/api/intent", {"prompt": prompt, "medium": medium})


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

    Supported models: veo3, seedance, kling, runway, wan, minimax, higgsfield, sora, flux, midjourney, ideogram, firefly, imagen
    Aliases: "veo" → veo3, "mj" → midjourney, "sd" → flux, "gen4" → runway, "hailuo" → minimax

    Args:
        prompt: The prompt to score
        model:  Target generation model
    """
    return call("/api/score", {"prompt": prompt, "model": model})


@mcp.tool()
def enhance_prompt(
    prompt: str,
    model: str,
) -> dict:
    """
    Rewrite a prompt using AI to score higher on the target model.

    Returns a rewrite brief — YOU (the LLM) write the enhanced prompt from it.

    Dali provides creative intelligence: what's missing, the model's native language rules,
    structure template, priority fixes, and length target.
    You provide creative execution: actually writing the better prompt.

    Returns:
      - score_before:    full ScoreCard showing current gaps
      - rewrite_brief:   native_language_rules, structure_template, priority_fixes, length_target
      - llm_instructions: step-by-step instructions for writing the enhanced prompt

    Args:
        prompt: The prompt to enhance
        model:  Target generation model (veo3, seedance, kling, runway, wan, minimax, higgsfield, sora, flux, midjourney, ideogram, firefly, imagen)
    """
    return call("/api/enhance", {"prompt": prompt, "model": model})


@mcp.tool()
def creative_patterns(
    model: str,
    grade: str = "A",
) -> dict:
    """
    Community graph intelligence: which patterns consistently produce high-grade prompts
    for this model?

    Powered by the Dali V3 graph brain — every prompt scored by every
    Dali user contributes to this. The more community usage, the richer the signal.

    Also returns: enhancement unlocks (which patterns added during enhance_prompt
    have produced the highest score gains for this model).

    Args:
        model: Target generation model (veo3, seedance, kling, runway, wan, minimax, higgsfield, flux, midjourney, ideogram, firefly)
        grade: Minimum grade filter — "A" (only A-grade), "B" (A+B), "C" (A+B+C)
    """
    return call("/api/patterns", {"model": model, "grade": grade})


@mcp.tool()
def community_benchmark(
    prompt: str,
    model: str,
) -> dict:
    """
    Compare your prompt against community top scorers for this model.

    Scores your prompt, then queries the Dali graph to find:
    - Which A-grade community patterns are absent from your prompt
    - Which enhancement patterns would give you the biggest score gain
    - Where you sit vs the community average for this model

    Args:
        prompt: Your prompt to benchmark
        model:  Target generation model
    """
    return call("/api/benchmark", {"prompt": prompt, "model": model})


@mcp.tool()
def my_story() -> dict:
    """
    Your Dali creative intelligence report.

    Shows your prompt scoring history across all models:
    - Total prompts scored + this month's count
    - Average score and model breakdown
    - Grade distribution (how many A, B, C, D, F scores)
    - Your creative DNA: patterns that define your highest-scoring work (V3 graph)
    - A personal insight on where you'd improve fastest

    Requires login at dali.getlulu.dev. History is tied to your GitHub account.
    """
    return call("/api/story", {})


@mcp.tool()
def list_models() -> dict:
    """List all supported generation models with medium, creator, and core strength."""
    return call("/api/models", {})


# ── Resources ──────────────────────────────────────────────────────────────

@mcp.resource("creative://guide/{model}")
def model_guide(model: str) -> str:
    """Full native-language prompt guide for a specific generation model."""
    result = call("/api/guide", {"model": model})
    if "error" in result:
        return f"Could not load guide: {result['error']}"
    return result.get("text", f"No guide found for {model}")


@mcp.resource("creative://models")
def models_overview() -> str:
    """Overview of all supported models and their strengths."""
    result = call("/api/models", {})
    if "error" in result:
        return "Could not load models overview. Is DALI_TOKEN set?"
    lines = [
        "# Dali by Lulu — Supported Generation Models",
        "dali.getlulu.dev | github.com/Lulu-The-Narwhal/dali-mcp",
        "",
    ]
    details = result.get("details", {})
    video = [m for m, d in details.items() if d.get("medium") == "video"]
    image = [m for m, d in details.items() if d.get("medium") == "image"]
    lines.append("## Video Models")
    for m in video:
        d = details[m]
        lines.append(f"- **{m}** ({d.get('by', '')}): {d.get('strength', '')}")
    lines.append("\n## Image Models")
    for m in image:
        d = details[m]
        lines.append(f"- **{m}** ({d.get('by', '')}): {d.get('strength', '')}")
    lines += [
        "\n## Tools",
        "- score_prompt(prompt, model) → 0–100 score + what's missing",
        "- enhance_prompt(prompt, model) → AI rewrites it for the model's native language",
        "- creative_patterns(model) → V3 graph: community A-grade patterns",
        "- community_benchmark(prompt, model) → V3 graph: how you compare to top scorers",
        "- my_story() → scoring history, model stats, creative DNA",
    ]
    return "\n".join(lines)


# ── Entry point ────────────────────────────────────────────────────────────

def main():
    """
    Entry point.
    - DALI_TRANSPORT=http  → streamable-http on PORT (for hosting your own instance)
    - default             → stdio (local / Claude Code)
    """
    transport = os.environ.get("DALI_TRANSPORT", "stdio")
    if transport == "http":
        port = int(os.environ.get("PORT", 8080))
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
