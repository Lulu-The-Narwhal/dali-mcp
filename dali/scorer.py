"""
Scoring engine — per-model heuristic scoring of AI generation prompts.
Each model has its own dimension weights derived from what actually works.
"""

from __future__ import annotations
from dataclasses import dataclass
from .intent import analyze_intent, IntentMap


@dataclass
class ScoreCard:
    model: str
    prompt_preview: str
    overall: int                     # 0–100
    grade: str                       # A / B / C / D / F
    dimensions: dict[str, int]       # dimension → 0–100
    missing: list[str]               # what would push the score up
    antipatterns: list[str]          # detected known bad patterns
    verdict: str                     # one-line call

    def as_dict(self) -> dict:
        return {
            "model": self.model,
            "prompt_preview": self.prompt_preview,
            "overall": self.overall,
            "grade": self.grade,
            "dimensions": self.dimensions,
            "missing": self.missing,
            "antipatterns": self.antipatterns,
            "verdict": self.verdict,
        }


# ── Grade thresholds ───────────────────────────────────────────────────────

def _grade(score: int) -> str:
    if score >= 85: return "A"
    if score >= 70: return "B"
    if score >= 55: return "C"
    if score >= 40: return "D"
    return "F"


def _verdict(score: int, model: str) -> str:
    if score >= 85: return f"Strong prompt — safe to generate on {model}."
    if score >= 70: return f"Good, minor gaps — consider adding camera/lighting before generating."
    if score >= 55: return f"Mediocre — spending a credit now risks a generic result."
    if score >= 40: return f"Weak — high probability of a disappointing output. Enhance first."
    return f"Very likely to waste a credit. Rewrite before generating."


# ── Per-model scorers ──────────────────────────────────────────────────────

def _score_veo3(prompt: str, intent: IntentMap) -> dict[str, int]:
    p = prompt.lower()
    dims: dict[str, int] = {}

    # Camera language — CRITICAL for Veo
    cam_score = min(100, len(intent.camera_language) * 35 + (20 if intent.has_camera else 0))
    dims["camera_language"] = min(100, cam_score)

    # Motion description
    mot_score = min(100, len(intent.motion_terms) * 25 + (10 if intent.has_motion else 0))
    dims["motion_description"] = min(100, mot_score)

    # Lighting
    lit_score = min(100, len(intent.lighting_terms) * 35 + (10 if intent.has_lighting else 0))
    dims["lighting"] = min(100, lit_score)

    # Subject specificity — rough: longer prompts usually more specific
    sub_score = min(100, max(0, (intent.word_count - 5) * 3))
    dims["subject_specificity"] = min(100, sub_score)

    # Style anchor
    dims["style_anchor"] = min(100, len(intent.style_terms) * 40) if intent.has_style else 0

    # Optimal length: 50–120 words
    wc = intent.word_count
    if 50 <= wc <= 120:
        dims["prompt_length"] = 100
    elif 30 <= wc < 50 or 120 < wc <= 160:
        dims["prompt_length"] = 70
    elif 15 <= wc < 30 or 160 < wc <= 200:
        dims["prompt_length"] = 40
    else:
        dims["prompt_length"] = 10

    return dims


def _score_higgsfield(prompt: str, intent: IntentMap) -> dict[str, int]:
    p = prompt.lower()
    dims: dict[str, int] = {}

    # Motion physics — the most important thing in Higgsfield
    physics_terms = {"cloth", "hair", "water", "smoke", "fire", "wind",
                     "fluid", "fabric", "draping", "ripple", "splash", "particle"}
    physics_hits = sum(1 for t in physics_terms if t in p)
    dims["motion_physics"] = min(100, physics_hits * 30 + len(intent.motion_terms) * 15)

    # Character consistency cues
    consist_terms = {"consistent", "same character", "character", "face", "expression",
                     "identity", "portrait", "subject"}
    dims["consistency_cues"] = min(100, sum(30 for t in consist_terms if t in p))

    # Camera + motion separation
    dims["camera_movement"] = min(100, len(intent.camera_language) * 40)

    # Style preset language
    style_score = min(100, len(intent.style_terms) * 35)
    dims["style"] = style_score

    # Subject detail
    wc = intent.word_count
    dims["subject_detail"] = min(100, max(0, (wc - 5) * 2))

    return dims


