# finbert-sentiment-trader

A 2024 experiment that traded SPY based on FinBERT sentiment scores of news headlines.
Archived here as a post-mortem — the system didn't work, and the specific reasons were
worth writing down. Lessons directly informed the risk engine in
[QuantWorkstation](https://github.com/william-burks/QuantWorkstation).

## What it did

Pull a 3-day window of news headlines for a symbol via Alpaca News API →
classify with ProsusAI/finbert → trade when sentiment probability exceeded a
threshold. Flask app wrapped the strategy for introspection during runs.

Stack: Python 3.12 · lumibot · alpaca-trade-api · transformers · Flask.

```
news → FinBERT (positive/negative/neutral + prob) → threshold check → Alpaca order
```

## Results

Two configurations were run against the same in-sample window and benchmark.
Numbers below are pulled from the contemporaneous backtest reports
(QuantStats tearsheet for v1, A/B comparison report for v1 vs v2) and are
reproduced verbatim for honesty — including the failures.

- **Instrument:** SPY (daily bars, Alpaca)
- **In-sample window:** 2020-01-01 → 2023-12-31
- **Benchmark:** SPY buy-and-hold over the same window

| Metric              | pre-Alpha 1.0.0 (v1) | pre-Alpha 1.0.1 (v2) | Benchmark (SPY) |
|---------------------|----------------------|----------------------|-----------------|
| Cumulative Return   | 34.82%               | 2,124.68%            | 56.05%          |
| CAGR                | 7.77%                | 117.41%              | 11.78%          |
| Sharpe Ratio        | 0.19                 | 1.06                 | 0.30            |
| Max Drawdown        | -14.15%              | -94.16%              | -33.68%         |
| Volatility (annual) | 6.93%                | 115.51%              | 20.53%          |
| Recovery Factor     | 2.46                 | —                    | 1.66            |
| Time in Market      | ~51%                 | —                    | 100%            |
| 2022 EOY Return     | -0.21%               | —                    | -18.16%         |

**How to read this.** v1 is a *conservative under-trader*: lower volatility
than the benchmark (6.93% vs 20.53%), shallower drawdown (-14.15% vs
-33.68%), and better recovery factor (2.46 vs 1.66) — but leaves return on
the table (Sharpe 0.19 vs 0.30, CAGR 7.77% vs 11.78%). The one genuinely
interesting datapoint is 2022: v1 returned -0.21% against SPY's -18.16%,
suggesting the sentiment filter was risk-off when it mattered. That's
suggestive, not dispositive — a single down year on one instrument is
anecdote, not edge.

v2 looks like a different animal on paper — Sharpe 1.06, 2,125% cumulative
return — but the -94.16% max drawdown and 115.51% annualized volatility
mean the strategy effectively blew up mid-run and clawed back through
leverage on a rising benchmark. Triple-digit volatility on an equity
strategy is a sizing failure, not a signal edge. Neither version is
deployable.

Trade count, turnover, and profit factor were not captured in the original
reports — a gap flagged in the post-mortem below and addressed in
QuantWorkstation's IS/OOS evidence harness.

## What went wrong

1. **Position sizing was naive.** `cash_at_risk = 0.5` meant 50% of available
   cash on every qualifying signal. No Kelly fraction, no volatility scaling,
   no conviction weighting beyond the threshold. A single bad trade could halve
   the account. This is the headline failure.

2. **The threshold was a step function, not conviction.** `probability > 0.999`
   → full position. `0.998` → zero position. A continuous sizing curve would
   have been trivial; I didn't build one.

3. **Fixed TP/SL were blind to volatility.** 20% take-profit, 5% stop-loss on
   every trade. SPY's realized vol on short horizons eats those levels through
   noise, not signal.

4. **3-day sentiment window on a daily strategy.** Sentiment coverage lags
   price. By the time the bot saw a positive classification above threshold,
   the move had been in for days.

5. **FinBERT's probability wasn't a return predictor.** The model classifies
   financial text as positive/negative/neutral — it was never trained to
   predict next-day returns. I used it as a proxy for forecast confidence,
   which is a category error.

## What I'd do differently

- Size by (conviction × inverse volatility), not a static cash fraction
- Use a fractional-Kelly or risk-parity approach
- Set TP/SL in terms of ATR, not fixed percent
- Treat sentiment as a feature in a broader signal stack with explicit
  next-return validation — not a standalone trigger
- Backtest first with walk-forward validation; don't deploy on paper without it

## What was useful

- FinBERT integration is clean (~30 lines: tokenize → softmax → argmax)
- Flask API layer made state inspection during runs easy
- Taught me that solid architecture around a bad signal is still bad — the
  subsequent project (QuantWorkstation) is research-first

## Superseded by

[QuantWorkstation](https://github.com/william-burks/QuantWorkstation) —
research harness with IS/OOS evidence gating, a risk engine with per-trade and
portfolio-level caps, and no promotion to live without walk-forward validation.
The killed-champion story in that repo's history is an outcome of applying
lessons from this one.

## Running it

Don't. See post-mortem above. If you want to read the code anyway:

```bash
cp example.env .env  # fill in Alpaca paper keys
pip install -r requirements.txt
python startup.py
```

Paper trading only. The code is preserved as the artifact, not recommended
for use.
