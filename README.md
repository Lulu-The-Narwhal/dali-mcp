<!-- mcp-name: io.github.Lulu-The-Narwhal/dali -->
# Dali by Lulu

<p align="center">
  <img src="https://raw.githubusercontent.com/Lulu-The-Narwhal/dali-mcp/main/assets/dali-lulu-scorer.png" alt="Dali by Lulu — creative intelligence MCP" width="100%">
</p>

<p align="center">
  <a href="https://dali.getlulu.dev"><strong>dali.getlulu.dev</strong></a> &nbsp;·&nbsp;
  <a href="https://dali.getlulu.dev/#install">Install</a> &nbsp;·&nbsp;
  <a href="https://dali.getlulu.dev/dashboard">Live stats</a> &nbsp;·&nbsp;
  <a href="https://getlulu.dev">Lulu</a>
</p>

<p align="center">
  <a href="https://www.producthunt.com/products/dali-by-lulu?utm_source=badge-featured&utm_medium=badge&utm_campaign=badge-dali-by-lulu" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1191380&theme=light&t=1783534343769" alt="Dali by Lulu — featured on Product Hunt" width="250" height="54"></a>
</p>

<p align="center">
  <a href="https://pypi.org/project/dali-mcp/"><img src="https://img.shields.io/pypi/v/dali-mcp.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/dali-mcp/"><img src="https://img.shields.io/pypi/dm/dali-mcp.svg" alt="PyPI downloads"></a>
  <a href="https://www.npmjs.com/package/dali-mcp"><img src="https://img.shields.io/npm/v/dali-mcp.svg" alt="npm version"></a>
  <a href="https://www.npmjs.com/package/dali-mcp"><img src="https://img.shields.io/npm/dm/dali-mcp.svg" alt="npm downloads"></a>
  <a href="https://github.com/Lulu-The-Narwhal/dali-mcp/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-server-6b5bff.svg" alt="MCP Server"></a>
  <a href="https://dali.getlulu.dev/dashboard"><img src="https://img.shields.io/badge/status-live-brightgreen.svg" alt="Live"></a>
</p>

---

**Score your creative against what's actually winning in the ad market — before you spend the credit.**

Most AI generation failures are predictable. A weak prompt, an off-formula creative — you can't tell until after you've burned the token. Dali scores it *first*, and it doesn't grade against opinions or generic "prompt tips." It grades against a **real, living corpus of proven-winning ads** — creatives still running in the market months after launch, scraped, embedded, and ranked. Two jobs:

