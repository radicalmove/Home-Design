# Agent Instructions

Follow `VISUAL_QA.md` for any visual app change.

This includes 2D plans, future design scenarios, transitions, furniture symbols, furniture placement, labels, dimensions, sunlight, 3D navigation, design-review graphics, and visible CSS/layout changes.

Do not rely only on coordinate tests, source tests, or successful builds for visual work. Before claiming a visual change is complete, render or open the affected view, inspect the changed area and nearby context, compare it to Design 1 or the relevant reference, and report the visual QA evidence in the final response.

When changing plan geometry, prefer relationship tests over isolated coordinate assertions. Examples: wall A aligns with wall B, a window uses the same style as Design 1 exterior windows, a removed wall has matching floor continuity, or furniture remains inside the proposed room envelope.
