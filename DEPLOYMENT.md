# 📊 Graphite Cost Dashboard — Deployment Guide

> **For users with no coding experience.** This guide walks you through deploying your dashboard so it auto-updates every 6 hours with fresh market data, available at a public URL 24/7.
>
> **Total time:** ~15 minutes • **Cost:** $0 (forever) • **Accounts needed:** 1 (GitHub, free)

---

## What you'll have when you're done

✅ A live dashboard at a URL like `https://your-username.github.io/graphite-dashboard/`
✅ Auto-refreshing market data every 6 hours (electricity prices, FX rates, oil/petcoke proxy)
✅ Works on any device with a browser — your phone, your boss's laptop, anywhere
✅ A "⬡ Live" badge showing when data was last updated
✅ Falls back gracefully to built-in calibration if any API has an outage

---

## What's in this folder

```
graphite-dashboard-deploy/
├── index.html                          ← the dashboard (open this in a browser to test)
├── data/
│   └── live-data.json                  ← updated automatically every 6 hours
├── scripts/
│   └── fetch_live_data.py              ← the script that pulls fresh data
├── .github/
│   └── workflows/
│       ├── update-data.yml             ← runs every 6 hours to refresh data
│       └── deploy.yml                  ← publishes the dashboard to a public URL
├── DEPLOYMENT.md                       ← this file
└── README.md                           ← short overview
```

---

## Step 1 — Create a free GitHub account (3 min)

1. Go to **https://github.com/signup**
2. Enter an email, password, and pick a username (e.g. `jane-smith`).
   *💡 Tip: your username will appear in your dashboard's URL — pick something professional.*
3. Verify your email.
4. **You're done.** You'll never need anything else from GitHub except this account.

---

## Step 2 — Create a new repository (2 min)

1. After logging in, click the green **"New"** button (top-left, next to "Repositories")
   *Or go directly to https://github.com/new*
2. Fill out the form:
   - **Repository name:** `graphite-dashboard` *(or whatever you want)*
   - **Description:** *Battery-grade graphite cost dashboard with live data*
   - **Visibility:** ⚪ Public *(required for free auto-updates)*
   - **Initialize this repository with:** leave all three checkboxes **unchecked**
3. Click the green **"Create repository"** button at the bottom.

You'll land on a page that says *"Quick setup — if you've done this kind of thing before"*. Ignore everything on that page; we'll do it through the web interface instead.

---

## Step 3 — Upload the files (5 min)

1. On the repository page, look for the link that says **"uploading an existing file"** (or click the **"Add file"** dropdown → **"Upload files"**).

2. Open this folder (`graphite-dashboard-deploy`) on your computer. **Select ALL files and folders inside** — including the hidden `.github` folder.
   - *Windows:* In File Explorer, press `Ctrl+A` to select all.
   - *Mac:* In Finder, press `Cmd+A`. Make sure "Show hidden files" is on (`Cmd+Shift+.`).

3. **Drag and drop** them all onto the GitHub upload page.

