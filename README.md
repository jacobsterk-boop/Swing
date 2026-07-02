# Swing

A thin, one-command wrapper around [**TradingAgents**](https://github.com/TauricResearch/TradingAgents)
(Tauric Research) for running multi-agent stock analyses and turning them into
actual trade decisions.

TradingAgents simulates a trading desk: role-based LLM agents (fundamentals,
sentiment, news, technicals) each analyze a ticker, then research-manager /
trader / portfolio-manager agents debate and converge on a **BUY / SELL / HOLD**
call. This repo just makes running it a single command and keeps your config and
results tidy.

> Credit: the analysis engine is [TradingAgents by Tauric Research](https://github.com/TauricResearch/TradingAgents).
> This repo does **not** vendor their code — install it separately (below).
> Like the maintainers, treat it as a research/second-opinion tool, not a
> money-printer.

## Setup

1. **Install TradingAgents** (from their repo, in the same Python env):
   ```bash
   git clone https://github.com/TauricResearch/TradingAgents.git
   cd TradingAgents && pip install -e .
   ```

2. **Add your API keys** — copy the template and fill it in:
   ```bash
   cp .env.example .env
   # then edit .env
   ```
   You need a `FINNHUB_API_KEY` (free tier is fine) and an `ANTHROPIC_API_KEY`.
   Some TradingAgents versions also want `OPENAI_API_KEY` for the embeddings/
   memory layer even when the agents run on Claude — uncomment it in `.env` if
   you hit an embeddings error.

## Usage

```bash
python run.py NVDA                     # analyze NVDA as of today
python run.py NVDA --date 2026-06-30   # a specific date
python run.py AAPL --debug             # stream the agent debate
python run.py TSLA --rounds 2          # deeper (more expensive) debate
make run TICKER=AAPL                   # same thing via make
```

Each run prints the final decision and saves the full result to
`results/<TICKER>_<DATE>_<timestamp>.json` (gitignored).

### Batch mode (the whole watchlist)

`universe.txt` holds the swing universe (one ticker per line, `#` comments ok) —
it mirrors the **Swing** watchlist on the trading account. Analyze all of them
and get a ranked BUY/HOLD/SELL summary:

```bash
python run.py --universe universe.txt   # run the whole list
make universe                           # same thing
```

Batch mode is resilient — a single failing ticker is logged and skipped, not
fatal — and writes a combined `results/_batch_<DATE>_<timestamp>.json` plus the
per-ticker files. Heads-up: 43 names × a full agent debate is a lot of tokens;
start with a couple of names or a cheap `--quick` model before running the lot.

### Cost control
- Analysts run on a cheap/fast model (`--quick`, default Haiku); the debate runs
  on a stronger model (`--deep`, default Sonnet — a cost/quality balance). Pass
  `--deep claude-opus-4-8` if you want maximum analysis quality at higher cost.
- `--rounds 1` (default) keeps token spend down. Raise it only when you want a
  more thorough debate.

## From decision to trade

TradingAgents outputs a **decision** — it does **not** place orders. The intended
workflow is:

```
run.py (this repo)  ->  BUY/SELL/HOLD + reasoning  ->  you review  ->  execute
```

Execution is a separate, deliberate step — sized small, within settled cash, with
a stop-loss. Keep a human in the loop before real money moves.

## Config knobs

Defaults live at the top of `run.py`. If your installed TradingAgents version
uses different config field names, edit the `CONFIG_KEYS` map in `run.py` — it's
the single place that translates this wrapper's options to their config.
