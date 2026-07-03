# Trading Policy & Guardrails

The rules the agent (Claude) follows when scanning, proposing, and (on approval)
executing trades on the **Claude** Robinhood account. Edit this file to change
the rules — the agent treats it as authoritative.

## Account scope
- **Only** the "Claude" account (agentic-enabled) is traded. All other accounts
  are read-only.
- **Equities:** live now.
- **Options:** only after options approval is enabled on the account. Via the
  agent, **single-leg only** (long calls/puts, covered calls, cash-secured puts).
  Multi-leg spreads are app-only and out of scope for the agent.

## Autonomy (current mode: TIER 1 — pre-approved setups auto-execute)
- **Pre-approved setups:** once the user approves a setup's PLAN (trigger + size
  + stop), the agent executes it automatically when the trigger confirms, then
  notifies. **No setups are pre-approved yet — nothing auto-trades until the user
  blesses a specific plan** (e.g., RIVN).
- **Novel / unplanned trades:** still proposed for explicit approval.
- Every options order is run through `review_option_order` first.
- **Tier 2 (full auto within guardrails) is NOT enabled.** Enabling it requires
  an explicit, unambiguous instruction in plain words (e.g., "enable Tier 2, full
  auto") — never inferred from a shorthand reply.

### Autonomy exception — raising cash from existing holdings
The agent is **pre-authorized to SELL** any of the four current Claude-account
positions — **NVDA, GOOGL, F, NOK** — without prior approval, but only to
reallocate into a better opportunity or cut clear downside. Constraints:
- Never sell just to hold cash, and never churn.
- This exception covers **sells only**; new buys still require approval.
- Respect settled-cash / good-faith rules — don't sell a newly bought position
  before the funding sale settles.
- Log every autonomous sell with the reason.

## Position sizing & cash rules
- **Settled cash only.** Never place a buy that isn't covered by settled cash —
  this avoids good-faith / free-riding violations on the cash account.
- **Max per position:** 20% of account value for equities.
- **Options cap:** total options premium at risk ≤ 10% of account value; any
  single option trade ≤ 5%. Options can go to zero — size accordingly.
- Keep a cash buffer; don't deploy 100% of settled cash at once.

## Risk management
- Every equity position gets a **stop-loss** (or a defined re-evaluation level).
- Long options are inherently defined-risk (max loss = premium paid); still cap
  size per the options cap above.
- Avoid earnings-week option lotto tickets and 0–1 DTE unless the user explicitly
  requests it for a specific trade.
- Prefer longer-dated options (more time = less decay pressure) when buying.

## The funnel (how a trade gets proposed)
1. **Scan** — screen the market with saved scanners (free).
2. **Shortlist** — reason over fundamentals/technicals/quotes to a handful.
3. **Deep-dive (optional)** — run TradingAgents on finalists (~$0.50 each).
4. **Propose** — thesis + entry + size + stop, shown to the user.
5. **Approve** — user confirms.
6. **Execute** — agent places the order (with `review_*` first for options).
7. **Log** — record the decision and outcome.

## Cost budget (LLM analysis)
- TradingAgents deep-dives are reserved for finalists, not the whole market.
- Track spend; flag the user when cumulative analysis spend passes each $2.50.

## Change log
- Initial policy created. Mode: propose-and-approve. Equities live; options
  pending account approval.