- **`score_prompt`** — judge the *prompt* before you generate (craft: camera, motion, lighting, model-native language).
- **`score_creative`** — judge the actual *image* against proven winners (does it look like what converts, and what's missing).

Every wasted generation has a real cost — a Seedance retry is ~$6. [The live dashboard](https://dali.getlulu.dev/dashboard) tracks what the community has saved by catching bad creatives before they burned a credit.

```
You: "make a video ad for our glass serum bottle"

dali::score_prompt(prompt, "veo3")
→ 8/100  Grade: F
→ no camera move · no motion · no lighting · 8 words
→ Verdict: Generic stock footage guaranteed. Enhance first.
→ enhancement_brief included (score < 70):

  ① lead with camera — Veo 3's #1 lever: "Slow dolly", "Orbital push"
  ② describe physics: "a drop falls", "liquid ripples", "glass refracts"
  ③ lighting type + quality: "warm backlight", "rim-lit edges"
  ↳ [Camera]. [Subject + motion]. [Lighting]. [Mood]. [No text.]

✦ YOUR LLM rewrites using the brief:

  "Slow orbital push around a glass serum bottle on white marble. A single
   amber drop falls in extreme slow motion, catching warm backlight. Macro:
   liquid gold ripples outward from impact. Rim-lit edges, soft studio
   diffusion. Premium, clinical. No text."

dali::score_prompt(enhanced, "veo3")
→ 91/100  Grade: A  ✓ Safe to generate.
```

---

## The real winning data layer

This is what makes Dali more than a prompt linter. The scores are grounded in **real ads that are actually winning**, not hand-written rules.

**How the corpus is built — longevity is the outcome signal.** We scrape the public Meta Ad Library. An ad still running *months* after it launched is one the advertiser keeps paying for — a **proven winner**. That "still-running-after-N-days" longevity is a market-validated label you can't fake, and it's the spine of the whole dataset.

**What's in it, today:**

| | |
|---|---|
| Ads ingested | **10,204** (14,100 raw archive) |
| Proven winners (long-running) | **3,808** |
| Distinct advertisers | **4,121** |
| Verticals | **8** — beauty, wellness, supplements, fitness, food, apparel, tech, pets |
| Winner creatives embedded | **800** (1408-dim, balanced ~100/vertical) |
| Longest-running winner seen | **2,431 days** (6.6 years live) |

**The pipeline (offline → serving).** The tools never scrape or embed on the fly — they read pre-built stores:

```
scrape Meta Ad Library         → proven winners (longevity label)
      → Gemini vision           → creative attributes (lighting, format, before/after, offer…)
      → prevalence SQL          → winning-pattern lift per vertical (winners vs baseline)
      → Vertex embeddings       → BigQuery VECTOR_SEARCH (nearest proven winners, cosine)
      → graph edges (Memgraph)  → (:Pattern)-[:WINS_IN {lift, n}]->(:Category)
```

So when `score_creative` runs, it embeds your image and finds the **actual winning ads it most resembles** by full visual signature — then tells you which winning attributes you're missing. When `enhance_prompt` runs with a category, the rewrite brief is backed by real market lift ("before/after shows up in 78% of winning wellness ads, 4× baseline"), not craft opinion.

> **Honest scope.** The winner label is *longevity* (a strong market-validated proxy), not per-ad conversion rate — measured CVR validation is in progress. The corpus grows on a schedule, so coverage per vertical keeps deepening. What you get today: your creative scored against what's *demonstrably surviving* in the live market.

```
dali::score_creative(image_url, "beauty")
→ score 62/100  — partial resemblance to proven winners
→ looks_like:      Frøya Organics (ran 411d), tashportcosmetics (884d), Face Reality (346d)
→ what_to_change:  winners use "before/after" 4× more · offer-visible 1.8× more
→ defects:         none
→ Verdict: Partial — strong resemblance, but add the high-lift attributes before spending.
```

---

## Contents

- [The real winning data layer](#the-real-winning-data-layer)
- [Install](#install)
- [Tools](#tools)
- [Supported models](#supported-models)
- [Platform supersets](#platform-supersets)
- [Why model-specific?](#why-model-specific)
- [MCP resources](#mcp-resources)
- [Contributing](#contributing)

---

## Install

**Hosted MCP — connect once, scores every prompt and creative:**

```bash
# Claude Code
claude mcp add --transport http dali https://dali.getlulu.dev/mcp
```

```json
// Cursor / Windsurf — .cursor/mcp.json or windsurf settings
{
  "mcpServers": {
    "dali": { "url": "https://dali.getlulu.dev/mcp" }
  }
}
```

```json
// stdio-only clients — npx wrapper around the hosted server, no Python needed
{
  "mcpServers": {
    "dali": { "command": "npx", "args": ["-y", "dali-mcp"] }
  }
}
```

→ **[Full install guide with all clients](https://dali.getlulu.dev/#install)**

**Self-hosted — local, no auth required:**

```bash
pip install dali-mcp
claude mcp add dali -- python -m dali.server
```

> The self-hosted package exposes the prompt-scoring tools locally. The creative-scoring tools (`score_creative`, `analyze_winning_formula`) and the winning-ad corpus run on the hosted server — connect via the hosted MCP to use them.

---

## Tools

**Score the creative — against real winners**

| Tool | What it does |
|------|-------------|
| `score_creative(image_url, category)` | Score an actual ad **image**. Embedding similarity to proven winners is the headline score; also returns the winners it resembles, which winning attributes it's missing, and generation defects — in one call |
| `score_creative_from_view(category, …)` | **Score an image you're looking at (pasted/attached in the chat) — no URL.** The model reads the creative's attributes and Dali scores them against the winning corpus (verdict + what to change). Use for images shared in-conversation; `score_creative` (URL) adds the embedding headline |
| `analyze_winning_formula(csv, category, email)` | Paste your own ads export (creative URL + CPA/CTR/ROAS) → your winning formula vs your losers, plus how you compare to the industry median |

**Score the prompt — before you generate**

| Tool | What it does |
|------|-------------|
| `score_prompt(prompt, model, category?)` | Grade 0–100 with a per-dimension breakdown and verdict. When the score is weak, the **rewrite brief is returned in the same call**. Reads intent with the conversation LLM (understands negation, any language) |
| `enhance_prompt(prompt, model, category?)` | Returns a structured rewrite brief — YOUR LLM writes the enhanced prompt. With a category, the brief is backed by real winning-ad lift |
| `track_enhancement(original, enhanced, generator)` | Record a before/after pair in the graph brain — trains community patterns |
| `score_variations(prompts, generator)` | Rank a list of prompt variants in one call — highest to lowest |
| `suggest_generator(concept, budget_usd_max)` | Pick the best model for your concept + budget |

**The graph brain & meta**

| Tool | What it does |
|------|-------------|
| `creative_patterns(model)` | Community top patterns for this model from the graph |
| `community_benchmark(prompt, model)` | Compare your prompt against community top scorers |
| `prompt_neighbors(prompt, model)` | Find A/B-grade prompts that share your patterns (score the prompt first, so its patterns are in the graph) |
| `analyze_intent(prompt)` | Parse dimensions: camera, motion, lighting, style, mood, gaps |
| `my_story()` | Your scoring history, model stats, grade distribution |
| `list_generators()` | All supported models with medium and core strength |
| `dali_version()` | Server version + changelog |

---

## Supported models

### Video

| Model | Platforms | Best for | Prompt style |
|-------|-----------|----------|--------------|
| `veo3` | Higgsfield, Google AI Studio (`veo-3.1-generate-preview`), Runway | Cinematic brand films, narrative ads, photorealistic motion | Camera move → Subject → Action → Location → Lighting → Mood |
| `seedance` | Higgsfield, fal.ai (`bytedance/seedance-2.0`) | UGC, social-native content, TikTok/Reels performance ads | Natural language, motion-first, authentic feel |
| `kling` | Higgsfield (`kling3`), Kling.ai (`kling-v3-text-to-video`) | Character animation, product showcases, facial performance | Scene → Characters → Action → Camera → Style; multi-shot labels |
| `runway` | Runway (`gen4_turbo`) | VFX, character performance, cinematic motion | Motion-first — describe what moves, not what exists |
| `wan` | fal.ai (`fal-ai/wan/v2.7/text-to-video`) | 4K, 20-second clips, native audio, open-source workflows | Scene → Motion → Sound → Duration → Mood |
| `minimax` | fal.ai (`fal-ai/minimax/hailuo-02/pro/text-to-video`) | Cinematic storytelling, character animation | Natural language + `[camera movement]` bracket syntax |
| `higgsfield` | Higgsfield (native model) | Physics-driven motion — cloth, hair, fluid, particles | Describe materials in motion, not motion abstractly |

> **Sora 2** (OpenAI): API shutdown September 24, 2026. Do not build new dependencies on it — use Runway or Kling instead.

### Image

| Model | Platforms | Best for | Prompt style |
|-------|-----------|----------|--------------|
| `flux` | BFL API (`flux-pro-v1.1`), fal.ai, Replicate | Photorealism, technical photography, product shots | 30–80 words; camera body + lens specs; front-load subject |
| `midjourney` | Midjourney (v8.1) | Artistic depth, editorial, stylized illustration | Prose + params appended: `--ar 16:9 --s 300 --v 8.1 --style raw` |
| `ideogram` | Ideogram API (`V_4`), fal.ai | Typography, logos, text-in-image, graphic design | Describe text exactly in quotes inside the prompt |
| `firefly` | Adobe Firefly 5 (enterprise) | IP-indemnified commercial assets, 4MP brand content | Natural language + `contentClass` and `style.presets` API params |

> **Imagen 4** (Google): deprecated — use `gemini-3.5-flash` with image output. Dali still scores legacy Imagen prompts via the `imagen` model key but don't build new things on it.

---

## Platform supersets

**Higgsfield** and **Runway** are aggregator platforms — they proxy multiple underlying models under one API. The model you pick matters more than the platform name:

| Platform | Model selector | Underlying model |
|----------|---------------|-----------------|
| Higgsfield | `veo3` | Google Veo 3.1 |
| Higgsfield | `seedance` | ByteDance Seedance 2.0 |
| Higgsfield | `kling3` | Kling 3 |
| Higgsfield | `wan2-7` | Wan 2.7 |
| Higgsfield | `image2video` | Higgsfield native |
| Runway | `veo3` | Google Veo 3.1 |
| Runway | `gen4_turbo` | Runway Gen 4.5 |
| Runway | `seedance` | ByteDance Seedance 2.0 |

Dali scores for the **underlying model's native prompt language**, not the platform wrapper. Pass the model name (`veo3`, `kling`, `seedance`…), not the platform name.

---

## Why model-specific?

Generic prompt optimizers don't know that:
- **Veo 3.1** needs camera movement specified above everything else
- **Kling 3** supports multi-shot scene labels natively in the prompt
- **Flux** responds to camera body and lens names like a photographer (`"Sony A7 IV, 85mm f/1.4"`)
- **Midjourney V8.1** reads prose + parameters, not keyword lists
- **Higgsfield** simulates physics — you describe materials in motion, not motion abstractly
- **Minimax** uses `[Pan left]` bracket syntax for camera moves — plain text camera commands are ignored
- **Ideogram V4** needs text quoted exactly in the prompt for typography accuracy
- **Wan 2.7** generates native audio — include sound descriptions alongside visuals

Dali has a separate scoring rubric and rewrite brief for each model. Your LLM does the creative rewriting — Dali provides the intelligence.

---

## MCP resources

```
creative://guide/veo3       → Veo 3.1 camera language guide
creative://guide/seedance   → Seedance UGC motion guide
creative://guide/kling      → Kling multi-shot + expression guide
creative://guide/runway     → Runway motion-first guide
creative://guide/wan        → Wan 2.7 audio + motion guide
creative://guide/minimax    → Minimax bracket camera guide
creative://guide/higgsfield → Higgsfield physics-motion guide
creative://guide/sora       → Sora 2 guide (API shutdown Sep 24, 2026)
creative://guide/flux       → Flux photography brief guide
creative://guide/midjourney → Midjourney V8.1 + parameters guide
creative://guide/ideogram   → Ideogram V4 typography guide
creative://guide/firefly    → Firefly 5 commercial content guide
creative://guide/imagen     → Imagen 4 guide (deprecated Aug 17, 2026)
creative://models           → All models overview
```

---

## Contributing

Model guides live in `dali/data/guides/{model}.json` on the hosted server. Found practitioner patterns that consistently produce high-grade results? Open an issue with the model, the pattern, and a sample prompt + result. The best contributions come from Reddit, Discord, and YouTube — real practitioners, not official docs.

→ **[Prompt best practices by model](https://github.com/Lulu-The-Narwhal/dali-mcp/blob/main/docs/best-practices.md)** — cheat sheets, do/don't tables, top patterns per model
→ **[Dali creative flow skill](https://github.com/Lulu-The-Narwhal/dali-mcp/blob/main/skills/dali-creative-flow.md)** — install this skill so your LLM follows the score → enhance → generate workflow automatically

---

[MIT License](https://github.com/Lulu-The-Narwhal/dali-mcp/blob/main/LICENSE) · Built by [Lulu](https://getlulu.dev) · [dali.getlulu.dev](https://dali.getlulu.dev)
