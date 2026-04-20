"""Curated strategy presets built on top of cutebacktests."""

from .models import (
    DEFAULT_MODEL_ID,
    DEFAULT_PROFILE_ALIAS,
    DEFAULT_PROFILE_NAME,
    DEFAULT_TICKERS,
    StrategyModel,
    build_default_config,
    build_default_model,
    get_default_profile,
    load_settings,
)
from .runtime import build_backtester, run_default_backtest

__all__ = [
    "DEFAULT_MODEL_ID",
    "DEFAULT_PROFILE_ALIAS",
    "DEFAULT_PROFILE_NAME",
    "DEFAULT_TICKERS",
    "StrategyModel",
    "build_backtester",
    "build_default_config",
    "build_default_model",
    "get_default_profile",
    "load_settings",
    "run_default_backtest",
]

__version__ = "0.1.0"
