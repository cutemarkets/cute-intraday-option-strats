"""Inspect the public model metadata and resolved profile fields."""

from __future__ import annotations

from pprint import pprint

from cuteoptionstrats import build_default_model, get_default_profile


def main() -> None:
    model = build_default_model()
    profile = get_default_profile()

    print("[model]")
    pprint(model.to_dict())
    print("[profile]")
    pprint(
        {
            "name": profile.name,
            "strategy_variant": profile.strategy_variant,
            "opening_range_minutes": profile.opening_range_minutes,
            "option_target_dte": profile.option_target_dte,
            "require_option_microstructure_filter": profile.require_option_microstructure_filter,
        }
    )


if __name__ == "__main__":
    main()
