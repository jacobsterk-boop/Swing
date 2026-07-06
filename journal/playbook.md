# Playbook — Rules & Lessons Learned

_Living document. Add a dated lesson whenever a trade or observation teaches one._

## Entry discipline
- **Don't chase overbought.** On 2026-07-02, FROG looked great on relative
  strength (+5.5% on a red day) but daily **RSI was 76.94** (>70) and the 5-min
  was **fading below the upper VWAP band** — classic exhaustion. We passed. The
  best trade that day was the one we didn't make.
- **Always do the intraday check before a big-mover entry:** (1) daily RSI(14) —
  skip/shrink if >70; (2) 5-min price vs VWAP — above = buyers in control; (3)
  is it holding the breakout level? The user reads these from TradingView fast.
- **Conviction = volume.** Favor **Relative Volume > 1** on breakouts; a big move
  on below-average volume is weak signal.
- **Buy strength at good entries, not extended ones.** Prefer a breakout that's
  holding its level, or a pullback to a rising base, over chasing a +8% intraday spike.
- **In a broad gap-up bounce, the names up the LEAST are the best entries.**
  2026-07-06: the semis complex snapped back off the 7/2 washout — BE +11.6%,
  SIMO +11.2%, AMBA +10.1% vs SMH +3.4%. Chasing the +10–12% names puts your
  stop 11%+ below you (poor R/R); SMH near its base takes a tight stop. Same
  thesis ("semis recovering"), far better risk-adjusted expression. Prefer the
  ETF or the least-extended leader, not the biggest green number.

## Risk
- **Every position gets a stop** placed below a real structural level (base /
  breakout shelf), not an arbitrary %.
- Size so max loss per trade is ~1–2% of the account.
- On broad **risk-off days** (sector down 5%+), the hunting ground is
  **relative-strength leaders** (green while everything's red) — but confirm
  they're not overextended before entering.

## Market-structure notes
- 2026-07-02 was a broad **semiconductor/AI washout** — money rotated OUT of
  chips (watchlist −5% to −19%) INTO healthcare, software, utilities, consumer.
  The TradingAgents MU deep-dive (Underweight, cyclical-peak thesis) called this
  well the day before it accelerated.

## Process
- **Verify regulatory/market-structure claims with a web search — don't answer
  from memory.** (2026-07-06) The agent warned Jacob about PDT rules that had
  been abolished a month earlier (effective 2026-06-04). Rules change; training
  knowledge goes stale. When a decision touches regulation, account mechanics,
  or anything datable, search first.
- Whole-market breadth comes from the **TradingView screener** (RH scanner is
  broken). Reserve the ~$0.50 TradingAgents deep-dive for finalists only.
- Log every proposal and outcome in `sessions/` so we can review what worked.
