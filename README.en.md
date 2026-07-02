# Kwork Gig Studio

> All-in-one MCP server for creating and publishing kwork (Russian freelance marketplace) gigs. From idea to publication in 15 minutes.

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![MCP](https://img.shields.io/badge/MCP-compatible-purple.svg)](https://modelcontextprotocol.io)
[![GitHub stars](https://img.shields.io/github/stars/shekelstrong/kwork-gig-studio.svg)](https://github.com/shekelstrong/kwork-gig-studio)

**Russian version:** [README.md](README.md)

---

## 🎯 What is this

Kwork Gig Studio is an MCP server that packages all the experience of working with Kwork into one tool. Instead of keeping moderation rules, character limits, and cover techniques in your head — just call the right tool.

**All steps of creating a kwork in one package:**

- 🔍 **Niche research** — category analysis, trends, competitors
- 📝 **Text generation** — title (≤70 chars), description (≤1200), FAQ
- 🎨 **Cover generation** — via OpenRouter `google/gemini-2.5-flash-image`
- ✅ **Cover validation** — vision checker for trigger words and forbidden brands
- 🛡 **Kwork ToS check** — moderation, prices, brands
- 🚀 **Publishing** — via Playwright (optional)

---

## 📦 Installation

### Requirements

- Python 3.11+
- OpenRouter API key (for covers and text generation)
- Optional: Playwright + Chromium (for auto-publishing)

### Quick start

```bash
git clone https://github.com/shekelstrong/kwork-gig-studio.git
cd kwork-gig-studio
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add OPENROUTER_API_KEY
python -m mcp.server
```

### As MCP server for Claude / Hermes / Cursor

```json
{
  "mcpServers": {
    "kwork-gig-studio": {
      "command": "python",
      "args": ["-m", "mcp.server"],
      "cwd": "/path/to/kwork-gig-studio",
      "env": {
        "OPENROUTER_API_KEY": "sk-or-v1-..."
      }
    }
  }
}
```

---

## 🛠 MCP Tools

### 1. `create_gig_draft`

Generates a gig draft: title + description + FAQ.

**Parameters:**
- `niche` (str) — niche description
- `price` (int) — desired price in rubles
- `deadline_days` (int) — execution time
- `target_audience` (str, optional) — buyer persona

**Returns:** dict with title, description, faq, metadata

### 2. `generate_cover`

Generates a cover via OpenRouter gemini-2.5-flash-image.

**Parameters:**
- `title` (str) — gig title
- `style` (str) — style (default `"dark-saas"`, options: `light`, `gradient`)
- `metrics` (list[str], optional) — metrics to display
- `bullets` (list[str], optional) — 3 bullets for the right panel

**Returns:** path to PNG file (660×440 minimum, generated 1024×1024)

### 3. `validate_cover`

Vision checker for the cover: trigger words, brands, prices, cyrillic ratio.

**Parameters:**
- `image_path` (str) — path to PNG
- `strict_mode` (bool) — strict check (default `true`)

**Returns:** dict with `ok`, `issues`, `score`

### 4. `check_tos`

Checks text against Kwork moderation rules.

**Parameters:**
- `text` (str) — title, description or FAQ
- `check_type` (str) — `"title" | "description" | "faq" | "all"`

**Returns:** list of violations with recommendations

### 5. `publish_gig` (optional)

Auto-publish via Playwright. Requires Kwork session.

⚠️ Use carefully — violation = ban.

---

## 🚀 Usage

```python
from mcp.server import create_gig_draft, generate_cover, validate_cover

draft = create_gig_draft(
    niche="AI audit of requests for e-commerce",
    price=5000,
    deadline_days=1
)
cover = generate_cover(title=draft["title"])
result = validate_cover(cover)
```

Full examples in [`examples/`](examples/).

---

## 🎨 Cover style (default: dark-saas)

- **Background:** `#0a0a0a` → `#161616` (radial vignette)
- **Accents:** mint `#7ee787` + sky `#79c0ff`
- **Font:** Inter / SF Pro Display
- **Layout:** 50/50 — title + metrics left, illustration right
- **Without:** Kwork logo, brands, prices, trigger words

See [`references/cover-style.md`](references/cover-style.md).

---

## 🛡 Kwork rules (strict moderation)

`check_tos` checks all known violations:

| Category | What's forbidden |
|---|---|
| **Brands** | VK, Avito, hh.ru, Ozon, WB, 2GIS, Yandex, T-Bank, QIWI |
| **Personal data** | Names, phones, emails (legal entities OK) |
| **Prices** | Numbers with ₽/$/€ in title/description |
| **Trigger words** | "рилс/Reels", "сторис/Stories", "паблик", "SMM" |
| **Cyrillic** | < 70% cyrillic in cover |
| **Sizes** | Title > 70, description > 1200, "buyer needs" > 500 |

Exceptions: in "Information bases", "Parsing", "SMM" niches VK brand is allowed.

Full list: [`references/kwork-rules.md`](references/kwork-rules.md).

---

## 📄 License

MIT © Vasiliy Nedopekin (shekelstrong)

---

## 🙏 Acknowledgments

- **nousresearch** for [Hermes Agent](https://github.com/nousresearch/hermes-agent)
- **OpenRouter** for unified LLM API
- **6 published kworks** at the time of repo creation — moderation rules are trained on them
