#!/usr/bin/env python3
"""
run.py — one-command runner for TradingAgents (Tauric Research).

Wraps TradingAgentsGraph so a full multi-agent analysis is a single command:

    python run.py NVDA
    python run.py NVDA --date 2026-06-30
    python run.py AAPL --deep claude-opus-4-8 --quick claude-haiku-4-5-20251001
    python run.py TSLA --rounds 2 --debug

It loads API keys from a .env file (or the environment), builds the config,
runs the analyst / researcher / trader debate, prints the final BUY/SELL/HOLD
decision, and saves the full result under ./results/.

NOTE: This wraps TradingAgents' *documented* interface. If your installed
version uses different config field names, adjust CONFIG_KEYS below — the
script prints a pointer to the exact spot if an import or key fails.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import traceback
from pathlib import Path

# ---- Defaults (edit to taste) -----------------------------------------------
DEFAULTS = {
    "provider": "anthropic",
    "deep_model": "claude-sonnet-5",          # heavy reasoning: the debate (cost-friendly)
    "quick_model": "claude-haiku-4-5-20251001",  # cheap/fast: the analysts
    "rounds": 1,                               # keep low to control cost
}

# Map our CLI concepts -> TradingAgents config keys. If your version differs,
# this dict is the ONLY place you need to edit.
CONFIG_KEYS = {
    "provider": "llm_provider",
    "deep_model": "deep_think_llm",
    "quick_model": "quick_think_llm",
    "rounds": "max_debate_rounds",
    "online_tools": "online_tools",
}

REQUIRED_ENV = ["ANTHROPIC_API_KEY", "FINNHUB_API_KEY"]
ROOT = Path(__file__).parent
RESULTS_DIR = ROOT / "results"


def load_dotenv(path: Path) -> None:
    """Minimal .env loader so we don't hard-depend on python-dotenv."""
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        val = val.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), val)


def check_env() -> None:
    missing = [k for k in REQUIRED_ENV if not os.environ.get(k)]
    if missing:
        sys.exit(
            "Missing required environment variables: "
            + ", ".join(missing)
            + "\nSet them in a .env file (see .env.example) or export them.\n"
            "Tip: some TradingAgents versions also need OPENAI_API_KEY for the "
            "embeddings/memory layer even when the agents run on Claude."
        )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run a TradingAgents multi-agent analysis on one ticker.",
    )
    p.add_argument("ticker", nargs="?", help="Ticker symbol, e.g. NVDA")
    p.add_argument(
        "--universe",
        metavar="FILE",
        help="Analyze every ticker in FILE (one per line; # comments ok), "
        "e.g. --universe universe.txt. Overrides a positional ticker.",
    )
    p.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="Analysis date YYYY-MM-DD (default: today)",
    )
    p.add_argument("--provider", default=DEFAULTS["provider"])
    p.add_argument("--deep", default=DEFAULTS["deep_model"], help="Deep-think model")
    p.add_argument("--quick", default=DEFAULTS["quick_model"], help="Quick-think model")
    p.add_argument("--rounds", type=int, default=DEFAULTS["rounds"], help="Max debate rounds")
    p.add_argument("--offline", action="store_true", help="Disable online tools")
    p.add_argument("--debug", action="store_true", help="Stream agent chatter")
    return p.parse_args()


def build_config(args: argparse.Namespace):
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
    except ImportError as e:
        sys.exit(
            f"Could not import TradingAgents ({e}).\n"
            "Install it first (in your terminal, from the TradingAgents repo):\n"
            "    pip install -e .\n"
            "and run this script from an environment where it's importable."
        )

    config = dict(DEFAULT_CONFIG)
    config[CONFIG_KEYS["provider"]] = args.provider
    config[CONFIG_KEYS["deep_model"]] = args.deep
    config[CONFIG_KEYS["quick_model"]] = args.quick
    config[CONFIG_KEYS["rounds"]] = args.rounds
    config[CONFIG_KEYS["online_tools"]] = not args.offline
    return config


def read_universe(path: str) -> list[str]:
    p = Path(path)
    if not p.exists():
        sys.exit(f"Universe file not found: {path}")
    tickers = []
    for raw in p.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            tickers.append(line.upper())
    if not tickers:
        sys.exit(f"No tickers found in {path}")
    return tickers


