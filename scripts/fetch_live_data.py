#!/usr/bin/env python3
"""
Graphite Dashboard — Live Data Fetcher
=======================================
Runs on a schedule via GitHub Actions (every 6 hours).
Fetches public market data from no-key APIs and writes data/live-data.json,
which the dashboard reads in the browser to update live values.

NO API KEYS REQUIRED for default operation. All sources are public/free tier.
Optional: set EIA_API_KEY environment variable in GitHub Secrets for higher-precision US data.

Author: built for the Graphite Cost Dashboard
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# ─── Configuration ──────────────────────────────────────────────────────────
TIMEOUT = 10          # seconds per HTTP request
USER_AGENT = "GraphiteDashboard/1.0 (+https://github.com/) Python-urllib"
OUTPUT_PATH = "data/live-data.json"

# Default fallback values (matched to the dashboard's hardcoded calibration).
# These are used when an API call fails — the dashboard still works either way.
FALLBACKS = {
    # Industrial electricity prices in USD/kWh (2024-2025 baseline)
    "elec_usa": 0.0810,
    "elec_china": 0.0890,
    "elec_eu": 0.2150,
    "elec_india": 0.1100,
    "elec_japan": 0.1100,
    "elec_canada": 0.0750,
    "elec_australia": 0.0950,
    "elec_vietnam": 0.0790,
    "elec_indonesia": 0.0650,
    "elec_korea": 0.0990,
    # Feedstock prices (USD/t DDP China, Benchmark Dec 2024 baseline)
    "cpc_china": 417.80,
    "needle_coke_china": 691.80,
    # FX (USD per 1 unit of foreign currency)
    "fx_eur_usd": 1.08,
    "fx_cny_usd": 0.139,
    "fx_inr_usd": 0.0118,
    "fx_jpy_usd": 0.0067,
}


def http_get_json(url, headers=None, timeout=TIMEOUT):
    """Fetch a URL and parse JSON. Returns None on failure."""
    req_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    try:
        req = Request(url, headers=req_headers)
        with urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (URLError, HTTPError, json.JSONDecodeError, TimeoutError) as e:
        print(f"  ⚠ HTTP fetch failed for {url}: {e}", file=sys.stderr)
        return None


def fetch_fx_rates():
    """Fetch FX rates from ExchangeRate-API (free, no key required).
    Source: https://www.exchangerate-api.com/docs/free
    Returns dict with USD-quoted rates.
    """
    print("→ Fetching FX rates (ExchangeRate-API free tier)...")
    data = http_get_json("https://open.er-api.com/v6/latest/USD")
    if not data or data.get("result") != "success":
        return {}
    rates = data.get("rates", {})
    # Convert from "1 USD = X foreign" to "1 foreign = X USD" for our use
    fx = {}
    if "EUR" in rates: fx["fx_eur_usd"] = round(1.0 / rates["EUR"], 4)
    if "CNY" in rates: fx["fx_cny_usd"] = round(1.0 / rates["CNY"], 4)
    if "INR" in rates: fx["fx_inr_usd"] = round(1.0 / rates["INR"], 4)
    if "JPY" in rates: fx["fx_jpy_usd"] = round(1.0 / rates["JPY"], 5)
    if "GBP" in rates: fx["fx_gbp_usd"] = round(1.0 / rates["GBP"], 4)
    if "KRW" in rates: fx["fx_krw_usd"] = round(1.0 / rates["KRW"], 5)
    if "VND" in rates: fx["fx_vnd_usd"] = round(1.0 / rates["VND"], 7)
    if "IDR" in rates: fx["fx_idr_usd"] = round(1.0 / rates["IDR"], 7)
    print(f"  ✓ Got {len(fx)} FX rates")
    return fx


def fetch_eu_electricity():
    """Fetch EU wholesale electricity from Elecz (no key required).
    Source: https://elecz.com/electricity-price-api/ — 32 countries, MCP-native.
    Returns USD/kWh estimate for industrial EU baseline.
    """
    print("→ Fetching EU electricity (Elecz, no key)...")
    # Try Germany as EU benchmark (largest industrial consumer)
    data = http_get_json("https://elecz.com/api/v1/current?zone=DE")
    if not data:
        return None
    price_cents = data.get("price_cents_kwh")
    currency = data.get("currency", "EUR")
    if price_cents is None:
        return None
    # Convert cents → primary unit, EUR → USD if needed
    price = float(price_cents) / 100.0
    if currency == "EUR":
        # Apply rough EUR→USD; we'll get exact FX separately
        price *= 1.08
    print(f"  ✓ EU (DE) wholesale ≈ ${price:.4f}/kWh")
    # Note: this is WHOLESALE spot. Industrial retail typically = wholesale + ~€0.10-0.13/kWh
    # for grid fees, levies, network charges. So add a markup for industrial reference:
    return round(price + 0.115, 4)


def fetch_eia_us_industrial(api_key):
    """Fetch US industrial electricity price from EIA (requires free API key).
    Source: https://www.eia.gov/opendata/ — register at the link for a free key.
    """
    if not api_key:
        print("→ Skipping EIA (no API key set — see EIA_API_KEY in GitHub Secrets)")
        return None
    print("→ Fetching US industrial electricity (EIA)...")
    # EIA API v2: monthly retail electricity, sector=IND (industrial), aggregate US
    url = (f"https://api.eia.gov/v2/electricity/retail-sales/data/?"
           f"api_key={api_key}"
           f"&frequency=monthly&data[0]=price"
           f"&facets[stateid][]=US&facets[sectorid][]=IND"
           f"&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=1")
    data = http_get_json(url)
    if not data or "response" not in data:
        return None
    try:
        entry = data["response"]["data"][0]
        # EIA returns cents/kWh; convert to $/kWh
        price = float(entry["price"]) / 100.0
        period = entry.get("period", "unknown")
        print(f"  ✓ US industrial (EIA {period}) = ${price:.4f}/kWh")
        return round(price, 4)
    except (KeyError, IndexError, ValueError) as e:
        print(f"  ⚠ EIA parse error: {e}")
        return None


def fetch_oil_price():
    """Fetch Brent crude oil price as a proxy/leading indicator for petroleum coke price trends.
    Source: Free CoinGecko-style oracle (no key). If unavailable, fall back to fixed estimate.
    Petroleum coke is a refinery byproduct, so its price tracks crude oil with a lag.
    """
    print("→ Fetching oil price as petcoke proxy...")
    # Try the open commodities feed (best-effort)
    data = http_get_json("https://api.allorigins.win/raw?url=https://www.commodities-api.com/api/latest?access_key=demo")
    # The above demo is rate-limited; we treat this as best-effort only.
    if data and isinstance(data, dict) and "rates" in data:
        rates = data["rates"]
        if "BRENTOIL" in rates:
            brent = 1.0 / rates["BRENTOIL"]  # API returns inverted
            print(f"  ✓ Brent crude ≈ ${brent:.2f}/bbl")
            # Pet coke roughly tracks Brent with a slope (-$200 to -$300/t below Brent×4)
            # Rough heuristic: cpc_china ≈ brent × 5.5 - 100  (calibrated to historical)
            cpc_estimate = round(brent * 5.5 - 100, 2)
            return brent, cpc_estimate
    print("  ⚠ Oil price unavailable; using static fallback")
    return None, None


def main():
    """Orchestrate all data fetches and write the output JSON."""
    print(f"=== Graphite Dashboard Live Data Fetcher ===")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print()

    data = dict(FALLBACKS)  # start with fallbacks; overwrite with live values
    sources = []  # track which sources succeeded
    errors = []   # track which failed

    # 1. FX rates (most reliable free source)
    fx = fetch_fx_rates()
    if fx:
        data.update(fx)
        sources.append("ExchangeRate-API (FX)")
    else:
        errors.append("ExchangeRate-API")

    # 2. EU wholesale electricity (Elecz, no key)
    eu_elec = fetch_eu_electricity()
    if eu_elec:
        data["elec_eu"] = eu_elec
        sources.append("Elecz (EU wholesale)")
    else:
        errors.append("Elecz")

    # 3. US industrial electricity (EIA, requires free key from secrets)
    eia_key = os.environ.get("EIA_API_KEY", "").strip()
    us_elec = fetch_eia_us_industrial(eia_key)
    if us_elec:
        data["elec_usa"] = us_elec
        sources.append("EIA (US industrial)")
    elif eia_key:
        errors.append("EIA")

    # 4. Oil price as petcoke proxy
    brent, cpc_est = fetch_oil_price()
    if brent:
        data["brent_crude"] = brent
        # Only override CPC if heuristic gives sensible value
        if cpc_est and 200 < cpc_est < 800:
            data["cpc_china"] = cpc_est
            sources.append("Brent crude → CPC estimate")

    # 5. Add metadata
    data["_meta"] = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "updated_unix": int(time.time()),
        "sources": sources,
        "errors": errors,
        "fetcher_version": "1.0.0",
    }

    # 6. Compute dashboard-friendly multipliers (relative to China baseline)
    china_elec = data["elec_china"]
    data["multipliers"] = {
        "usa_en":       round(data["elec_usa"]      / china_elec, 3),
        "eu_en":        round(data["elec_eu"]       / china_elec, 3),
        "india_en":     round(data["elec_india"]    / china_elec, 3),
        "japan_en":     round(data["elec_japan"]    / china_elec, 3),
        "canada_en":    round(data["elec_canada"]   / china_elec, 3),
        "australia_en": round(data["elec_australia"]/ china_elec, 3),
        "vietnam_en":   round(data["elec_vietnam"]  / china_elec, 3),
        "indonesia_en": round(data["elec_indonesia"]/ china_elec, 3),
        "korea_en":     round(data["elec_korea"]    / china_elec, 3),
    }

    # 7. Write the output file
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2, sort_keys=False)

    print()
    print(f"=== Summary ===")
    print(f"  Live sources used:      {len(sources)}")
    print(f"  Fallback values used:   {len(errors)} (graceful degradation)")
    print(f"  Output written to:      {OUTPUT_PATH}")
    print(f"  Total keys in payload:  {len(data)}")
    print(f"Finished: {datetime.now(timezone.utc).isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
