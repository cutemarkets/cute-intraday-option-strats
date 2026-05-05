from __future__ import annotations

import argparse
import json
from datetime import datetime
from typing import Any, Dict, Optional

from .models import build_default_model, build_effective_config_payload
from .runtime import run_default_backtest, run_default_universe_backtests


def _parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Curated public options strategies built on cutebacktests.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_model = subparsers.add_parser("show-model", help="Print metadata for the default model.")
    show_model.add_argument("--json-indent", type=int, default=2)

    run_backtest = subparsers.add_parser("run-backtest", help="Run the default c36 strategy backtest.")
    run_backtest.add_argument("--ticker", default="SPY")
    run_backtest.add_argument("--start", required=True, help="YYYY-MM-DD")
    run_backtest.add_argument("--end", required=True, help="YYYY-MM-DD")
    run_backtest.add_argument("--env-path", default=".env")
    run_backtest.add_argument("--db-path", default="")
    run_backtest.add_argument("--or-width-min", type=float, default=None)
    run_backtest.add_argument("--initial-equity", type=float, default=100000.0)
    run_backtest.add_argument("--risk-per-trade", type=float, default=0.02)
    run_backtest.add_argument("--max-trades-per-day", type=int, default=1)
    run_backtest.add_argument("--return-trade-log", action="store_true")
    run_backtest.add_argument(
        "--with-alpaca",
        dest="with_alpaca",
        action="store_true",
        help="Optionally enable the auxiliary Alpaca provider. CuteMarkets remains the default API path.",
    )
    run_backtest.add_argument(
        "--without-alpaca",
        dest="with_alpaca",
        action="store_false",
        help=argparse.SUPPRESS,
    )
    run_backtest.set_defaults(with_alpaca=False)
    run_backtest.add_argument("--json-indent", type=int, default=2)

    run_default_universe = subparsers.add_parser(
        "run-default-universe",
        help="Run the default c36 strategy across the package's default ticker universe.",
    )
    run_default_universe.add_argument("--start", required=True, help="YYYY-MM-DD")
    run_default_universe.add_argument("--end", required=True, help="YYYY-MM-DD")
    run_default_universe.add_argument("--env-path", default=".env")
    run_default_universe.add_argument("--db-path", default="")
    run_default_universe.add_argument("--or-width-min", type=float, default=None)
    run_default_universe.add_argument("--initial-equity", type=float, default=100000.0)
    run_default_universe.add_argument("--risk-per-trade", type=float, default=0.02)
    run_default_universe.add_argument("--max-trades-per-day", type=int, default=1)
    run_default_universe.add_argument("--return-trade-log", action="store_true")
    run_default_universe.add_argument(
        "--with-alpaca",
        dest="with_alpaca",
        action="store_true",
        help="Optionally enable the auxiliary Alpaca provider. CuteMarkets remains the default API path.",
    )
    run_default_universe.add_argument(
        "--without-alpaca",
        dest="with_alpaca",
        action="store_false",
        help=argparse.SUPPRESS,
    )
    run_default_universe.set_defaults(with_alpaca=False)
    run_default_universe.add_argument("--json-indent", type=int, default=2)

    show_effective_config = subparsers.add_parser(
        "show-effective-config",
        help="Resolve the inherited cutebacktests profile into a concrete JSON config payload.",
    )
    show_effective_config.add_argument("--ticker", default="SPY")
    show_effective_config.add_argument("--start", default="2025-01-01", help="YYYY-MM-DD")
    show_effective_config.add_argument("--end", default="2025-01-31", help="YYYY-MM-DD")
    show_effective_config.add_argument("--or-width-min", type=float, default=None)
    show_effective_config.add_argument("--initial-equity", type=float, default=100000.0)
    show_effective_config.add_argument("--risk-per-trade", type=float, default=0.02)
    show_effective_config.add_argument("--max-trades-per-day", type=int, default=1)
    show_effective_config.add_argument("--json-indent", type=int, default=2)
    return parser


def _run_backtest_payload(args: argparse.Namespace) -> Dict[str, Any]:
    return run_default_backtest(
        start=_parse_date(args.start),
        end=_parse_date(args.end),
        ticker=str(args.ticker).strip().upper(),
        env_path=str(args.env_path),
        db_path=str(args.db_path).strip() or None,
        include_alpaca=bool(args.with_alpaca),
        or_width_min=args.or_width_min,
        initial_equity=float(args.initial_equity),
        risk_per_trade=float(args.risk_per_trade),
        max_trades_per_day=int(args.max_trades_per_day),
        return_trade_log=bool(args.return_trade_log),
    )


def _run_default_universe_payload(args: argparse.Namespace) -> Dict[str, Any]:
    return run_default_universe_backtests(
        start=_parse_date(args.start),
        end=_parse_date(args.end),
        env_path=str(args.env_path),
        db_path=str(args.db_path).strip() or None,
        include_alpaca=bool(args.with_alpaca),
        or_width_min=args.or_width_min,
        initial_equity=float(args.initial_equity),
        risk_per_trade=float(args.risk_per_trade),
        max_trades_per_day=int(args.max_trades_per_day),
        return_trade_log=bool(args.return_trade_log),
    )


def _effective_config_payload(args: argparse.Namespace) -> Dict[str, Any]:
    return build_effective_config_payload(
        start=_parse_date(args.start),
        end=_parse_date(args.end),
        ticker=str(args.ticker).strip().upper(),
        or_width_min=args.or_width_min,
        initial_equity=float(args.initial_equity),
        risk_per_trade=float(args.risk_per_trade),
        max_trades_per_day=int(args.max_trades_per_day),
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-model":
        print(json.dumps(build_default_model().to_dict(), indent=int(args.json_indent), sort_keys=True))
        return 0
    if args.command == "run-backtest":
        print(json.dumps(_run_backtest_payload(args), indent=int(args.json_indent), sort_keys=True, default=str))
        return 0
    if args.command == "run-default-universe":
        print(json.dumps(_run_default_universe_payload(args), indent=int(args.json_indent), sort_keys=True, default=str))
        return 0
    if args.command == "show-effective-config":
        print(json.dumps(_effective_config_payload(args), indent=int(args.json_indent), sort_keys=True, default=str))
        return 0
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
