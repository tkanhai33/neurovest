# Evaluating a trading strategy before trusting it

A strategy should be treated as a testable hypothesis, not a promise.
Start by writing its market, instruments, holding period, entry rule,
exit rule, position sizing, and risk limits in plain language. If the
rules cannot be stated clearly, the result cannot be audited well.

Review evidence across more than one market period. Check return,
drawdown, volatility, win rate, turnover, and the effect of fees,
spreads, slippage, and taxes where relevant. A strategy that only
works in one unusually favourable period may be overfit.

Separate in-sample development from out-of-sample testing. Avoid
changing rules repeatedly until historical results look perfect.
Compare the result with a simple benchmark and consider whether the
strategy is realistic to execute at the intended scale.

Before treating anything as actionable, use controlled paper
evaluation and preserve the evidence, assumptions, and limitations.
Historical performance does not guarantee future results.
