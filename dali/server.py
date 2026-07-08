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
  score_and_enhance    — score + enhance in one call, returns both versions
  track_enhancement    — record a before/after pair in the graph (trains community data)
  suggest_generator    — pick the best model for concept + budget
  score_variations     — rank multiple prompt variants in one call
  dali_version         — server version + changelog
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
        "- score_and_enhance(prompt, generator) — score + enhance in one round-trip\n"
        "- track_enhancement(original, enhanced, generator) — record A/B pair in graph\n"
        "- suggest_generator(concept, budget_usd_max) — pick best model for concept + budget\n"
        "- score_variations(prompts, generator) — rank multiple variants in one call\n"
        "- dali_version() — server version + changelog\n"
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



@mcp.tool()
def score_and_enhance(
    prompt: str,
    generator: str,
) -> dict:
    """
    Score a prompt AND get an AI-enhanced version in one call.

    Combines score_prompt + enhance_prompt into a single round-trip.
    Returns: original score, enhanced prompt, and new score — so you can
    see the exact improvement before deciding which version to use.

    Args:
        prompt:    The prompt to score and enhance
        generator: Target generation model (veo3, seedance, higgsfield, flux, midjourney, etc.)
    """
    return call("/api/score_and_enhance", {"prompt": prompt, "generator": generator})


@mcp.tool()
def track_enhancement(
    original_prompt: str,
    enhanced_prompt: str,
    generator: str,
) -> dict:
    """
    Record a before/after enhancement pair in the Dali graph.

    Call this after you've written an enhanced prompt using the rewrite brief
    from enhance_prompt. This trains the community graph with real A/B data —
    contributing to creative_patterns and community_benchmark for all users.

    Args:
        original_prompt: The un-enhanced prompt
        enhanced_prompt: The version you actually improved
        generator:       Target generation model
    """
    return call("/api/track_enhancement", {
        "original_prompt": original_prompt,
        "enhanced_prompt": enhanced_prompt,
        "generator": generator,
    })


@mcp.tool()
def suggest_generator(
    concept: str,
    budget_usd_max: float = 1.0,
) -> dict:
    """
    Pick the best generation model for a creative concept + budget.

    Analyzes the concept (motion, style, realism requirements) and returns
    a ranked list of generators with rationale and estimated cost per generation.

    Args:
        concept:        What you want to create (plain language or a prompt)
        budget_usd_max: Max spend per generation in USD (default $1.00)
    """
    return call("/api/suggest_generator", {
        "concept": concept,
        "budget_usd_max": budget_usd_max,
    })


@mcp.tool()
def score_variations(
    prompts: list,
    generator: str,
) -> dict:
    """
    Score multiple prompt variations for the same generator in one call.

    Returns a ranked list — highest to lowest score — so you can immediately
    see which variation to send to generation. Best used after writing 2–5
    candidate prompts and wanting to pick the winner objectively.

    Args:
        prompts:   List of prompt strings to compare (2–10 recommended)
        generator: Target generation model
    """
    return call("/api/score_variations", {"prompts": prompts, "generator": generator})


@mcp.tool()
def dali_version() -> dict:
    """
    Return the current Dali server version and changelog.

    Useful for checking if your MCP is connected to the latest server,
    or for debugging version mismatches between the pip package and hosted API.
    """
    from .client import get_call
    return get_call("/api/version")

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
