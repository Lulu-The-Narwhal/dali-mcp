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
- Video intent → default to `veo3`
- Realistic image → `flux` or `imagen`
- Artistic/stylized → `midjourney`
- Character animation → `kling` or `higgsfield`
- Narrative video → `sora`

If still ambiguous, ask: "Which model are you targeting? (veo3, midjourney, flux, kling, sora, imagen, higgsfield)"

### Step 2: Score immediately
Call `score_prompt(prompt=<prompt>, model=<model>)`.

Present concisely:
- Grade + score: "**Grade C — 58/100**"
- 2–3 bullet points of what's missing
- One-line verdict

### Step 3: Decision
| Grade | Score | Action |
|-------|-------|--------|
| A     | 90+   | Confirm and generate |
| B     | 70–89 | Confirm and generate |
| C     | 50–69 | Offer to enhance. If user agrees or doesn't object → enhance |
| D/F   | < 50  | Enhance automatically. Show before/after. Use enhanced prompt. |

### Step 4: Enhance (when triggered)
Call `enhance_prompt(prompt=<prompt>, model=<model>)`.

Show:
- Score delta: "58 → 84 (+26 pts)"
- Enhanced prompt in a code block
- What changed (key additions)

Then confirm: "Ready to generate with the enhanced prompt?"

### Step 5: Generate
Always use the highest-scoring prompt. If enhanced, use `enhanced_prompt` from the response.

## Output format (keep it tight)

```
Scored: **Grade C — 58/100** for Veo3
Missing: cinematic camera movement, lighting style, motion description
Verdict: Watchable but flat. Enhancing automatically...

Enhanced: **Grade B — 82/100** (+24 pts)
```<enhanced prompt here>```
Ready to generate?
```

## Rules

- Score FIRST, always — before generating anything
- Don't ask permission to score — just do it
- Do ask permission to enhance if grade is C (auto-enhance D/F)
- Never dump raw JSON — translate to human-readable output
- Lead with grade + missing — not the full dimension breakdown

## Community tools (bonus)

- Grade C or below after scoring → call `community_benchmark(prompt, model)` to show missing A-grade patterns
- "What makes a good [model] prompt?" → call `creative_patterns(model)` and summarize top 5
- "Show my history" → call `my_story()`
