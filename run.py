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
from pathlib import Path

# ---- Defaults (edit to taste) -----------------------------------------------
DEFAULTS = {
    "provider": "anthropic",
    "deep_model": "claude-opus-4-8",          # heavy reasoning: the debate
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
    p.add_argument("ticker", help="Ticker symbol, e.g. NVDA")
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


def run(args: argparse.Namespace, config) -> None:
    from tradingagents.graph.trading_graph import TradingAgentsGraph

    ticker = args.ticker.upper()
    print(f"\n=== TradingAgents: {ticker} @ {args.date} "
          f"({args.provider}/{args.deep}) ===\n")

    ta = TradingAgentsGraph(debug=args.debug, config=config)
    result = ta.propagate(ticker, args.date)

    # propagate() returns either (final_state, decision) or just a decision,
    # depending on version — handle both.
    if isinstance(result, tuple) and len(result) == 2:
        final_state, decision = result
    else:
        final_state, decision = None, result

    print("\n" + "=" * 60)
    print(f"DECISION for {ticker} ({args.date}):\n")
    print(decision)
    print("=" * 60 + "\n")

    RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = RESULTS_DIR / f"{ticker}_{args.date}_{stamp}.json"
    payload = {
        "ticker": ticker,
        "date": args.date,
        "provider": args.provider,
        "deep_model": args.deep,
        "quick_model": args.quick,
        "rounds": args.rounds,
        "decision": str(decision),
    }
    if final_state is not None:
        # final_state may not be JSON-serializable; stringify defensively.
        try:
            payload["final_state"] = json.loads(json.dumps(final_state, default=str))
        except Exception:
            payload["final_state"] = str(final_state)
    out.write_text(json.dumps(payload, indent=2))
    print(f"Saved full result -> {out.relative_to(ROOT)}")


def main() -> None:
    load_dotenv(ROOT / ".env")
    args = parse_args()  # handles --help before we require any keys
    check_env()
    config = build_config(args)
    run(args, config)


if __name__ == "__main__":
    main()
