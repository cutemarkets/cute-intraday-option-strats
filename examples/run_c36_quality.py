"""Run the default c36_quality backtest from Python."""

from __future__ import annotations

from datetime import datetime

from cuteoptionstrats import build_default_model, run_default_backtest


def main() -> None:
    model = build_default_model()
    result = run_default_backtest(
        start=datetime(2025, 1, 1),
        end=datetime(2025, 1, 31),
        ticker="SPY",
        env_path=".env",
        return_trade_log=True,
    )
    print(
        {
            "model_id": model.model_id,
            "profile_name": result.get("profile_name"),
            "trades": result.get("trades"),
            "total_return": result.get("total_return"),
            "max_drawdown": result.get("max_drawdown"),
        }
    )


if __name__ == "__main__":
    main()
