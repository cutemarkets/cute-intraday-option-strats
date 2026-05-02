from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from cutebacktests import IntradayOptionsBacktester
from cutebacktests.providers import AlpacaDataProvider, CuteMarketsProvider
from cutebacktests.storage import DataStore

from .models import build_default_config, build_default_model, load_settings


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