def extract_signal(decision: object) -> str:
    """Best-effort BUY/SELL/HOLD extraction for ranking. Scans from the end,
    since the final call usually lands last."""
    text = str(decision).upper()
    hits = [t for t in ("BUY", "SELL", "HOLD") if t in text]
    if not hits:
        return "?"
    # pick whichever appears last in the text
    return max(hits, key=lambda t: text.rfind(t))


def analyze_one(ta, ticker: str, date: str) -> tuple[str, object]:
    result = ta.propagate(ticker, date)
    # propagate() returns either (final_state, decision) or just a decision,
    # depending on version — handle both.
    if isinstance(result, tuple) and len(result) == 2:
        final_state, decision = result
    else:
        final_state, decision = None, result
    return decision, final_state


def save_result(args, ticker: str, decision, final_state, stamp: str) -> Path:
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"{ticker}_{args.date}_{stamp}.json"
    payload = {
        "ticker": ticker,
        "date": args.date,
        "provider": args.provider,
        "deep_model": args.deep,
        "quick_model": args.quick,
        "rounds": args.rounds,
        "signal": extract_signal(decision),
        "decision": str(decision),
    }
    if final_state is not None:
        # final_state may not be JSON-serializable; stringify defensively.
        try:
            payload["final_state"] = json.loads(json.dumps(final_state, default=str))
        except Exception:
            payload["final_state"] = str(final_state)
    out.write_text(json.dumps(payload, indent=2))
    return out


def run(args: argparse.Namespace, config) -> None:
    from tradingagents.graph.trading_graph import TradingAgentsGraph

    if args.universe:
        tickers = read_universe(args.universe)
    else:
        tickers = [args.ticker.upper()]

    ta = TradingAgentsGraph(debug=args.debug, config=config)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    summary: list[dict] = []

    for i, ticker in enumerate(tickers, 1):
        print(f"\n=== [{i}/{len(tickers)}] TradingAgents: {ticker} @ {args.date} "
              f"({args.provider}/{args.deep}) ===\n")
        try:
            decision, final_state = analyze_one(ta, ticker, args.date)
        except Exception as e:  # one bad ticker shouldn't kill a batch
            print(f"!! {ticker} failed: {type(e).__name__}: {e}")
            traceback.print_exc()  # full detail for diagnosis
            summary.append({"ticker": ticker, "signal": "ERR", "error": str(e)})
            continue

        signal = extract_signal(decision)
        out = save_result(args, ticker, decision, final_state, stamp)
        summary.append({"ticker": ticker, "signal": signal, "file": out.name})

        if len(tickers) == 1:
            print("\n" + "=" * 60)
            print(f"DECISION for {ticker} ({args.date}):\n")
            print(decision)
            print("=" * 60)
        else:
            print(f"  -> {signal}   (saved {out.name})")

    if len(tickers) > 1:
        print_batch_summary(args, summary, stamp)


def print_batch_summary(args, summary: list[dict], stamp: str) -> None:
    order = {"BUY": 0, "HOLD": 1, "SELL": 2, "?": 3, "ERR": 4}
    ranked = sorted(summary, key=lambda r: order.get(r["signal"], 5))
    print("\n" + "=" * 60)
    print(f"BATCH SUMMARY — {len(summary)} names @ {args.date}")
    print("=" * 60)
    for r in ranked:
        print(f"  {r['signal']:>4}  {r['ticker']}")
    counts = {}
    for r in summary:
        counts[r["signal"]] = counts.get(r["signal"], 0) + 1
    print("-" * 60)
    print("  " + "  ".join(f"{k}:{v}" for k, v in sorted(counts.items())))

    RESULTS_DIR.mkdir(exist_ok=True)
    combined = RESULTS_DIR / f"_batch_{args.date}_{stamp}.json"
    combined.write_text(json.dumps(
        {"date": args.date, "results": ranked}, indent=2))
    print(f"\nSaved batch summary -> {combined.relative_to(ROOT)}")


def main() -> None:
    load_dotenv(ROOT / ".env")
    args = parse_args()  # handles --help before we require any keys
    if not args.universe and not args.ticker:
        sys.exit("Provide a ticker (e.g. `run.py NVDA`) or --universe FILE.")
    check_env()
    config = build_config(args)
    run(args, config)


if __name__ == "__main__":
    main()
