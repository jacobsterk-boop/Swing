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

## Current holdings (Claude account)
- **SMH** 0.487258 sh @ $615.69 (~$300) — **managed stop $580** (fractional =
  no resting stop possible; enforce at every check-in).
- **SOFI** 18 sh @ $18.92 (~$341) — **resting GTC stop $17.70** on the books
  (order `6a4bcc52`). Protects itself unattended.
- (Legacy NVDA/GOOGL/F/NOK all sold at the open 2026-07-06 per plan.)

## Autonomy (see TRADING_POLICY.md for full rules)
- **Current: TIER 1** — pre-approved setups auto-execute; novel buys proposed.
- **Tier 2 under discussion (2026-07-06):** Jacob proposed it ("Thoughts?") on
  the grounds that the cash account naturally throttles churn. Agent recommended
  YES with a written guardrail package (max 2 new positions/session, stop at
  entry on every buy, playbook no-chase rules binding, options stay
  propose-first, full after-session report). **Awaiting Jacob's explicit
  plain-words confirmation ("enable Tier 2") — not enabled yet.**
- Options always run through `review_option_order` before placing.

## Sizing constraints
- Max equity position: 20% of account (~$440 at current size).
- Options premium at risk: ≤10% total (~$220), ≤5% single trade (~$110).
- Keep a cash buffer; don't deploy 100% of settled cash.

## Other accounts (read-only to this agent — do NOT trade)
Main (`5UW35123`, margin, option_level_3, the big one — holds MU, SOFI, HOOD,
etc.), plus Autopilot, AskLivermore, a Roth IRA, and a joint account.
