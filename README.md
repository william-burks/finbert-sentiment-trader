# finbert-sentiment-trader

A 2024 experiment that traded SPY based on FinBERT sentiment scores of news headlines.
Archived here as a post-mortem — the system didn't work, and the specific reasons were
worth writing down. Lessons directly informed the risk engine in
[QuantWorkstation](https://github.com/Burkswill2/QuantWorkstation).

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
Numbers below are pulled from the contemporaneous backtest report
(`pre-Alpha 1.0.0` vs `pre-Alpha 1.0.1`) and are reproduced verbatim for
honesty — including the failures.

- **Instrument:** SPY (daily bars, Alpaca)
- **In-sample window:** 2020-01-01 → 2023-12-31
- **Benchmark:** SPY buy-and-hold over the same window

| Metric              | pre-Alpha 1.0.0 (v1) | pre-Alpha 1.0.1 (v2) | Benchmark |
|---------------------|----------------------|----------------------|-----------|
| Cumulative Return   | 34.82%               | 2,124.68%            | 56.05%    |
| CAGR                | 7.77%                | 117.41%              | 11.78%    |
| Sharpe Ratio        | 0.19                 | 1.06                 | 0.03      |
| Max Drawdown        | -14.15%              | -94.16%              | -33.68%   |
| Volatility (annual) | 6.93%                | 115.51%              | 20.53%    |

**How to read this.** v2's Sharpe and cumulative return look impressive in
isolation, but the -94.16% max drawdown means the strategy effectively blew
up mid-run and clawed back. A ~115% annualized volatility on an equity
strategy is a sizing failure, not a signal edge — the Sharpe improvement
over v1 is almost entirely a compounding artifact from running leveraged
aggressive position sizing over a rising benchmark. v1 under-trades
(Sharpe 0.19, vol 6.93% vs a 20.53% benchmark); v2 over-trades to the point
of ruin. Neither is a deployable system.

Trade count, turnover, and profit factor were not captured in the original
report — a gap flagged in the post-mortem below and addressed in
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

[QuantWorkstation](https://github.com/Burkswill2/QuantWorkstation) —
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
