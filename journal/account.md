# Account Facts

_Last updated: 2026-07-02_

## The tradeable account
- **Nickname:** "Claude" · **account_number:** `933543845`
- **agentic_allowed:** true (the only account this agent can trade)
- **option_level:** `option_level_2` — enabled 2026-07-02. Via the MCP, that
  means **single-leg only**: long calls/puts, covered calls, cash-secured puts.
  No spreads through the agent (app-only).
- **Account type (per broker API):** `cash` ⚠️ — the user reports enabling
  **margin**, but the API still returns `type: "cash"` as of 2026-07-02. Until
  the API shows `margin`, **treat as cash: settled funds only, no shorting.**
  Re-check `get_accounts` each session.
- **Value (2026-07-02):** ~$492.62 total · equity ~$392.62 · **cash $100** ·
  buying power $100.

## Current holdings (Claude account)
NVDA (0.516 sh), GOOGL (0.292 sh), F (7.125 sh), NOK (7.791 sh) — each was a
~$100 starter. Small gains as of 2026-06-30.

## Autonomy (see TRADING_POLICY.md for full rules)
- **Buys:** propose → user approves. Nothing bought without a "go".
- **Sells:** pre-authorized to sell **NVDA / GOOGL / F / NOK** to reallocate into
  a better opportunity (no churn; sells only; settled-cash aware).
- Options always run through `review_option_order` before placing.

## Sizing constraints (small account!)
- Max equity position: 20% of account (~$98 today).
- Options premium at risk: ≤10% total, ≤5% single trade (~$25) — so most single
  contracts are too big; options will be rare/tiny until the account grows.
- Keep a cash buffer; don't deploy 100%.

## Other accounts (read-only to this agent — do NOT trade)
Main (`5UW35123`, margin, option_level_3, the big one — holds MU, SOFI, HOOD,
etc.), plus Autopilot, AskLivermore, a Roth IRA, and a joint account.
