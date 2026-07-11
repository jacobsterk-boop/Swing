# Account Facts

_Last updated: 2026-07-06_

## The tradeable account
- **Nickname:** "Claude" · **account_number:** `933543845`
- **agentic_allowed:** true (the only account this agent can trade)
- **option_level:** `option_level_2` — enabled 2026-07-02. Via the MCP, that
  means **single-leg only**: long calls/puts, covered calls, cash-secured puts.
  No spreads through the agent (app-only).
- **Account type: `cash` — BY DESIGN, permanent.** (2026-07-06) Jacob researched
  it: Robinhood does **not allow agentic accounts to be margin** — cash-only is
  their guardrail against agents over-trading. Stop expecting the type to flip;
  no shorting; settled-funds mechanics apply forever on this account. The
  broker's live `buying_power` figure (from `get_portfolio`) is authoritative
  for what's spendable — it already excludes unsettled proceeds.
- **PDT rule is GONE (regulatory).** SEC approved FINRA's Rule 4210 amendment
  2026-04-14; effective **2026-06-04** the pattern-day-trader designation and
  $25k minimum are eliminated (replaced by real-time intraday margin standards
  for margin accounts). Cash accounts were never PDT-bound anyway — good-faith
  (settlement) rules are what still bind us. Verified via FINRA Notice 26-10.
- **Value (2026-07-06 ~11:45 ET):** ~$2,200 total · equity ~$640 ·
  cash ~$1,560 · settled buying power ~$1,159. Jacob deposited ~$500 over the
  7/4 weekend + ~$200 more on 7/6.

## Status: PAUSED (2026-07-10)
Jacob paused the operation. All three scheduled reminder triggers
(open/mid-day/afternoon) were **deleted** — no automated pings until he restarts.
Account sits all-cash; no open positions or resting orders to babysit. To resume,
recreate the reminder triggers (see environment.md for the recipe) and pick an
autonomy tier. Current tier remains Tier 2 (per TRADING_POLICY.md) but nothing
runs until a live "run the routine".

## Current holdings (Claude account)
- **NONE — all cash (~$1,460) as of 2026-07-08.**
- Recent exits: SOFI stopped out 2026-07-07 @ $17.70 (−6.4%); SMH stopped out
  2026-07-07 @ ~$578 (−6.1%); legacy NVDA/GOOGL/F/NOK sold 2026-07-06.
- Both stops fired as designed on a choppy sawtooth semis tape (bounce Mon,
  reverse Tue, bounce Wed). Lesson reinforced: don't chase the semis bounce.

## Cash movement (2026-07-07) — RESOLVED
Cash fell ~$700 overnight (Mon close $2,199.98 → Tue open $1,468.28). Jacob
confirmed: he'd moved that money IN on 7/6 to hit the $2,000 margin threshold,
then moved it back OUT once we established the agentic account is cash-only (no
margin available) and PDT is gone — so the extra cash served no purpose.
Deliberate withdrawal, not an error. **True account value ≈ $1,468; size off the
live `buying_power` figure as always.** Don't expect deposits to stick around
solely for a margin threshold that doesn't apply here.

## Autonomy (see TRADING_POLICY.md for full rules)
- **Current: TIER 2 — ENABLED 2026-07-06** by Jacob's explicit instruction.
  Agent may auto-initiate equity buys AND sells within the guardrail package:
  ≤2 new positions/session, a stop at entry on every buy (resting GTC for
  whole-share lots, documented managed stop for fractional), ≤20%/position,
  settled cash only, playbook no-chase rules binding, full after-session report.
- **Options stay propose-first** — always run through `review_option_order`;
  never auto-executed under Tier 2.
- **Kill-switch:** "back to Tier 1", "Tier 0", or "pause trading" reverts
  instantly; any bad surprise → agent proposes dialing back on its own.

## Sizing constraints
- Max equity position: 20% of account (~$440 at current size).
- Options premium at risk: ≤10% total (~$220), ≤5% single trade (~$110).
- Keep a cash buffer; don't deploy 100% of settled cash.

## Other accounts (read-only to this agent — do NOT trade)
Main (`5UW35123`, margin, option_level_3, the big one — holds MU, SOFI, HOOD,
etc.), plus Autopilot, AskLivermore, a Roth IRA, and a joint account.
