# Dali by Lulu

<p align="center">
  <img src="assets/dali-lulu-scorer.png" alt="Dali by Lulu — creative intelligence MCP" width="100%">
</p>

<p align="center">
  <a href="https://dali.getlulu.dev"><strong>dali.getlulu.dev</strong></a> &nbsp;·&nbsp;
  <a href="https://dali.getlulu.dev/#install">Install</a> &nbsp;·&nbsp;
  <a href="https://getlulu.dev">Lulu</a>
</p>

---

**The prediction MCP that helps you avoid the AI generation tax.**

Most AI generation failures are prompt failures. You can't tell the difference until after you've burned the token. Dali scores your prompt *before* you generate — so you never waste a credit on a bad prompt again.

```
You: "make a cinematic video of a woman walking in tokyo at night"

dali::score_prompt(prompt, "veo3")
→ 34/100  Grade: D
→ Missing: camera movement, lighting description, motion adverb
→ Verdict: High probability of a generic result. Enhance first.

dali::enhance_prompt(prompt, "veo3")
→ Returns a rewrite brief — YOUR LLM writes the enhanced prompt:

  ① lead with camera movement — Veo 3's #1 lever: "Slow dolly push"
  ② describe motion with adverbs: "walks slowly", "breath drifts"
  ③ lighting: type + quality — "warm sodium-vapor glow", "wet street reflection"
  ↳ [Camera]. [Subject + motion]. [Location]. [Lighting]. [Mood]. [No text.]

✦ Claude rewrites using the brief:

  "Slow dolly push following a woman in her 30s walking through neon-lit
   Shinjuku at 3am. Rain-wet streets reflect pink and blue. Breath visible
   in cold air. Warm sodium-vapor glow above, neon below. Melancholic,
   atmospheric. No text."

→ Score after: 87/100  Grade: A  ✓ Safe to generate.
```

---

## Install

**Hosted MCP — connect once, scores every prompt:**

```bash
# Claude Code
claude mcp add --transport http dali https://dali.getlulu.dev/mcp

# Cursor / Windsurf — add to mcp.json:
{
  "mcpServers": {
    "dali": { "url": "https://dali.getlulu.dev/mcp" }
  }
}
```