def _score_midjourney(prompt: str, intent: IntentMap) -> dict[str, int]:
    p = prompt.lower()
    dims: dict[str, int] = {}

    # Style reference — king in MJ
    artist_patterns = ["by ", "in the style of", "inspired by", "--style"]
    style_refs = sum(1 for pat in artist_patterns if pat in p)
    dims["style_reference"] = min(100, style_refs * 50 + len(intent.style_terms) * 25)

    # Aspect ratio (--ar)
    dims["aspect_ratio"] = 100 if "--ar" in p else 0

    # Lighting
    dims["lighting"] = min(100, len(intent.lighting_terms) * 35 + (15 if intent.has_lighting else 0))

    # Composition / framing
    comp_terms = {"composition", "foreground", "background", "rule of thirds",
                  "centered", "symmetrical", "diagonal", "depth", "layered"}
    dims["composition"] = min(100, sum(25 for t in comp_terms if t in p))

    # Keyword density (MJ loves comma-separated nouns, not sentences)
    commas = p.count(",")
    dims["keyword_format"] = min(100, commas * 15 + (20 if commas >= 3 else 0))

    # Parameters
    params = ["--q", "--s", "--v", "--chaos", "--stylize", "--seed"]
    dims["parameters"] = min(100, sum(35 for par in params if par in p))

    return dims


def _score_flux(prompt: str, intent: IntentMap) -> dict[str, int]:
    p = prompt.lower()
    dims: dict[str, int] = {}

    # Style specificity — most important in Flux
    artist_refs = sum(1 for pat in ["by ", "photograph by", "shot on", "film by", "style of"] if pat in p)
    camera_refs = ["leica", "hasselblad", "sony a7", "fujifilm", "kodak", "35mm", "85mm", "50mm"]
    cam_hits = sum(1 for c in camera_refs if c in p)
    dims["style_specificity"] = min(100, artist_refs * 40 + cam_hits * 30 + len(intent.style_terms) * 20)

    # Technical photography terms
    tech_terms = {"f/", "iso ", "shutter", "aperture", "bokeh", "depth of field",
                  "sharp focus", "lens flare", "chromatic"}
    dims["technical_photography"] = min(100, sum(25 for t in tech_terms if t in p))

    # Lighting
    dims["lighting"] = min(100, len(intent.lighting_terms) * 35 + (15 if intent.has_lighting else 0))

    # Negative prompt (Flux supports it — big boost)
    dims["negative_prompt"] = 100 if "negative:" in p or "no " in p or "avoid" in p else 0

    # Subject detail (Flux rewards verbosity)
    wc = intent.word_count
    dims["subject_detail"] = min(100, max(0, wc * 2))

    return dims


def _score_kling(prompt: str, intent: IntentMap) -> dict[str, int]:
    p = prompt.lower()
    dims: dict[str, int] = {}

    # Motion amplitude — Kling's superpower
    amplitude_terms = {"subtle", "slight", "gentle", "dramatic", "explosive", "slow", "rapid",
                       "exaggerated", "minimal", "extreme"}
    amp_hits = sum(1 for t in amplitude_terms if t in p)
    dims["motion_amplitude"] = min(100, amp_hits * 30 + len(intent.motion_terms) * 15)

    # Expression description
    expression_terms = {"smile", "smiling", "laughing", "crying", "frowning", "wide-eyed",
                        "expression", "emotion", "intense", "serene", "shocked", "grinning"}
    dims["expression"] = min(100, sum(30 for t in expression_terms if t in p))

    # Camera movement
    dims["camera_movement"] = min(100, len(intent.camera_language) * 40)

    # Subject detail
    dims["subject_detail"] = min(100, max(0, (intent.word_count - 5) * 3))

    # Mood/atmosphere
    dims["mood"] = min(100, len(intent.mood_terms) * 40 + (20 if intent.has_mood else 0))

    return dims


def _score_sora(prompt: str, intent: IntentMap) -> dict[str, int]:
    p = prompt.lower()
    dims: dict[str, int] = {}

    # Temporal consistency cues
    consist_terms = {"consistent", "throughout", "same", "continuously", "maintaining", "stable"}
    dims["temporal_consistency"] = min(100, sum(30 for t in consist_terms if t in p))

    # Sequence / narrative structure
    sequence_terms = ["first", "then", "next", "finally", "before", "after", "transitions to",
                      "cuts to", "dissolves"]
    dims["narrative_structure"] = min(100, sum(25 for t in sequence_terms if t in p))

    # Camera
    dims["camera_movement"] = min(100, len(intent.camera_language) * 40)

    # Motion
    dims["motion"] = min(100, len(intent.motion_terms) * 30 + (20 if intent.has_motion else 0))

    # Lighting
    dims["lighting"] = min(100, len(intent.lighting_terms) * 35 + (10 if intent.has_lighting else 0))

    return dims


def _score_imagen(prompt: str, intent: IntentMap) -> dict[str, int]:
    p = prompt.lower()
    dims: dict[str, int] = {}

    # Style specificity
    dims["style"] = min(100, len(intent.style_terms) * 40 + (20 if intent.has_style else 0))

    # Lighting description
    dims["lighting"] = min(100, len(intent.lighting_terms) * 40 + (15 if intent.has_lighting else 0))

    # Camera terms (Imagen loves photography language)
    camera_terms = ["leica", "canon", "nikon", "fujifilm", "35mm", "85mm",
                    "shot on", "photograph", "taken with"]
    dims["camera_language"] = min(100, sum(30 for t in camera_terms if t in p) +
                                  len(intent.camera_language) * 20)

    # Color / palette
    color_terms = ["warm", "cool", "vibrant", "muted", "desaturated", "golden", "teal",
                   "monochrome", "palette", "tones", "hues"]
    dims["color_palette"] = min(100, sum(20 for t in color_terms if t in p))

    # Subject specificity
    dims["subject_detail"] = min(100, max(0, (intent.word_count - 5) * 2))

    return dims


