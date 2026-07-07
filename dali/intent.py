"""
Intent parser — extracts structured creative intent from raw prompt text.
No LLM calls. Pure heuristic signal extraction.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field

# ── Signal dictionaries ────────────────────────────────────────────────────

CAMERA_TERMS: set[str] = {
    "dolly in", "dolly out", "push in", "pull back", "pan left", "pan right",
    "tilt up", "tilt down", "orbit", "crane shot", "tracking shot", "handheld",
    "static", "aerial", "drone", "close-up", "closeup", "close up",
    "wide shot", "medium shot", "extreme close", "over the shoulder",
    "dutch angle", "bird's eye", "worm's eye", "rack focus", "zoom in",
    "zoom out", "slow push", "dolly zoom",
}

MOTION_TERMS: set[str] = {
    "slowly", "drifting", "drift", "floating", "float", "billowing", "billow",
    "cascading", "cascade", "swirling", "swirl", "rushing", "rush",
    "creeping", "creep", "lurching", "lurch", "swaying", "sway",
    "fluttering", "flutter", "pulsing", "pulse", "oscillating", "oscillate",
    "rippling", "ripple", "exploding", "imploding", "spinning", "spin",
    "rotating", "rotate", "flowing", "flow",
}

LIGHTING_TERMS: set[str] = {
    "golden hour", "blue hour", "sunset", "sunrise", "backlit", "back-lit",
    "silhouette", "rim light", "rim lighting", "neon", "candlelight",
    "moonlight", "moonlit", "studio light", "softbox", "dramatic lighting",
    "volumetric", "god rays", "overcast", "diffused", "harsh shadow",
    "warm light", "cool light", "low key", "high key", "chiaroscuro",
    "dappled", "fluorescent", "ambient",
}

STYLE_TERMS: set[str] = {
    "cinematic", "photorealistic", "photorealism", "realistic", "hyperrealistic",
    "hyper-realistic", "artistic", "stylized", "anime", "illustration",
    "painterly", "impressionist", "expressionist", "abstract", "minimalist",
    "documentary", "editorial", "commercial", "film noir", "lo-fi", "retro",
    "vintage", "futuristic", "cyberpunk", "fantasy", "surreal",
}

MOOD_TERMS: set[str] = {
    "dramatic", "peaceful", "serene", "calm", "melancholic", "melancholy",
    "energetic", "tense", "whimsical", "mysterious", "joyful", "ethereal",
    "gritty", "lonely", "haunting", "epic", "intimate", "raw", "intense",
    "euphoric", "somber", "nostalgic", "ominous",
}

VIDEO_HINTS: set[str] = {
    "walking", "running", "flying", "swimming", "dancing", "moving",
    "camera", "shot", "scene", "motion", "animate", "video",
    "seconds", "duration", "clip", "footage", "cinematic", "pan", "dolly",
}

# ── Output types ───────────────────────────────────────────────────────────

@dataclass
class IntentMap:
    medium: str                          # "video" | "image"
    camera_language: list[str]
    motion_terms: list[str]
    lighting_terms: list[str]
    style_terms: list[str]
    mood_terms: list[str]
    word_count: int
    has_subject: bool
    has_camera: bool
    has_lighting: bool
    has_style: bool
    has_motion: bool
    has_mood: bool
    gaps: list[str]
    model_affinity: dict[str, float]     # model → 0–1 score

    def as_dict(self) -> dict:
        return {
            "medium": self.medium,
            "camera_language": self.camera_language,
            "motion_terms": self.motion_terms,
            "lighting_terms": self.lighting_terms,
            "style_terms": self.style_terms,
            "mood_terms": self.mood_terms,
            "word_count": self.word_count,
            "has_subject": self.has_subject,
            "has_camera": self.has_camera,
            "has_lighting": self.has_lighting,
            "has_style": self.has_style,
            "has_motion": self.has_motion,
            "has_mood": self.has_mood,
            "gaps": self.gaps,
            "model_affinity": self.model_affinity,
        }


# ── Core parser ────────────────────────────────────────────────────────────

def _match_terms(text: str, terms: set[str]) -> list[str]:
    text_lower = text.lower()
    return sorted(t for t in terms if t in text_lower)


def _detect_medium(prompt: str) -> str:
    p = prompt.lower()
    score = sum(1 for h in VIDEO_HINTS if h in p)
    return "video" if score >= 2 else "image"


def _has_subject(prompt: str) -> bool:
    """Rough check: does the prompt describe a concrete subject (not just vibes)?"""
    # Any noun-like word sequence counts — heuristic only
    p = prompt.lower()
    subject_patterns = [
        r"\b(a|an|the)\s+\w+",         # "a woman", "an old man", "the forest"
        r"\b(person|woman|man|child|figure|character|creature|building|landscape|object)\b",
    ]
    return any(re.search(pat, p) for pat in subject_patterns)


def _compute_gaps(intent: dict, medium: str) -> list[str]:
    gaps = []
    if not intent["has_camera"] and medium == "video":
        gaps.append("no camera movement specified (e.g. 'slow dolly push', 'orbit', 'static wide')")
    if not intent["has_lighting"]:
        gaps.append("lighting not described (e.g. 'golden hour', 'dramatic rim light', 'overcast')")
    if not intent["has_style"]:
        gaps.append("style/aesthetic not anchored (e.g. 'cinematic', 'photorealistic', 'editorial')")
    if not intent["has_motion"] and medium == "video":
        gaps.append("subject motion not described (e.g. 'slowly drifting', 'rushing past', 'still')")
    if intent["word_count"] < 15:
        gaps.append("prompt is very short — more detail improves model output significantly")
    if intent["word_count"] > 200:
        gaps.append("prompt may be too long — models can lose focus beyond ~150 words")
    return gaps


def _model_affinity(intent: dict, medium: str) -> dict[str, float]:
    """
    Rough affinity: how well does this prompt's current signals map to each model's strengths?
    This is NOT the score — it's which model will respond best to what's already there.
    """
    camera = int(intent["has_camera"])
    lighting = int(intent["has_lighting"])
    style = int(intent["has_style"])
    motion = int(intent["has_motion"])
    words = intent["word_count"]

    if medium == "video":
        return {
            "veo3":       round(min(1.0, 0.5 + camera * 0.25 + lighting * 0.15 + motion * 0.10), 2),
            "higgsfield": round(min(1.0, 0.5 + motion * 0.30 + camera * 0.10 + lighting * 0.10), 2),
            "kling":      round(min(1.0, 0.5 + motion * 0.25 + camera * 0.15 + style * 0.10), 2),
            "sora":       round(min(1.0, 0.5 + camera * 0.20 + motion * 0.20 + lighting * 0.10), 2),
        }
    else:
        verbose_bonus = 0.1 if words > 40 else 0
        return {
            "midjourney": round(min(1.0, 0.5 + style * 0.25 + lighting * 0.15 + camera * 0.10), 2),
            "flux":       round(min(1.0, 0.5 + style * 0.20 + lighting * 0.15 + verbose_bonus), 2),
            "imagen":     round(min(1.0, 0.5 + lighting * 0.20 + style * 0.15 + camera * 0.15), 2),
            "dalle3":     round(min(1.0, 0.5 + style * 0.15 + lighting * 0.15), 2),
        }


def analyze_intent(prompt: str, medium: str = "auto") -> IntentMap:
    """Parse raw creative text into structured intent dimensions."""
    if medium == "auto":
        medium = _detect_medium(prompt)

    camera   = _match_terms(prompt, CAMERA_TERMS)
    motion   = _match_terms(prompt, MOTION_TERMS)
    lighting = _match_terms(prompt, LIGHTING_TERMS)
    style    = _match_terms(prompt, STYLE_TERMS)
    mood     = _match_terms(prompt, MOOD_TERMS)
    words    = len(prompt.split())

    raw = {
        "has_camera":   len(camera) > 0,
        "has_lighting": len(lighting) > 0,
        "has_style":    len(style) > 0,
        "has_motion":   len(motion) > 0,
        "word_count":   words,
    }

    return IntentMap(
        medium=medium,
        camera_language=camera,
        motion_terms=motion,
        lighting_terms=lighting,
        style_terms=style,
        mood_terms=mood,
        word_count=words,
        has_subject=_has_subject(prompt),
        **raw,
        gaps=_compute_gaps(raw, medium),
        model_affinity=_model_affinity(raw, medium),
    )
