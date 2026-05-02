"""Run the default model and export the trade log to CSV."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from cuteoptionstrats import run_default_backtest


def main() -> None:
    output_path = Path("trade_log.csv")
    result = run_default_backtest(
        start=datetime(2025, 1, 1),
        end=datetime(2025, 1, 31),
        ticker="SPY",
        env_path=".env",
        return_trade_log=True,
    )
    rows = list(result.get("trade_log") or [])
    if not rows:
        print("No trade_log rows were returned.")
        return

    fieldnames = sorted({str(key) for row in rows for key in row.keys()})
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})
    print({"rows": len(rows), "path": str(output_path)})


if __name__ == "__main__":
    main()