4. Wait for all files to upload (you'll see progress bars).

5. Scroll down. In the "Commit changes" box, leave the default message ("Add files via upload") and click the green **"Commit changes"** button.

---

## Step 4 — Enable GitHub Pages to host the dashboard (1 min)

1. On your repository page, click the **"Settings"** tab (top-right of the page).

2. In the left sidebar, click **"Pages"**.

3. Under **"Build and deployment"** → **"Source"**, click the dropdown that says "Deploy from a branch" and change it to **"GitHub Actions"**.

4. *That's it.* No other settings to change.

---

## Step 5 — Trigger the first deployment (1 min)

1. Click the **"Actions"** tab at the top of your repository.

2. You should see two workflows in the left sidebar:
   - **"Fetch live data and update dashboard"**
   - **"Deploy dashboard to GitHub Pages"**

3. Click **"Deploy dashboard to GitHub Pages"** → click the **"Run workflow"** button (right side) → confirm with another **"Run workflow"**.

4. Wait ~1-2 minutes. The workflow will show a green ✓ when done.

5. Now also run **"Fetch live data and update dashboard"** → **"Run workflow"** → **"Run workflow"**. This fetches the first batch of live data.

---

## Step 6 — Visit your live dashboard 🎉

Your URL is:

```
https://YOUR-USERNAME.github.io/graphite-dashboard/
```

(Replace `YOUR-USERNAME` with your actual GitHub username and `graphite-dashboard` with whatever you named your repository.)

Bookmark it. Share it. The dashboard will now refresh its live data every 6 hours forever, with no further action from you.

---

## Optional — Add a free EIA API key for higher-precision US electricity data

The dashboard works fine without this. But if you want exact monthly US industrial electricity prices instead of static fallback values:

1. Go to **https://www.eia.gov/opendata/register.php**, enter your email, and click "Register".
2. Check your email for the key (looks like `aBc123XyZ...`).
3. On your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions** → **"New repository secret"**.
4. **Name:** `EIA_API_KEY`
5. **Value:** *paste your key*
6. Click **"Add secret"**.

The next time the workflow runs (within 6 hours, or trigger it manually), it'll start using live EIA data.

---

## Troubleshooting

### "My dashboard URL shows a 404"
GitHub Pages can take 5-10 minutes to publish after the first deploy. Wait, then refresh. If still 404, check **Actions** tab for failed workflows.

### "The Live badge says 'Offline'"
The dashboard couldn't reach `data/live-data.json`. Causes:
- The "Fetch live data" workflow hasn't run yet — trigger it manually from the Actions tab.
- The repository is set to Private — must be Public for free GitHub Pages.

### "I see green ✓ but data hasn't updated"
Open the workflow run from the Actions tab, click "Run data fetcher", read the log. Common cause: an upstream API is temporarily down. The dashboard falls back to built-in values automatically — no fix needed.

### "I see a Node.js 20 deprecation warning"
This is a benign warning, not an error. GitHub is migrating their Actions runtime from Node 20 to Node 24 (deadline: June 2026). The latest version of this project already:
- Uses `actions/checkout@v5` and `actions/setup-python@v6` (both Node 24 native)
- Sets `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true` to force any remaining Node 20 actions (transitively used by `upload-pages-artifact`) onto Node 24

Your workflow runs normally. The warning will disappear entirely once GitHub ships `actions/upload-pages-artifact@v4` (tracked at [actions/upload-pages-artifact#138](https://github.com/actions/upload-pages-artifact/issues/138)).

### "I want to update the dashboard code"
Edit `index.html` directly on GitHub (click the pencil icon when viewing the file). On commit, the deploy workflow runs automatically and your changes go live in ~2 minutes.

### "I want to test locally first"
1. Download or clone the repo to your computer.
2. Open `index.html` directly in your browser (no server needed for testing).
3. Note: locally, the "Live" badge will say "Offline" because there's no JSON path resolution — that's normal.

---

## What gets updated live, and what doesn't?

| Updates live every 6 hours | Built-in (paper-validated) |
|---|---|
| Industrial electricity prices (EU, US, etc.) | Bhuwalka 2025 cost baselines ($5,415/t China) |
| FX rates (EUR, CNY, INR, JPY, KRW, VND) | Wright's-Law learning rate (15%/doubling) |
| Brent crude → CPC proxy estimate | Capex ratios (3.88× US/China) |
| EU wholesale spot (via Elecz, no key) | Labor cost benchmarks |
| US EIA monthly industrial (if you add the key) | Furnace efficiency parameters |

The dashboard's **structural calibration** (the Bhuwalka 2025 paper baseline, the capex multipliers, the Wright's Law parameters) is locked into the code itself. Live data only refreshes the **market-rate inputs** that fluctuate week-to-week.

---

## Where the live data comes from

| Data | Source | API | Auth required? |
|---|---|---|---|
| FX rates | ExchangeRate-API | `open.er-api.com` | No |
| EU electricity spot | Elecz | `elecz.com/api/v1/current` | No |
| US industrial electricity | EIA (US gov) | `api.eia.gov/v2/electricity` | Free key |
| Brent crude (petcoke proxy) | Commodities-API demo | `commodities-api.com` | No |

All API calls are made **server-side** in GitHub Actions (not from your browser), so there are no CORS issues and no risk of leaking API keys to visitors.

---

## Need help?

The dashboard, the fetcher script, and these workflows are all open files in your repository. You can read them, modify them, or ask anyone (an AI assistant, a developer friend, ChatGPT) for help interpreting them — they're well-commented for non-developers.

Happy modeling! 🔋
