# 🔋 Battery-Grade Graphite Cost Dashboard

A self-updating dashboard for comparing battery-grade synthetic graphite production costs across 12 locations (China, USA, EU, India, Japan, S. Korea, Vietnam, Indonesia, Australia, Canada, Mozambique).

**Live data refreshes every 6 hours** via GitHub Actions — no server to maintain, no monthly bills.

---

## 📖 First time here?

👉 **Read [DEPLOYMENT.md](DEPLOYMENT.md)** for click-by-click setup instructions (15 min, no coding required).

After deploying, your dashboard will be live at:
```
https://YOUR-USERNAME.github.io/REPOSITORY-NAME/
```

---

## Built on validated research

| Source | What it provides |
|---|---|
| **Bhuwalka et al. 2025** (Stanford/SLAC) | Process-based cost baseline ($5,415/t China, $12,312/t US, capex ratio 3.88×) |
| **Sharma et al. 2026** (Nature Reviews Materials) | Industry context, market structure |
| **McKinsey & Co. Apr 2026** | Western cost-gap validation (+100% synthetic AAM) |
| **Mordor Intelligence Q1 2026** | Energy intensity (10–15 MWh/t), regional cost shares |
| **Benchmark Mineral Intelligence Dec 2024** | Pet coke prices (CPC $417.80/t DDP China; needle $691.80/t) |
| **BusinessEurope 2025 / IEA 2026** | Industrial electricity by region |

---

## Live data sources (auto-fetched every 6 hours)

| Source | Authentication | What it updates |
|---|---|---|
| ExchangeRate-API | None | EUR, CNY, INR, JPY, KRW, VND, IDR vs USD |
| Elecz | None | EU wholesale electricity spot |
| EIA (US gov) | Free API key (optional) | US industrial electricity monthly |
| Commodities-API | None (demo) | Brent crude → pet coke proxy |

---

## Project structure

```
graphite-dashboard/
├── index.html                          # The dashboard (single-file, runs offline too)
├── data/
│   └── live-data.json                  # ← auto-updated every 6 hours
├── scripts/
│   └── fetch_live_data.py              # Python script, runs in GitHub Actions
├── .github/workflows/
│   ├── update-data.yml                 # Cron job (every 6 hours)
│   └── deploy.yml                      # GitHub Pages deployment
├── DEPLOYMENT.md                       # Step-by-step setup guide
└── README.md                           # This file
```

---

## License & attribution

- Dashboard code: free to use and modify.
- Underlying cost data: cite Bhuwalka et al. 2025 + the sources listed in the validation banner.
- Live-data API providers (ExchangeRate-API, Elecz, EIA, Commodities-API): used under their public/free tiers.
