#!/usr/bin/env python3
"""
screen.py — relative-strength momentum screener over the swing universe.

Ranks the tickers in universe.txt by today's move using the Finnhub API, so you
get a candidate shortlist in one command — no TradingView, no live agent needed.
Cron-friendly.

    python screen.py                    # screen universe.txt by % change
    python screen.py --min-change 2     # only names up >= 2% today
    python screen.py --rsi              # also compute RSI(14) on the shortlist
    python screen.py --file mylist.txt  # screen a different list

Reads FINNHUB_API_KEY from .env (the same key TradingAgents uses).

Free-tier note: real-time /quote works on the free plan. RSI needs daily candles
(/stock/candle), which some Finnhub plans gate — with --rsi the script computes
RSI when candles are available and shows "n/a" (ranking on % change) otherwise.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
API = "https://finnhub.io/api/v1"
THROTTLE = 1.1  # seconds between calls — stay under the free 60/min limit


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def get_json(url: str):
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode())


def quote(sym: str, key: str) -> dict:
    try:
        return get_json(f"{API}/quote?symbol={urllib.parse.quote(sym)}&token={key}")
    except Exception as e:  # network / rate-limit / bad symbol
        return {"error": str(e)}


def daily_closes(sym: str, key: str, days: int = 120):
    end = int(time.time())
    start = end - days * 86400
    try:
        d = get_json(
            f"{API}/stock/candle?symbol={urllib.parse.quote(sym)}"
            f"&resolution=D&from={start}&to={end}&token={key}"
        )
        if d.get("s") == "ok" and d.get("c"):
            return d["c"]
    except Exception:
        pass
    return None


def rsi(closes, period: int = 14):
    """Wilder's RSI. Returns None if not enough data."""
    if not closes or len(closes) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        ch = closes[i] - closes[i - 1]
        gains.append(max(ch, 0.0))
        losses.append(max(-ch, 0.0))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - 100 / (1 + rs), 1)


def read_universe(path: str):
    p = Path(path)
    if not p.exists():
        sys.exit(f"Universe file not found: {path}")
    out = []
    for raw in p.read_text().splitlines():
        s = raw.split("#", 1)[0].strip()
        if s:
            out.append(s.upper())
    if not out:
        sys.exit(f"No tickers in {path}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Relative-strength screener over a ticker list.")
    ap.add_argument("--file", default=str(ROOT / "universe.txt"))
    ap.add_argument("--min-change", type=float, default=None,
                    help="Only keep names with today's %% change >= this")
    ap.add_argument("--rsi", action="store_true",
                    help="Also fetch RSI(14) on the shortlist (extra calls; needs candle access)")
    args = ap.parse_args()

    load_dotenv(ROOT / ".env")
    key = os.environ.get("FINNHUB_API_KEY")
    if not key:
        sys.exit("Missing FINNHUB_API_KEY — set it in .env (see .env.example).")

    tickers = read_universe(args.file)
    print(f"Screening {len(tickers)} names from {Path(args.file).name} …")

    rows = []
    for sym in tickers:
        q = quote(sym, key)
        if "error" in q or not q.get("c"):
            print(f"  ! {sym}: no quote ({q.get('error', 'empty')})")
            time.sleep(THROTTLE)
            continue
        rows.append({"sym": sym, "price": q.get("c"), "chg": q.get("dp"),
                     "hi": q.get("h"), "lo": q.get("l"), "rsi": None})
        time.sleep(THROTTLE)

    if args.min_change is not None:
        rows = [r for r in rows if r["chg"] is not None and r["chg"] >= args.min_change]
    rows.sort(key=lambda r: (r["chg"] is None, -(r["chg"] or 0)))

    if args.rsi:
        for r in rows:
            closes = daily_closes(r["sym"], key)
            r["rsi"] = rsi(closes) if closes else None
            time.sleep(THROTTLE)

    print(f"\n{'Sym':<6}{'Price':>10}{'Chg%':>9}{'RSI':>7}")
    print("-" * 32)
    for r in rows:
        chg_s = f"{r['chg']:+.2f}" if r["chg"] is not None else "n/a"
        rsi_s = f"{r['rsi']:.1f}" if r["rsi"] is not None else "n/a"
        print(f"{r['sym']:<6}{r['price']:>10.2f}{chg_s:>9}{rsi_s:>7}")

    RESULTS.mkdir(exist_ok=True)
    stamp = dt.date.today().isoformat()
    out = RESULTS / f"screen_{stamp}.csv"
    lines = ["symbol,price,change_pct,rsi14,day_high,day_low"]
    for r in rows:
        lines.append(f"{r['sym']},{r['price']},{r['chg']},"
                     f"{r['rsi'] if r['rsi'] is not None else ''},{r['hi']},{r['lo']}")
    out.write_text("\n".join(lines))
    print(f"\nSaved -> {out.relative_to(ROOT)}  ({len(rows)} names)")


if __name__ == "__main__":
    main()
