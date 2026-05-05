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
    build_effective_config_payload,
    build_default_model,
    get_default_profile,
    load_settings,
)
from cuteoptionstrats import cli as public_cli


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


def test_public_cli_keeps_backwards_compatible_alpaca_flags() -> None:
    parser = public_cli.build_parser()
    default_args = parser.parse_args(
        ["run-backtest", "--ticker", "SPY", "--start", "2025-01-01", "--end", "2025-01-31"]
    )
    with_flag = parser.parse_args(
        ["run-backtest", "--ticker", "SPY", "--start", "2025-01-01", "--end", "2025-01-31", "--with-alpaca"]
    )
    without_flag = parser.parse_args(
        [
            "run-backtest",
            "--ticker",
            "SPY",
            "--start",
            "2025-01-01",
            "--end",
            "2025-01-31",
            "--without-alpaca",
        ]
    )

    assert default_args.with_alpaca is False
    assert with_flag.with_alpaca is True
    assert without_flag.with_alpaca is False


def test_public_cli_accepts_new_research_commands() -> None:
    parser = public_cli.build_parser()
    run_default_universe = parser.parse_args(
        ["run-default-universe", "--start", "2025-01-01", "--end", "2025-01-31"]
    )
    show_effective = parser.parse_args(["show-effective-config"])
    assert run_default_universe.command == "run-default-universe"
    assert show_effective.command == "show-effective-config"


def test_effective_config_payload_is_stable_for_key_model_fields() -> None:
    payload = build_effective_config_payload(
        start=datetime(2025, 1, 1),
        end=datetime(2025, 1, 31),
        ticker="SPY",
    )
    assert payload["model"]["model_id"] == DEFAULT_MODEL_ID
    assert payload["strategy_variant"] == "mr_vwap_zscore_v2"
    assert payload["option_target_dte"] == 1
    assert payload["option_max_dte"] == 2
    assert payload["require_option_microstructure_filter"] is True
    assert payload["mr_zscore_entry"] == 1.35
