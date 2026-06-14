# Daily Sports Digest — self-updating web app

A dark, mobile-first page (Bruins · Patriots · Ohio State · NHL · UFC) that a
GitHub Action rebuilds every morning using Claude + web search, served free on
GitHub Pages, and pinned to your phone's home screen as a PWA.

```
index.html              ← the page (regenerated daily; an initial copy is included)
render.py               ← turns digest data into HTML (the design lives here, once)
generate.py             ← research via Claude + web search, then render → index.html
seed.json               ← sample data used to build the initial index.html
manifest.webmanifest    ← makes it installable as an app
sw.js                   ← service worker (offline fallback)
icons/                  ← app icons (192 / 512)
.github/workflows/daily-digest.yml   ← the daily cron job
requirements.txt        ← (none needed — stdlib only)
```

---

## One-time setup (~10 minutes)

### 1. GitHub account + repo
- Sign up at https://github.com (free) if you don't have an account.
- Create a **new public repository** (public = free Pages). Name it e.g. `sports-digest`.
- Push these files to it, e.g.:
  ```bash
  git clone https://github.com/<you>/sports-digest.git
  cd sports-digest
  # copy everything from this kit in here (keep the .github folder)
  git add .
  git commit -m "Initial sports digest"
  git push
  ```

### 2. Anthropic API key
- Get a key at https://console.anthropic.com → **API Keys**, and add billing.
  (Cost is tiny — a handful of web searches + a few thousand tokens per run,
  typically pennies a day. Check current rates at https://www.anthropic.com/pricing.)
- Make sure **web search is enabled** for your org: Console → Settings → look for the
  web search / tool setting and turn it on. (The Action fails clearly if it's off.)

### 3. Store the key as a repo secret
- Repo → **Settings → Secrets and variables → Actions → New repository secret**
- Name: `ANTHROPIC_API_KEY`  ·  Value: your key.

### 4. Let Actions commit to the repo
- Repo → **Settings → Actions → General → Workflow permissions**
- Select **Read and write permissions** → Save.
  (The workflow also declares `permissions: contents: write`, but this repo-level
  toggle must allow it.)

### 5. Turn on GitHub Pages
- Repo → **Settings → Pages**
- **Source:** Deploy from a branch · **Branch:** `main` · **Folder:** `/ (root)` → Save.
- Your URL appears after a minute: `https://<you>.github.io/sports-digest/`

### 6. First run
- Repo → **Actions** tab → **Daily Sports Digest** → **Run workflow**.
- It researches today, rewrites `index.html`, and commits. Pages redeploys in ~1 min.
- Open the Pages URL to confirm it looks right.

### 7. Pin it to your Pixel
- Open the Pages URL in **Chrome** on the Pixel 9 Pro XL.
- Chrome **⋮ menu → Add to Home screen** (it should offer **Install app** since this is a
  proper PWA) → Add.
- You get a real app icon that opens full-screen, no address bar, and works offline
  (shows the last fetched copy).

Done. Every morning around 7:00 the page refreshes itself and your icon shows the new day.

---

## Tuning
- **Time of day:** edit the `cron:` line in `.github/workflows/daily-digest.yml`.
  It's in **UTC**. `0 11 * * *` ≈ 7 AM EDT. (Cron has no DST; in winter it lands an hour
  earlier. Use `0 12 * * *` if you prefer 7 AM year-round-ish in winter.)
- **Model:** defaults to `claude-sonnet-4-6`. For deeper research set a repo variable /
  env `DIGEST_MODEL=claude-opus-4-8` (higher quality, higher cost).
- **Design / sections:** all visual structure is in `render.py`. Change colors, spacing,
  or add a section there and it applies every day. `generate.py` only decides *content*.
- **Run it yourself anytime:** Actions tab → Run workflow. Or locally:
  `ANTHROPIC_API_KEY=sk-... python generate.py`

## How it holds up
- If a run fails (API/network/search off), the job exits non-zero and the **previous**
  `index.html` stays live — you never get a blank page.
- Links are taken from real search results; `generate.py` is told never to invent URLs.
