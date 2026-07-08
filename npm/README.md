<!-- mcp-name: io.github.Lulu-The-Narwhal/dali -->
# Dali by Lulu

<p align="center">
  <img src="https://raw.githubusercontent.com/Lulu-The-Narwhal/dali-mcp/main/assets/dali-lulu-scorer.png" alt="Dali by Lulu — creative intelligence MCP" width="100%">
</p>

<p align="center">
  <a href="https://dali.getlulu.dev"><strong>dali.getlulu.dev</strong></a> &nbsp;·&nbsp;
  <a href="https://dali.getlulu.dev/dashboard">Live stats</a> &nbsp;·&nbsp;
  <a href="https://github.com/Lulu-The-Narwhal/dali-mcp">GitHub</a> &nbsp;·&nbsp;
  <a href="https://getlulu.dev">Lulu</a>
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/dali-mcp"><img src="https://img.shields.io/npm/v/dali-mcp.svg" alt="npm version"></a>
  <a href="https://www.npmjs.com/package/dali-mcp"><img src="https://img.shields.io/npm/dm/dali-mcp.svg" alt="npm downloads"></a>
  <a href="https://pypi.org/project/dali-mcp/"><img src="https://img.shields.io/pypi/v/dali-mcp.svg" alt="PyPI version"></a>
  <a href="https://github.com/Lulu-The-Narwhal/dali-mcp/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-server-6b5bff.svg" alt="MCP Server"></a>
</p>

---

**The prediction MCP that helps you avoid the AI generation tax.**

Most AI generation failures are prompt failures. You can't tell the difference until after you've burned the token. Dali scores your prompt *before* you generate — so you never waste a credit on a bad prompt again.

```
You: "make a video ad for our glass serum bottle"

dali::score_prompt(prompt, "veo3")
→ 8/100  Grade: F
→ no camera move · no motion · no lighting · 8 words
→ Verdict: Generic stock footage guaranteed. Enhance first.

dali::enhance_prompt(prompt, "veo3")
→ Returns a rewrite brief — YOUR LLM writes the enhanced prompt:

  ① lead with camera — Veo 3's #1 lever: "Slow dolly", "Orbital push"
  ② describe physics: "a drop falls", "liquid ripples", "glass refracts"
  ③ lighting type + quality: "warm backlight", "rim-lit edges"
  ↳ [Camera]. [Subject + motion]. [Lighting]. [Mood]. [No text.]

✦ Claude rewrites using the brief:

  "Slow orbital push around a glass serum bottle on white marble. A single
   amber drop falls in extreme slow motion, catching warm backlight. Macro:
   liquid gold ripples outward from impact. Rim-lit edges, soft studio
   diffusion. Premium, clinical. No text."

dali::score_prompt(enhanced, "veo3")
→ 91/100  Grade: A  ✓ Safe to generate.
```

---

## What this package is

This is the **npx wrapper** — a thin package that lets stdio-only MCP clients run `npx -y dali-mcp` and connect straight to the hosted Dali server, no Python or local server required.

```json
{
  "mcpServers": {
    "dali": { "command": "npx", "args": ["-y", "dali-mcp"] }
  }
}
```

That's it — no install step, no config beyond this. It resolves and launches [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) pointed at `https://dali.getlulu.dev/mcp` under the hood.

Want to self-host the actual Python server instead (no dependency on the hosted instance)? See **[`pip install dali-mcp`](https://pypi.org/project/dali-mcp/)**.

---

## Tools

| Tool | What it does |
|------|-------------|
| `score_prompt(prompt, model)` | Grade 0–100, letter grade, per-dimension breakdown, what's missing, verdict |
| `enhance_prompt(prompt, model)` | Returns a structured rewrite brief — YOUR LLM writes the enhanced prompt using it |
| `score_and_enhance(prompt, generator)` | Score + enhance in one round-trip |
| `track_enhancement(original, enhanced, generator)` | Record a before/after pair in the graph brain — trains community patterns |
| `suggest_generator(concept, budget_usd_max)` | Pick the best model for your concept + budget |
| `score_variations(prompts, generator)` | Rank a list of prompt variants in one call |
| `creative_patterns(model)` | Community top patterns for this model from the graph brain |
| `community_benchmark(prompt, model)` | Compare your prompt against community top scorers |
| `my_story()` | Your scoring history, model stats, grade distribution |
| `list_models()` | All supported models with medium and core strength |

Supports 13 models across video (Veo 3, Seedance, Kling, Runway, Wan, Minimax, Higgsfield) and image (Flux, Midjourney, Ideogram, Firefly) generation — each scored against its own native prompt language, not a generic rubric.

→ **[Full docs, model tables, and rewrite-brief details](https://github.com/Lulu-The-Narwhal/dali-mcp)**

---

[MIT License](https://github.com/Lulu-The-Narwhal/dali-mcp/blob/main/LICENSE) · Built by [Lulu](https://getlulu.dev) · [dali.getlulu.dev](https://dali.getlulu.dev)