→ **[Full install guide with all clients](https://dali.getlulu.dev/#install)**

**Self-hosted — local, no auth required:**

```bash
pip install dali-mcp
claude mcp add dali -- python -m dali.server
```

---

## Tools

| Tool | What it does |
|------|-------------|
| `score_prompt(prompt, model)` | Grade 0–100, letter grade, per-dimension breakdown, what's missing, verdict |
| `enhance_prompt(prompt, model)` | Returns a structured rewrite brief — YOUR LLM writes the enhanced prompt using it |
| `analyze_intent(prompt)` | Parse dimensions: camera, motion, lighting, style, mood, gaps |
| `creative_patterns(model)` | Community top patterns for this model from the graph brain |
| `community_benchmark(prompt, model)` | Compare your prompt against community top scorers |
| `my_story()` | Your scoring history, model stats, grade distribution |
| `list_models()` | All supported models with medium and core strength |

---

## Supported models

### Video

| Model | Platforms | Best for | Prompt style |
|-------|-----------|----------|--------------|
| `veo3` | Higgsfield, Google AI Studio (`veo-3.1-generate-preview`), Runway | Cinematic brand films, narrative ads, photorealistic motion | Cinematography → Subject → Action → Context → Style → Audio |
| `seedance` | Higgsfield, fal.ai (`bytedance/seedance-2.0`) | UGC, social-native content, TikTok/Reels performance ads | Natural language, motion-first, authentic feel |
| `kling` | Higgsfield (`kling3`), Kling.ai (`kling-v3-text-to-video`) | Character animation, product showcases, facial performance | Scene → Characters → Action → Camera → Style; multi-shot labels |
| `runway` | Runway (`gen4.5`) | VFX, character performance, cinematic motion | Motion-first — describe what moves, not what exists |
| `wan` | fal.ai (`fal-ai/wan/v2.7/reference-to-video`) | 4K, 20-second clips, open-source workflows | Natural language; supports first/last frame, native audio |
| `minimax` | fal.ai (`fal-ai/minimax/hailuo-02/pro/text-to-video`) | Cinematic storytelling, character animation | Natural language + `[camera movement]` bracket syntax |
| `higgsfield` | Higgsfield (native model) | Physics-driven motion — cloth, hair, fluid, particles | Describe materials in motion, not motion abstractly |

> **Sora 2** (OpenAI): API shutdown September 24, 2026. Do not build new dependencies on it — use Runway or Kling instead.

### Image

| Model | Platforms | Best for | Prompt style |
|-------|-----------|----------|--------------|
| `flux` | BFL API (`flux-2-pro`), fal.ai, Replicate | Photorealism, technical photography, product shots | 30–80 words; camera body + lens specs; front-load subject; no negatives |
| `midjourney` | Midjourney (v8.1) | Artistic depth, editorial, stylized illustration | Prose + params appended: `--ar 16:9 --s 300 --v 8.1 --style raw` |
| `ideogram` | Ideogram API (`V_4`), fal.ai | Typography, logos, text-in-image, graphic design | Describe text exactly in quotes inside the prompt |
| `firefly` | Adobe Firefly 5 (enterprise) | IP-indemnified commercial assets, 4MP brand content | Natural language + `contentClass` and `style.presets` API params |

> **Imagen 4** (Google): Deprecated August 17, 2026. Use `gemini-3.1-flash-image` for new builds.

---

## Platform supersets

**Higgsfield** and **Runway** are aggregator platforms — they proxy multiple underlying models under one API. When you're on Higgsfield, the model you pick matters more than the platform:

| Higgsfield API ID | Underlying model |
|-------------------|-----------------|
| `veo3` | Google Veo 3.1 |
| `seedance` / `seedance1-5` | ByteDance Seedance 1.0 / 1.5 |
| `kling3` / `kling2-6` | Kling 3 / Kling 2.6 |
| `sora2-video` | OpenAI Sora 2 |
| `wan2-6` / `wan2-7` | Wan 2.6 / 2.7 |
| `image2video` | Higgsfield native |

Dali scores and enhances for the **underlying model's native prompt language**, not the platform wrapper. Pass the model name (`veo3`, `kling`, `seedance`...), not the platform name.

---

## Why model-specific?

Generic prompt optimizers don't know that:
- **Veo 3.1** needs camera movement specified above everything else
- **Kling 3** supports multi-shot scene labels natively in the prompt
- **Flux 2** responds to camera body and lens names like a photographer (`"Sony A7 IV, 85mm f/1.4"`)
- **Midjourney V8.1** reads prose + parameters, not keyword lists
- **Higgsfield** simulates physics — you describe materials in motion, not motion abstractly
- **Minimax Director** uses `[Pan left]` bracket syntax for camera moves
- **Ideogram V4** needs text quoted exactly in the prompt for typography accuracy

Dali has a separate scoring rubric and Gemini enhancement system prompt for each model.

---

## MCP resources

```
creative://guide/veo3       → Veo 3.1 camera language + audio cue guide
creative://guide/seedance   → Seedance UGC motion guide
creative://guide/kling      → Kling multi-shot + expression guide
creative://guide/runway     → Runway motion-first guide
creative://guide/wan        → Wan 2.7 guide
creative://guide/minimax    → Minimax bracket camera guide
creative://guide/higgsfield → Higgsfield physics-motion guide
creative://guide/flux       → Flux 2 photography brief guide
creative://guide/midjourney → Midjourney V8.1 + parameters guide
creative://guide/ideogram   → Ideogram V4 typography guide
creative://guide/firefly    → Firefly 5 commercial content guide
creative://models           → All models overview
```

---

## Contributing

Model guides live in `dali/data/guides/{model}.json` in the private hosted server. Found practitioner patterns that consistently produce high-grade results? Open an issue with the model, the pattern, and a sample prompt + result. The best contributions come from Reddit, Discord, and YouTube — real practitioners, not official docs.

---

MIT License · Built by [Lulu](https://getlulu.dev) · [dali.getlulu.dev](https://dali.getlulu.dev)
