from __future__ import annotations

from datetime import datetime
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, List, Optional

from cutebacktests import IntradayOptionsBacktester
from cutebacktests.providers import AlpacaDataProvider, CuteMarketsProvider
from cutebacktests.storage import DataStore

from .models import DEFAULT_TICKERS, build_default_config, build_default_model, load_settings


def build_backtester(
    *,
    settings,
    store: DataStore,
    include_alpaca: bool = False,
) -> IntradayOptionsBacktester:
    return IntradayOptionsBacktester(
        store=store,
        cutemarkets_provider=CuteMarketsProvider(settings),
        alpaca_data_provider=AlpacaDataProvider(settings) if include_alpaca else None,
    )


def run_default_backtest(
    *,
    start: datetime,
    end: datetime,
    ticker: str = "SPY",
    env_path: str = ".env",
    db_path: Optional[str] = None,
    include_alpaca: bool = False,
    or_width_min: Optional[float] = None,
    **config_overrides: Any,
) -> Dict[str, Any]:
    settings = load_settings(env_path)
    store_path = Path(db_path) if db_path else settings.db_path
    store = DataStore(store_path)
    try:
        backtester = build_backtester(settings=settings, store=store, include_alpaca=include_alpaca)
        result = backtester.run(
            build_default_config(
                start=start,
                end=end,
                ticker=ticker,
                or_width_min=or_width_min,
                **config_overrides,
            )
        )
    finally:
        store.close()

    result["model"] = build_default_model().to_dict()
    result["profile_name"] = result.get("profile_name") or build_default_model().profile_name
    return result


def run_default_universe_backtests(
    *,
    start: datetime,
    end: datetime,
    env_path: str = ".env",
    db_path: Optional[str] = None,
    include_alpaca: bool = False,
    or_width_min: Optional[float] = None,
    **config_overrides: Any,
) -> Dict[str, Any]:
    ticker_results: Dict[str, Dict[str, Any]] = {}
    combined_trade_log: List[Dict[str, Any]] = []
    for ticker in DEFAULT_TICKERS:
        result = run_default_backtest(
            start=start,
            end=end,
            ticker=ticker,
            env_path=env_path,
            db_path=db_path,
            include_alpaca=include_alpaca,
            or_width_min=or_width_min,
            **config_overrides,
        )
        ticker_results[ticker] = dict(result)
        if isinstance(result.get("trade_log"), list):
            combined_trade_log.extend(dict(row) for row in result["trade_log"])

    returns = [float(result.get("total_return") or 0.0) for result in ticker_results.values()]
    sharpes = [float(result.get("sharpe") or 0.0) for result in ticker_results.values()]
    sortinos = [float(result.get("sortino") or 0.0) for result in ticker_results.values()]
    rocis = [float(result.get("roci") or 0.0) for result in ticker_results.values()]
    drawdowns = [float(result.get("max_drawdown") or 0.0) for result in ticker_results.values()]
    combined_summary = {
        "ticker_count": len(ticker_results),
        "trades_total": int(sum(int(result.get("trades") or 0) for result in ticker_results.values())),
        "mean_total_return": float(mean(returns)) if returns else 0.0,
        "median_total_return": float(median(returns)) if returns else 0.0,
        "mean_sharpe": float(mean(sharpes)) if sharpes else 0.0,
        "mean_sortino": float(mean(sortinos)) if sortinos else 0.0,
        "mean_roci": float(mean(rocis)) if rocis else 0.0,
        "worst_max_drawdown": float(min(drawdowns)) if drawdowns else 0.0,
    }
    payload: Dict[str, Any] = {
        "model": build_default_model().to_dict(),
        "per_ticker": ticker_results,
        "combined_summary": combined_summary,
    }
    if combined_trade_log:
        payload["combined_trade_log"] = combined_trade_log
    return payload
