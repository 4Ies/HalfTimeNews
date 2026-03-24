# ◈ NewsAgg

A personal, AI-powered news aggregator for Ubuntu/Linux.  
Fetches RSS feeds, clusters same-story articles from multiple sources, ranks them by your interests, and supplements with DuckDuckGo — all with a clean dark UI and no cloud APIs required.

---

## Features

| Feature | How it works |
|---|---|
| **Multi-source RSS** | Fetches from any RSS/Atom feed you enable |
| **Story clustering** | Groups articles covering the same event using local sentence embeddings (`all-MiniLM-L6-v2`, ~80 MB, downloaded once) |
| **Interest ranking** | Scores articles by cosine similarity to your interest phrases |
| **DuckDuckGo supplement** | Derives search queries from top RSS keywords and pulls fresh web results |
| **Live filter** | Sidebar lets you filter by category or source instantly |
| **Auto-refresh** | Background thread refreshes on a configurable schedule |
| **Fully offline ML** | No OpenAI, no Anthropic, no API keys — embeddings run locally |

---

## Project Structure

```
newsagg/
├── main.py                  # Entry point
├── requirements.txt         # pip dependencies
├── build_deb.sh             # Builds the .deb package
├── newsagg                  # CLI launcher (installed to /usr/local/bin)
│
├── core/
│   ├── models.py            # Article, StoryCluster dataclasses
│   ├── config.py            # Load/save ~/.config/newsagg/config.json
│   ├── fetcher.py           # RSS fetching (feedparser) + DDG search
│   ├── clusterer.py         # Sentence embeddings + DBSCAN clustering
│   ├── ranker.py            # Interest-based relevance scoring
│   └── scheduler.py        # QThread background refresh scheduler
│
├── ui/
│   ├── main_window.py       # QMainWindow: header + sidebar + feed
│   ├── story_feed.py        # Scrollable QScrollArea of cards
│   ├── story_card.py        # Per-cluster card widget
│   ├── sidebar.py           # Category/source filter panel
│   ├── settings_dialog.py   # Tabbed settings: sources, interests, behaviour
│   └── style.py             # Global Qt stylesheet (dark editorial theme)
│
├── data/
│   └── sources.json         # Bundled default sources (copied to ~/.config on first run)
│
├── assets/
│   └── newsagg.desktop      # .desktop launcher for GNOME app grid
│
├── debian/
│   ├── control              # Package metadata
│   ├── postinst             # Post-install: creates venv + pip install
│   ├── prerm                # Pre-remove: deletes venv
│   └── copyright
│
└── tests/
    └── test_clusterer.py    # pytest unit tests (no GPU/model needed)
```

---

## Quick Start (development)

### 1. Prerequisites

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

### 2. Clone and create a virtual environment

```bash
git clone https://github.com/yourname/newsagg.git
cd newsagg
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `sentence-transformers` will download the `all-MiniLM-L6-v2` model (~80 MB)
> the first time you run the app. It caches to `~/.cache/huggingface/`.

### 4. Run

```bash
python main.py
```

---

## Building the .deb package

```bash
sudo apt install dpkg-dev
chmod +x build_deb.sh
./build_deb.sh
```

This produces `dist/newsagg_0.1.0_all.deb`.

### Install

```bash
sudo dpkg -i dist/newsagg_0.1.0_all.deb
```

The postinst script will create `/opt/newsagg/venv/` and pip-install all dependencies automatically.

### Uninstall

```bash
sudo apt remove newsagg
```

---

## Configuration

On first launch, NewsAgg copies `data/sources.json` to `~/.config/newsagg/config.json`.  
You can edit this file directly, or use the **Settings** panel in the app.

### Adding a custom RSS source

Either:
- Open **Settings → Sources → Add custom RSS feed**
- Or add an entry to `~/.config/newsagg/config.json` under `"sources"`

### Setting your interests

Open **Settings → Interests** and add one topic per line:

```
artificial intelligence
Milan
Formula 1
climate change
geopolitics
```

These are used to score and sort every article by relevance.

---

## How the AI pipeline works

```
RSS feeds + DDG
      │
      ▼
  fetch_all_rss()          ← feedparser, one thread per source
      │
      ▼
  rank_articles()          ← keyword pass (fast, before embeddings)
      │
      ▼
  embed_articles()         ← sentence-transformers all-MiniLM-L6-v2
      │
      ▼
  rank_articles()          ← cosine similarity to interest phrases
      │
      ▼
  cluster_articles()       ← DBSCAN on embedding matrix
      │
      ▼
  List[StoryCluster]       ← sorted: multi-source first, then score
      │
      ▼
  StoryFeed (UI)
```

### Clustering threshold

- **0.90+** Very strict: only nearly-identical headlines cluster together
- **0.75** (default) Balanced: same event from different sources clusters well
- **0.60** Loose: thematically similar articles cluster together

Tune in **Settings → Behaviour**.

---

## Extending with a local LLM (optional)

Install [Ollama](https://ollama.com/) and pull a small model:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral
```

Then in `core/summarizer.py` (not yet implemented — a good next step!):

```python
import requests

def summarize(articles: list[Article]) -> str:
    titles = "\n".join(f"- {a.title}" for a in articles)
    resp = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": f"Summarize these news headlines in one neutral sentence:\n{titles}",
        "stream": False,
    })
    return resp.json()["response"].strip()
```

---

## Running tests

```bash
pip install pytest
python -m pytest tests/ -v
```

No GPU or internet needed for the tests — embeddings are faked with numpy.

---

## Roadmap

- [ ] Per-story LLM summary (via Ollama)
- [ ] Read/unread state with local SQLite persistence
- [ ] Full-text article reader pane (right-click → Open in reader)
- [ ] Import/export OPML for source lists
- [ ] Notification on high-relevance breaking stories
- [ ] AppImage build for non-Debian distros

---

## License

MIT — see `debian/copyright`.
