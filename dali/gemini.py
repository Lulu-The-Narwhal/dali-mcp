"""
Gemini-powered prompt enhancement engine.
Takes a raw prompt + model guide + score gaps → returns an actually better prompt.

Uses gemini-3.5-flash. Requires GEMINI_API_KEY in environment.
"""

from __future__ import annotations
import os
from typing import Optional

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
MODEL = "gemini-3.5-flash"

_VIDEO_MODELS = {"veo3", "higgsfield", "kling", "sora"}
_IMAGE_MODELS = {"midjourney", "flux", "imagen", "dalle3"}

_SYSTEM_TEMPLATE = """You are Dali — an expert creative director specialized in writing AI generation prompts for {model_name}.

You know the exact language, structure, and signals that make {model_name} produce exceptional results.

## Your knowledge of {model_name}:

{guide}

## Your task:

The user will give you:
1. Their original prompt
2. The current score (0-100) and what's missing
3. What to keep (their creative intent)

You will return ONLY the enhanced prompt — no explanation, no commentary, no score.

## Rules:
- Keep the core creative concept exactly — don't change what they're trying to make
- Add the specific missing elements ({medium} signals: {key_signals})
- Use {model_name}'s native vocabulary from the guide above
- Length: {length_guidance}
- Output format: just the prompt text, nothing else. No quotes, no labels.
"""

_VIDEO_SIGNALS = "camera movement, motion description, lighting, atmosphere"
_IMAGE_SIGNALS = "style reference, lighting setup, composition, camera/lens"

_LENGTH_GUIDANCE = {
    "veo3":       "50-120 words (DP brief, not a novel)",
    "higgsfield": "40-100 words (focus on physics-driven motion)",
    "kling":      "40-100 words (focus on motion amplitude + expression)",
    "sora":       "60-130 words (describe the sequence, not just the frame)",
    "midjourney": "20-60 words of comma-separated descriptors + parameters",
    "flux":       "60-150 words (photography brief, be technical)",
    "imagen":     "50-120 words (photography genre brief)",
}


def enhance_with_gemini(
    prompt: str,
    model: str,
    guide_text: str,
    missing: list[str],
    antipatterns: list[str],
    score_before: int,
) -> Optional[str]:
    """
    Call Gemini to rewrite the prompt for the target model.
    Returns the enhanced prompt string, or None if Gemini is unavailable.
    """
    if not GEMINI_API_KEY:
        return None

    try:
        from google import genai
        from google.genai import types as gtypes
    except ImportError:
        return None

    medium      = "video" if model in _VIDEO_MODELS else "image"
    key_signals = _VIDEO_SIGNALS if medium == "video" else _IMAGE_SIGNALS
    length      = _LENGTH_GUIDANCE.get(model, "50-120 words")

    system_prompt = _SYSTEM_TEMPLATE.format(
        model_name=model,
        guide=guide_text[:3000],
        medium=medium,
        key_signals=key_signals,
        length_guidance=length,
    )

    missing_block = "\n".join(f"- {m}" for m in missing) if missing else "- none identified"
    anti_block    = "\n".join(f"- {a}" for a in antipatterns) if antipatterns else "- none"

    user_message = (
        f"Original prompt (score: {score_before}/100):\n"
        f"\"{prompt}\"\n\n"
        f"What's missing (add these):\n{missing_block}\n\n"
        f"Anti-patterns to fix:\n{anti_block}\n\n"
        f"Rewrite it now."
    )

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=MODEL,
            contents=user_message,
            config=gtypes.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=512,
            ),
        )
        enhanced = response.text.strip()
        # Strip any accidental quotes the model might add
        if enhanced.startswith('"') and enhanced.endswith('"'):
            enhanced = enhanced[1:-1]
        return enhanced
    except Exception:
        return None
