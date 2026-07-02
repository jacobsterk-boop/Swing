# Environment & Tooling Learnings

_Last updated: 2026-07-02_

## What works
- **Robinhood MCP** — quotes, fundamentals, historicals (OHLCV), earnings,
  positions, orders (equity + single-leg options). This is my data + execution.
- **Direct-data screening** — I can pull `get_equity_quotes` (movers) +
  `get_equity_historicals` (trend/RSI/levels) on any universe and rank myself.
  This is the reliable screening path.
- **TradingView (via the user)** — the user runs screeners/charts in TradingView
  and pastes CSV/readings back. This is our **whole-market scanner** and our
  intraday chart read. Best combo we have.

## What's broken / limited
- **Robinhood scanner (Legend/Beacon) returns 0 for everything** — even a broad
  `stock + close $5–60` screen returns 0 during market hours. Data-feed/entitlement
  issue on RH's side, not our filters. **Don't rely on `run_scan`; use direct data
  or TradingView instead.**
- **No native TradingView connection** — the user is the bridge (paste outputs).
- **Options via MCP:** single-leg Level 2 only. No multi-leg spreads.
- Scanner filter gotcha (if we ever use it): `FILTER_TYPE_CLOSE` needs
  `length: 1`, or it errors with `candleCount=0`.

## TradingView screener recipe (whole-market relative strength)
> US common stocks · Price $5–$60 · Avg vol (30D) > 1M · Change% today > +2% ·
> Price above 50-day SMA · RSI(14) 45–68
> Columns: Ticker, Price, Change %, Rel Volume, RSI, 50-SMA, Sector

Ranking after import: favor **RelVol > 1** (conviction) + RSI < 70 (room) +
liquid/recognizable names over micro-cap lottery tickets.

## TradingAgents (deep-dive engine, the user's machine)
- Repo: `~/Desktop/swing` (public GitHub `jacobsterk-boop/swing`, branch
  `claude/stock-portfolio-review-9wlo9k`). Engine cloned separately at
  `~/Desktop/TradingAgents`; venv at `~/Desktop/TradingAgents/.venv` (Python 3.14).
- Run: `python run.py TICKER` (single) or `--universe universe.txt` (batch).
- **Default deep model = `claude-sonnet-5`** (cost). Opus via `--deep claude-opus-4-8`.
- **Cost:** one MU run = **$0.47** (Sonnet). Check spend at platform.claude.com/dashboard.
- SSL certs were installed on the Mac (fixed the `CERTIFICATE_VERIFY_FAILED`
  errors); Reddit/StockTwits sentiment sources now work.
- Output labels use "Overweight/Underweight" (not just Buy/Hold/Sell) — the
  runner's signal extractor tags those as "?" (cosmetic).

## The funnel
Scan (free: TradingView / direct data) → shortlist (my reasoning) → optional
TradingAgents deep-dive (~$0.50, finalists only) → propose (size + stop) →
approve → execute → log here.
