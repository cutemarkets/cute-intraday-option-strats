from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import os
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

from cutebacktests import IntradayOptionsBacktestConfig, OpeningRangeProfile, get_opening_range_profile
from cutebacktests.settings import Settings


DEFAULT_MODEL_ID = "c36_quality"
DEFAULT_PROFILE_ALIAS = "c36_quality"
DEFAULT_PROFILE_NAME = "c36_vwap_mr_option_native_quality_v1"
DEFAULT_TICKERS: Tuple[str, ...] = ("SPY", "QQQ")

_ENV_ALIASES = (
    ("CUTEOPTIONSTRATS_DATA_DIR", "CUTEBACKTESTS_DATA_DIR"),
    ("CUTEOPTIONSTRATS_DB_PATH", "CUTEBACKTESTS_DB_PATH"),
)


@dataclass(frozen=True)
class StrategyModel:
    model_id: str
    profile_name: str
    profile_alias: str
    description: str
    default_tickers: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _read_env_file(env_path: Path) -> Dict[str, str]:
    payload: Dict[str, str] = {}
    if not env_path.exists():
        return payload
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        payload[key.strip()] = value.strip().strip('"').strip("'")
    return payload


def _apply_repo_env_aliases(env_values: Optional[Mapping[str, str]] = None) -> None:
    source = env_values or os.environ
    for repo_key, runtime_key in _ENV_ALIASES:
        value = str(source.get(repo_key) or "").strip()
        if value and not os.getenv(runtime_key):
            os.environ[runtime_key] = value


def load_settings(env_path: str = ".env") -> Settings:
    env_file = Path(env_path)
    _apply_repo_env_aliases(_read_env_file(env_file))
    _apply_repo_env_aliases()
    return Settings.from_env(env_path)


def build_default_model() -> StrategyModel:
    return StrategyModel(
        model_id=DEFAULT_MODEL_ID,
        profile_name=DEFAULT_PROFILE_NAME,
        profile_alias=DEFAULT_PROFILE_ALIAS,
        description="Quote-aware 0-2 DTE VWAP mean-reversion options model.",
        default_tickers=DEFAULT_TICKERS,
    )


def get_default_profile(or_width_min: Optional[float] = None) -> OpeningRangeProfile:
    if or_width_min is None:
        return get_opening_range_profile(DEFAULT_PROFILE_ALIAS)
    return get_opening_range_profile(DEFAULT_PROFILE_ALIAS, or_width_min=or_width_min)


def build_default_config(
    *,
    start: datetime,
    end: datetime,
    ticker: str = "SPY",
    or_width_min: Optional[float] = None,
    **overrides: Any,
) -> IntradayOptionsBacktestConfig:
    profile = get_default_profile(or_width_min=or_width_min)
    cfg_kwargs = profile.to_intraday_strategy_kwargs()
    cfg_kwargs.update(overrides)
    cfg_kwargs["start"] = start
    cfg_kwargs["end"] = end
    cfg_kwargs["ticker"] = str(ticker).strip().upper()
    return IntradayOptionsBacktestConfig(**cfg_kwargs)
