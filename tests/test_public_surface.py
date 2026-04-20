from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
from unittest.mock import patch

from cuteoptionstrats import (
    DEFAULT_MODEL_ID,
    DEFAULT_PROFILE_ALIAS,
    DEFAULT_PROFILE_NAME,
    DEFAULT_TICKERS,
    build_default_config,
    build_default_model,
    get_default_profile,
    load_settings,
)


def test_default_model_metadata_is_stable() -> None:
    model = build_default_model()
    assert model.model_id == DEFAULT_MODEL_ID
    assert model.profile_name == DEFAULT_PROFILE_NAME
    assert model.profile_alias == DEFAULT_PROFILE_ALIAS
    assert model.default_tickers == DEFAULT_TICKERS


def test_default_profile_resolves_to_c36_quality() -> None:
    profile = get_default_profile()
    assert profile.name == DEFAULT_PROFILE_NAME
    assert profile.option_target_dte == 1
    assert profile.option_max_dte == 2


def test_build_default_config_applies_profile_and_overrides() -> None:
    config = build_default_config(
        start=datetime(2025, 1, 1),
        end=datetime(2025, 1, 31),
        ticker="spy",
        initial_equity=250000.0,
        return_trade_log=True,
    )
    assert config.ticker == "SPY"
    assert config.initial_equity == 250000.0
    assert config.return_trade_log is True
    assert config.strategy_variant == get_default_profile().strategy_variant


def test_load_settings_honors_repo_scoped_data_path_aliases(tmp_path: Path) -> None:
    data_dir = tmp_path / "repo-data"
    db_path = data_dir / "cuteoptionstrats.duckdb"
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join(
            [
                f"CUTEOPTIONSTRATS_DATA_DIR={data_dir}",
                f"CUTEOPTIONSTRATS_DB_PATH={db_path}",
                "CUTEMARKETS_API_KEY=cm-key",
            ]
        ),
        encoding="utf-8",
    )

    with patch.dict(os.environ, {}, clear=True):
        settings = load_settings(str(env_path))

    assert settings.cutemarkets_api_key == "cm-key"
    assert settings.data_dir == data_dir
    assert settings.db_path == db_path
