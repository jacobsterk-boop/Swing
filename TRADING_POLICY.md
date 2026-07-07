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

## Autonomy (current mode: TIER 2 — auto within guardrails)
**Enabled 2026-07-06 by Jacob's explicit instruction ("enable Tier 2").** The
agent may INITIATE equity buys and sells on the Claude account without prior
approval, provided every guardrail below is met. This is the highest trust
level; it works because the agentic account is mechanically forced to be a
**cash** account (Robinhood does not allow margin on agentic accounts — this is
itself a throttle on churn), and the agent only acts inside scheduled check-ins.

### Tier 2 guardrails (ALL binding — a trade that fails any one waits for approval)
1. **Max 2 NEW equity positions opened per session.** Adds/exits to existing
   positions don't count against this, but don't churn.
2. **Every buy ships with a stop, placed at entry.** Whole-share lots get a
   resting GTC stop order immediately. Fractional lots (no broker stop possible —
   see environment.md) get a **documented managed stop** logged in the session
   file and enforced at every check-in — prefer whole-share names when a hard
   stop matters.
3. **Sizing caps hold:** ≤20% of account value per equity position; **settled
   `buying_power` only** (the cash account blocks unsettled use anyway — respect
   it, don't fight it); keep a cash buffer (don't deploy 100%).
4. **No-chase rules are binding** (see playbook): no entries on daily RSI > 70;
   confirm price is holding above session VWAP; favor the least-extended leader,
   not the biggest green number; RelVol > 1 for conviction.
5. **Options stay propose-first.** No auto-executed options under Tier 2 — every
   options order is proposed, then run through `review_option_order` on approval.
   (Options can go to zero; they stay a human decision for now.)
6. **No new position within its earnings week** unless proposed first.
7. **Full transparency:** every auto-executed trade is logged to the session
   file with thesis + size + stop + reason, and reported to Jacob in the
   after-session summary. Nothing happens silently.

### Downgrade / kill-switch
Jacob can say "back to Tier 1" (or "Tier 0", or "pause trading") at any time and
the agent reverts immediately. Any single bad surprise → the agent proactively
proposes dialing back rather than pressing on.

### Regulatory notes (verified 2026-07-06)
- **PDT rule is GONE.** The SEC approved eliminating the $25k pattern-day-trader
  minimum and the PDT designation (FINRA Rule 4210 amendment, effective
  2026-06-04). Day-trade counting no longer applies. Not a constraint for us.
- **Agentic account is cash-only by Robinhood policy** — margin isn't offered on
  agentic accounts. So good-faith/settlement rules (settled funds only) remain
  the real mechanical guardrail, and that's fine — it caps aggression by design.

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
- 2026-07-06: **Tier 2 enabled** (auto equity buys/sells within the guardrails
  above), per Jacob's explicit instruction. Options remain propose-first.
  Recorded verified regulatory facts: PDT rule eliminated (2026-06-04); agentic
  account is cash-only by broker policy.
