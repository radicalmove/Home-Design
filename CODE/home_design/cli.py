from __future__ import annotations

import argparse

from .model import load_model
from .validate import validate_model


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Home design model tools")
    parser.add_argument(
        "command",
        choices=[
            "validate",
            "render",
            "overlay",
            "report",
            "viewer",
            "presentation",
            "editor",
            "base-plan",
            "reference-plan",
            "house-3d",
        ],
    )
    parser.add_argument("--model", default="DATA/house_model.json")
    parser.add_argument("--output", default="OUTPUT/current_baseline.svg")
    parser.add_argument("--season", default=None)
    parser.add_argument("--time-band", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    model = load_model(args.model)
    result = validate_model(model)
    for warning in result.warnings:
        print(f"warning: {warning}")
    for error in result.errors:
        print(f"error: {error}")
    if not result.ok:
        return 1
    if args.command == "render":
        from .render_svg import render_baseline_svg, write_svg

        svg = render_baseline_svg(model, season=args.season, time_band=args.time_band)
        write_svg(args.output, svg)
        print(f"wrote {args.output}")
    elif args.command == "overlay":
        from .render_svg import render_overlay_svg, write_svg

        svg = render_overlay_svg(model)
        write_svg(args.output, svg)
        print(f"wrote {args.output}")
    elif args.command == "report":
        from pathlib import Path

        from .report import render_calibration_report

        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_calibration_report(model))
        print(f"wrote {args.output}")
    elif args.command == "viewer":
        from pathlib import Path

        from .viewer import render_calibration_viewer_html

        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_calibration_viewer_html(model))
        print(f"wrote {args.output}")
    elif args.command == "presentation":
        from pathlib import Path

        from .presentation_plan import render_presentation_plan_svg
        from .presentation_viewer import render_presentation_plan_html

        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.suffix.lower() == ".svg":
            output.write_text(render_presentation_plan_svg(model))
        else:
            output.write_text(render_presentation_plan_html(model))
        print(f"wrote {args.output}")
    elif args.command == "editor":
        from pathlib import Path

        from .scenario_editor import render_scenario_editor_html

        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_scenario_editor_html(model))
        print(f"wrote {args.output}")
    elif args.command == "base-plan":
        from pathlib import Path

        from .base_plan_viewer import render_base_plan_viewer_html

        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_base_plan_viewer_html(model))
        print(f"wrote {args.output}")
    elif args.command == "reference-plan":
        from pathlib import Path

        from .reference_plan import render_reference_plan_svg
        from .reference_plan_viewer import render_reference_plan_html

        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.suffix.lower() == ".svg":
            output.write_text(render_reference_plan_svg(model))
        else:
            output.write_text(render_reference_plan_html(model))
        print(f"wrote {args.output}")
    elif args.command == "house-3d":
        from pathlib import Path

        from .three_d_viewer import render_house_3d_html

        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_house_3d_html(model))
        print(f"wrote {args.output}")
    else:
        print("model valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
