# Dali Prompt Best Practices

Model-specific patterns that consistently score A or B. Sourced from Reddit, Discord, and YouTube creators — not official docs.

---

## Video models

### Veo 3.1 (`veo3`)

**The rule: camera move first. Everything else follows.**

```
Slow dolly push following [subject] as [motion with adverb]. [Location/time].
[Lighting type] + [lighting quality]. [Style anchor]. No text.
```

| Do | Don't |
|----|-------|
| "Slow dolly push" / "Orbital camera" / "Static wide" | Start with the subject |
| "gently cascades", "slowly drifts" | Just "cascades", "drifts" |
| "warm sodium-vapor glow, wet street reflection" | "good lighting" |
| End with "Cinematic. No text." | Leave mood unanchored |
| 50–120 words | One-liners |

**Top pattern**: `[Camera]. [Subject + motion adverb]. [Location]. [Lighting: type + quality]. [Style]. No text.`

---

### Seedance 2.0 (`seedance`)

**Write like you're describing a video to a friend. No cinematography jargon.**

```
A [person description] [does action] in [location]. [Natural light cue].
Shot in a [UGC/authentic style] way.
```

| Do | Don't |
|----|-------|
| "A woman holds up the product and smiles at camera" | "Cinematic shot of woman" |
| "Morning light through the window" | "Studio lighting" |
| "TikTok-style", "authentic feel" | Cinematography terms |
| 20–60 words | Overly detailed prompts |

**Top pattern**: `[Person + action]. [Natural light]. [Social context: TikTok/Reels/UGC].`

---

### Kling 3 (`kling`)

**Motion amplitude and expression are your biggest levers.**

```
[Subject with expression]. [Motion with amplitude modifier] in [location].
[Camera move]. [Mood].
```

| Do | Don't |
|----|-------|
| "subtle sway", "dramatic turn", "gentle tilt" | "moves", "walks" |
| "warm smile", "focused expression", "wide-eyed" | Skip expression |
| "Shot 1: ...\nShot 2: ..." for multi-shot | Freeform paragraphs |
| "Intimate. Warm." as a closing line | No mood anchor |

**Multi-shot pattern**: Label each beat — `Shot 1:`, `Shot 2:`, etc. Kling reads these natively.

---

### Runway Gen 4.5 (`runway`)

**Motion is the noun. Subject is the vehicle.**

```
[Physical force or motion]. [Subject in that motion]. Camera [tracking move].
[Location]. [Style].
```

| Do | Don't |
|----|-------|
| Open with a verb or force: "Rain crashes", "Wind tears through", "Light floods" | Static descriptions |
| Physical forces: gravity, wind, water, pressure | Abstract descriptions of stillness |
| Camera tracking AFTER establishing motion | Lead with camera |
| 30–80 words, tight | Long atmospheric paragraphs |

**Rule**: If nothing moves in your prompt, nothing will move in the output.

---

### Wan 2.7 (`wan`)

**Describe the sound. Wan generates native audio from the prompt.**

```
[Scene description]. [Motion description]. We hear [sound description].
[Duration pacing]. [Mood].
```

| Do | Don't |
|----|-------|
| "We hear rain pattering softly on leaves" | Skip audio |
| "Accompanied by a slow jazz piano" | Assume it'll infer audio |
| "15 seconds", "brief moment", "gradually" | Unspecified duration |
| Scene → Motion → Sound → Mood order | Random order |

---

### Minimax Hailuo 2 (`minimax`)

**Brackets are required for camera moves. Plain text is ignored.**

```
[Scene]. [Subject action]. [Emotional beat]. [Pan left] or [Dolly in].
```

| Do | Don't |
|----|-------|
| `[Pan left]`, `[Dolly in]`, `[Close-up]`, `[Tracking shot]` | "pan left", "dolly in" (no brackets) |
| Multiple brackets in one prompt | One camera move max |
| Natural language for everything except camera | Use brackets for non-camera text |

