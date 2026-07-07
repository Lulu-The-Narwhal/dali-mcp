# SKILL: Dali Creative Intelligence — Proactive Prompt Scoring

You have access to the **Dali MCP** (`dali.getlulu.dev`). Use it BEFORE any image or video generation.
The golden rule: **never spend a generation credit on an unscored prompt.**

## When to activate

Any time the user's intent involves generating, creating, rendering, or making an image or video:
- Keywords: generate, create, make, draw, render, animate, illustrate, design, produce
- Media types: image, photo, picture, video, clip, footage, reel, scene, animation

Also activate when a user pastes a raw prompt without asking to score it — score it anyway.

## The Flow

### Step 1: Detect model
If the user doesn't specify a model, infer from context:

**Video:**
- Cinematic brand/narrative → `veo3`
- UGC, TikTok, social → `seedance`
- Character animation, facial performance → `kling`
- VFX, motion-first → `runway`
- Native audio, 4K → `wan`
- Cinematic storytelling with camera control → `minimax`
- Physics-driven (cloth, hair, fluid) → `higgsfield`

**Image:**
- Photorealistic, product photography → `flux`
- Artistic, editorial, stylized → `midjourney`
- Typography, logos, text-in-image → `ideogram`
- IP-safe commercial → `firefly`

If still ambiguous: "Which model are you targeting?" and list: `veo3, seedance, kling, runway, wan, minimax, higgsfield, flux, midjourney, ideogram, firefly`

### Step 2: Score immediately
Call `score_prompt(prompt=<prompt>, model=<model>)`.

Present concisely:
- Grade + score: "**Grade C — 58/100**"
- 2–3 bullet points of what's missing (from `missing` array)
- One-line verdict

### Step 3: Decision

| Grade | Score | Action |
|-------|-------|--------|
| A | 90+ | Confirm and generate |
| B | 70–89 | Confirm and generate |
| C | 50–69 | Offer to enhance. If user agrees or doesn't object → enhance |
| D/F | < 50 | Enhance automatically. Show before/after. Use enhanced prompt. |

### Step 4: Enhance (when triggered)
Call `enhance_prompt(prompt=<prompt>, model=<model>)`.

The tool returns a **rewrite brief** — not a finished prompt. YOU write the enhanced prompt using it.

The brief contains:
- `native_language_rules` — how this model thinks
- `structure_template` — the prompt format to follow
- `priority_fixes` — what to add, by weight × gap
- `length_target` — target word count
- `what_to_add` — specific missing elements

**Your job**: write the enhanced prompt using these rules. Then call `score_prompt` on what you wrote to verify improvement.

Show:
- Score delta: "8 → 91 (+83 pts)"
- What changed (key additions from the brief)
- Enhanced prompt in a code block
- Score verification result

### Step 5: Generate
Always use the highest-scoring prompt (your enhanced version, not a raw API field).

## Output format (keep it tight)

```
Scored: **Grade F — 8/100** for Veo3
Missing: camera move, motion description, lighting · 8 words only
Verdict: Generic stock footage guaranteed. Enhancing...

Brief applied:
  ① camera move first: "Slow orbital push"
  ② physics: "drop falls", "liquid ripples", "glass refracts"
  ③ lighting: "warm backlight", "rim-lit edges"

Enhanced prompt:
```
"Slow orbital push around a glass serum bottle on white marble. A single amber
drop falls in extreme slow motion, catching warm backlight. Macro: liquid gold
ripples outward from impact. Rim-lit edges, soft studio diffusion. Premium,
clinical. No text."
```

Re-scored: **Grade A — 91/100** ✓ Safe to generate.
Ready to generate with this?
```

## Rules

- Score FIRST, always — before generating anything
- Don't ask permission to score — just do it
- Do ask permission to enhance if grade is C (auto-enhance D/F)
- Never dump raw JSON — translate to human-readable output
- Lead with grade + missing — not the full dimension breakdown
- **You write the enhanced prompt from the brief** — don't look for an `enhanced_prompt` field in the response
- Always re-score your enhanced version to show the delta

## Community tools (bonus)

- Grade C or below → call `community_benchmark(prompt, model)` to show missing A-grade patterns
- "What makes a good [model] prompt?" → call `creative_patterns(model)` and summarize top 5
- "Show my history" → call `my_story()`
- "What models do you support?" → call `list_models()`
