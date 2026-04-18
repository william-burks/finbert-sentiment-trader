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