**Rule**: `[bracket]` syntax = camera. Natural language = everything else.

---

### Higgsfield (`higgsfield`)

**Name the physics. Describe materials in motion, not motion abstractly.**

```
[Material in motion: silk draping / hair streaming / water cascading].
[Character detail]. [Camera movement]. [Style].
```

| Do | Don't |
|----|-------|
| "silk draping", "hair streaming in wind", "water cascading over stone" | "things move naturally" |
| Name the physics: "cloth simulation", "fluid dynamics", "particle trail" | Vague movement language |
| Separate character physics from camera movement | Conflate them |
| Omit "stay still" | "Stay still" creates physics conflicts |

---

## Image models

### Flux Pro (`flux`)

**Write a photography brief, not a description.**

```
[Camera body], [lens], [aperture]. [Subject front-loaded]. [Lighting: type + quality].
[Technical style].
```

| Do | Don't |
|----|-------|
| "Sony A7 IV, 85mm f/1.4, f/1.8" | Omit camera specs |
| "Hasselblad", "Leica M11", "Fujifilm GFX" for premium feel | Generic "professional camera" |
| 60–150 words with technical specificity | Short vague descriptions |
| Subject first, then specs, then lighting | Specs first |

---

### Midjourney V8.1 (`midjourney`)

**Keyword list + parameters. Not sentences.**

```
[subject], [style descriptors], [lighting], [mood], [composition] --ar 16:9 --s 300 --v 8.1 --style raw
```

| Do | Don't |
|----|-------|
| Comma-separated keywords | Full sentences |
| `--ar 16:9 --s 300 --v 8.1 --style raw` appended | Forget parameters |
| Style refs: "in the style of [artist]" | Generic "beautiful" |
| Lighting keywords: "rim lighting", "golden hour", "dramatic side light" | Skip lighting |
| Remove conversational language | "please make", "I want" |

---

### Ideogram V4 (`ideogram`)

**Text to render MUST be in double quotes inside the prompt.**

```
[Background/composition context]. [Font style]: "[TEXT IN QUOTES]". [Color palette].
```

| Do | Don't |
|----|-------|
| `"SALE"`, `"Open"`, `"DailyWell"` — exact text in double quotes | "text that says SALE" |
| Keep each text element under 5 words | Long text strings |
| Describe font: "bold sans-serif", "neon 3D", "handwritten", "italic serif" | Skip font style |
| Describe the background + composition | Prompt only the text |

---

### Adobe Firefly 5 (`firefly`)

**Commercial context explicit. No trademarked names.**

```
[Commercial context: product photography / brand asset]. [Subject precision].
[Lighting setup]. [Style]. [Color mood].
```

| Do | Don't |
|----|-------|
| "product photography for a health supplement brand" | Vague "photo of a bottle" |
| "professional", "editorial", "clean studio", "lifestyle" | Generic "high quality" |
| End with color mood: "Warm amber tones. Premium feel." | Skip mood |
| Avoid trademarked brands, characters | Name real brands/IPs (defeats IP-safety) |

---

## Universal rules

1. **Score before you generate.** A D-grade prompt wastes the credit. `score_prompt → enhance_prompt → generate`.
2. **Specificity beats quality adjectives.** "warm sodium-vapor glow" > "beautiful lighting".
3. **Name the motion, not the result.** "silk draping over her shoulder" > "looks elegant".
4. **Camera ≠ style.** They're separate signals. Both matter.
5. **End with an anchor.** A mood/style closing line (even just "Cinematic. No text.") consistently lifts scores.

---

## Contributing

Found a pattern that consistently scores A on a specific model? [Open an issue](https://github.com/Lulu-The-Narwhal/dali-mcp/issues) with:
- Model name
- The pattern (ideally as a template)
- A real prompt + result that scored A

Source it from Reddit, Discord, or YouTube — practitioner evidence beats theory.