# ── Model registry ─────────────────────────────────────────────────────────

_SCORERS = {
    "veo3":       (_score_veo3,       {"camera_language": 0.25, "motion_description": 0.20,
                                       "lighting": 0.20, "subject_specificity": 0.20,
                                       "style_anchor": 0.10, "prompt_length": 0.05}),
    "higgsfield": (_score_higgsfield, {"motion_physics": 0.30, "consistency_cues": 0.20,
                                       "camera_movement": 0.20, "style": 0.15,
                                       "subject_detail": 0.15}),
    "midjourney": (_score_midjourney, {"style_reference": 0.25, "aspect_ratio": 0.20,
                                       "lighting": 0.20, "composition": 0.15,
                                       "keyword_format": 0.10, "parameters": 0.10}),
    "flux":       (_score_flux,       {"style_specificity": 0.30, "technical_photography": 0.20,
                                       "lighting": 0.20, "negative_prompt": 0.15,
                                       "subject_detail": 0.15}),
    "kling":      (_score_kling,      {"motion_amplitude": 0.30, "expression": 0.20,
                                       "camera_movement": 0.20, "subject_detail": 0.15,
                                       "mood": 0.15}),
    "sora":       (_score_sora,       {"temporal_consistency": 0.25, "narrative_structure": 0.20,
                                       "camera_movement": 0.20, "motion": 0.20,
                                       "lighting": 0.15}),
    "imagen":     (_score_imagen,     {"style": 0.25, "lighting": 0.25, "camera_language": 0.20,
                                       "color_palette": 0.15, "subject_detail": 0.15}),
}

SUPPORTED_MODELS = list(_SCORERS.keys())


# ── Anti-pattern detection ─────────────────────────────────────────────────

_ANTIPATTERNS: dict[str, list[tuple[str, str]]] = {
    "veo3": [
        ("cartoon", "Veo 3 is a photorealistic model — animation terms confuse it"),
        ("anime", "Veo 3 doesn't do animation styles well"),
        ("draw", "Veo 3 renders, not draws — remove artistic creation verbs"),
    ],
    "midjourney": [
        ("please ", "Conversational language weakens MJ output — use nouns/adjectives"),
        ("make a ", "Conversational language weakens MJ output — use nouns/adjectives"),
        ("i want", "Conversational language weakens MJ output — use nouns/adjectives"),
    ],
    "higgsfield": [
        ("stay still", "Higgsfield defaults to motion — 'stay still' creates conflict"),
    ],
}


def _detect_antipatterns(prompt: str, model: str) -> list[str]:
    p = prompt.lower()
    patterns = _ANTIPATTERNS.get(model, [])
    return [msg for trigger, msg in patterns if trigger in p]


# ── Main scoring entry point ───────────────────────────────────────────────

def score_prompt(prompt: str, model: str) -> ScoreCard:
    """Score a prompt for a specific generation model. Returns a ScoreCard."""
    model = model.lower().replace("-", "").replace("_", "").replace(".", "")
    # Normalize aliases
    aliases = {"veo": "veo3", "veo31": "veo3", "mj": "midjourney", "sd": "flux",
               "stablediffusion": "flux", "dalle": "dalle3", "dall-e": "dalle3"}
    model = aliases.get(model, model)

    if model not in _SCORERS:
        raise ValueError(f"Unknown model '{model}'. Supported: {', '.join(SUPPORTED_MODELS)}")

    intent = analyze_intent(prompt)
    scorer_fn, weights = _SCORERS[model]
    raw_dims = scorer_fn(prompt, intent)

    # Weighted average
    total_weight = sum(weights.values())
    overall = 0
    for dim, w in weights.items():
        overall += raw_dims.get(dim, 0) * (w / total_weight)
    overall = round(overall)

    antipatterns = _detect_antipatterns(prompt, model)
    if antipatterns:
        overall = max(0, overall - 10 * len(antipatterns))

    missing = [g for g in intent.gaps if g]
    if not intent.has_subject:
        missing.insert(0, "no concrete subject detected — add a person, place, or object")

    preview = prompt[:80] + "..." if len(prompt) > 80 else prompt

    return ScoreCard(
        model=model,
        prompt_preview=preview,
        overall=overall,
        grade=_grade(overall),
        dimensions=raw_dims,
        missing=missing,
        antipatterns=antipatterns,
        verdict=_verdict(overall, model),
    )
