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
- **NO resting stops on fractional shares.** (2026-07-06) A stop order on any
  fractional quantity is rejected outright: `gtc` → "Invalid time in force for
  fractional order"; `gfd` → "Invalid trigger for fractional order." Fractional
  orders must be `market` + `regular_hours` + `gfd`, which excludes every stop
  type. **Implication for a small account:** high-priced names (SMH ~$615,
  TSM ~$455, ANET ~$171) can only be bought fractionally here, so they CANNOT
  carry a broker-native stop. Their stops are **managed levels** — enforced by
  the agent at each check-in (and by Jacob) with a market sell if breached.
  - To get a *real* resting broker stop, size a WHOLE-share position: pick names
    cheap enough that a whole-share lot fits the ~20% cap (e.g. a ~$20–40 stock,
    5–15 shares ≈ $200–300). Trade-off: managed-stop torque names vs.
    hard-stop protection on cheaper names.
- Scanner filter gotcha (if we ever use it): `FILTER_TYPE_CLOSE` needs
  `length: 1`, or it errors with `candleCount=0`.

## Scheduled runs — connector NOT available to background sessions
- (2026-07-06) The cron triggers fire on time, but the fresh background session
  they spawn loads only the default coding + web tools — **the Robinhood MCP
  connector is not attached**, so any trade/quote attempt fails ("can't connect
  to Robinhood MCP"). The per-tool Allow/Ask/Block toggles in claude.ai
  Connectors govern the connector *inside interactive chats*, NOT background
  automations — a separate, deeper layer that isn't wired up.
- **Chosen model = "ping to run" (reliable).** The three schedules were switched
  from "trade autonomously" to **push reminders**: at 9:35 / 11:30 / 2:00 ET
  they send Jacob a phone push to open the app and reply "run the routine",
  which then executes in a live (connector-enabled) session. Trigger IDs:
  open `trig_0188ACudCBHyQb1bcwLBGS71`, mid-day `trig_01RzMUH3kxUwoye34K2nSGRk`,
  afternoon `trig_01AMfGDEnAEkSg3GpPBUjF16` (all fresh-session, push:true, M–F).
- True unattended trading would need the connector wired into the background
  environment AND would still be fragile — Robinhood logins expire / need MFA
  re-auth with no human present. Revisit only if the account grows enough to
  justify it.
- Note: `update_trigger` can't change a trigger's prompt — to change what a
  scheduled run *does*, delete and recreate it.

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
