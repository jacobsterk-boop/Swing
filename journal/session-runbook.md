# Session Runbook — the routine the agent runs each session

Goal: minimal user input. Ideally the user says **"run the routine"** and the
agent does everything below, surfacing only decisions that need a human.

## 0. Load context (no input needed)
Read `journal/` — `account.md`, `environment.md`, `playbook.md`,
`watchlist-setups.md`, and the latest `sessions/` log.

## 1. Refresh account state (no input needed)
- `get_accounts` → confirm the Claude account is agentic, its `option_level`,
  and whether `type` has flipped from `cash` to `margin`.
- `get_portfolio` + `get_equity_positions` (account `933543845`) → cash, buying
  power, current holdings.

## 2. Check active setups (no input needed to evaluate)
For each setup in `watchlist-setups.md`:
- Pull `get_equity_quotes` + `get_equity_historicals` (daily for RSI/levels,
  intraday for VWAP).
- **Compute indicators myself:** RSI(14), session VWAP (Σ(typical×vol)/Σvol,
  typical=(H+L+C)/3), 20/50 SMA, relative volume, recent support/resistance.
- Evaluate the trigger. If it fires → go to Step 5 (propose/execute). If it
  invalidated → log the invalidation and drop it.

## 3. Screen the WHOLE market for candidates (no input needed)
**Look everywhere — do not anchor to prior names or the watchlist.** Each
session restarts the search from scratch; previously-watched setups (incl. any
in `watchlist-setups.md`) compete on equal footing with fresh finds and get no
head start.
- **Primary breadth = the whole market**, via the TradingView whole-market
  screener output (user-run or exported) and/or `screen.py` over a broad list.
  This is the "everywhere" source.
- Also pull `get_equity_quotes` / historicals on the 43-name watchlist — but the
  watchlist is a **convenience list, not a boundary.**
- Rank ALL candidates together by: relative strength (green on a red tape) +
  **RelVol > 1** (conviction) + RSI in a healthy zone (not >70) + liquid names.
- Surface the best 1–3 regardless of where they came from.

## 4. Deep-dive finalists (optional, ~$0.50 each)
Run TradingAgents only on the top 1–3 finalists when a decision is close.

## 5. Propose or execute (per autonomy tier — see below)
- Build each proposal: thesis + entry + **size (within TRADING_POLICY caps)** +
  **stop at a real structural level** + target.
- Options: always `review_option_order` first.
- Execute per the current autonomy tier.

## 6. Log & update memory (no input needed)
- Append to `sessions/<date>.md` (decisions + outcomes).
- Move fired/invalidated setups out of `watchlist-setups.md`; add new ones.
- Update `account.md` / `environment.md` if any facts changed.
- Report a concise summary.

---

## Autonomy tiers (user picks)
- **Tier 0 — Propose→Approve.** Every buy waits for an explicit "go".
- **Tier 1 — Pre-approved conditional setups.** Approved plans auto-execute on
  trigger; novel ideas proposed.
- **Tier 2 — Auto within guardrails (CURRENT, enabled 2026-07-06).** Agent
  initiates equity buys/sells within the TRADING_POLICY guardrails without
  pre-approval (≤2 new positions/session, stop at entry, ≤20%/position, settled
  cash, no-chase binding, full report). Options stay propose-first.

> **Reality check — Tier 2 ≠ unattended trading.** Background/scheduled sessions
> still cannot reach the Robinhood connector (see environment.md), so auto-
> execution only happens **inside a live session** — i.e., when Jacob taps a
> reminder and says "run the routine." What Tier 2 buys us today is *no
> stop-and-ask on every trade during that live run*, not trading while he's away.

**Broker-native automation (works with NO session running):** for a planned
entry, place a resting **stop-limit buy** (fills only on a strength trigger) or
**limit buy** (fills only on a pullback), each paired with a protective **stop**.
Robinhood executes these unattended. Use where the trigger can be expressed as a
price level (dynamic triggers like "reclaim VWAP" still need a live session).
