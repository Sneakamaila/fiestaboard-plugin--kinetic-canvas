#!/usr/bin/env python3
"""Interactive terminal visualizer and acoustic simulator for Kinetic Canvas."""

from __future__ import annotations
import argparse
import sys
import time

from plugins.kinetic_canvas import KineticCanvasPlugin

# ANSI 24-bit TrueColor tile representations
ANSI_COLORS = {
    0: "\033[48;2;18;18;18m  \033[0m",      # Blank (Deep charcoal)
    63: "\033[48;2;225;35;35m  \033[0m",    # Poppy Red
    64: "\033[48;2;255;120;0m  \033[0m",    # Orange
    65: "\033[48;2;255;210;0m  \033[0m",    # Yellow
    66: "\033[48;2;0;190;80m  \033[0m",     # Green
    67: "\033[48;2;20;120;255m  \033[0m",   # Blue
    68: "\033[48;2;160;50;220m  \033[0m",   # Violet
    69: "\033[48;2;240;240;240m  \033[0m",  # White
    70: "\033[48;2;30;30;30m  \033[0m",     # Black
}


def render_terminal_matrix(matrix: list[list[int]], label: str) -> None:
    width = len(matrix[0]) if matrix else 0
    height = len(matrix)

    print(f"\n┌── {label} ({width}x{height}) " + "─" * max(0, (width * 2 - len(label) - 12)) + "┐")
    for row in matrix:
        line_str = "│"
        for code in row:
            if code in ANSI_COLORS:
                line_str += ANSI_COLORS[code]
            elif 1 <= code <= 26:
                char = chr(ord("A") + code - 1)
                line_str += f"\033[38;2;230;230;230m\033[48;2;30;30;30m {char}\033[0m"
            else:
                line_str += "  "
        line_str += "│"
        print(line_str)
    print("└──" + "─" * (width * 2 + 1) + "┘")


def main():
    parser = argparse.ArgumentParser(description="Preview Kinetic Canvas art and sound transitions.")
    parser.add_argument(
        "--mode",
        choices=[
            "cycle",
            "zen_snap",
            "zen_wave",
            "zen_rain",
            "zen_gong",
            "mondrian",
            "game_of_life",
            "wolfram",
            "weather",
            "zen_chime",
        ],
        default="cycle",
        help="Art and acoustic mode to preview (default: cycle)",
    )
    parser.add_argument(
        "--chime-style",
        choices=["staccato_snap", "acoustic_wave", "rainfall", "harmonic_decay"],
        default="staccato_snap",
        help="Specific chime envelope when using zen_chime",
    )
    parser.add_argument("--steps", type=int, default=3, help="Number of consecutive transitions to preview")
    parser.add_argument("--rule", type=int, default=30, help="Wolfram rule number (30, 90, 110, 184)")
    args = parser.parse_args()

    # Load manifest
    manifest = {"id": "kinetic_canvas", "name": "Kinetic Canvas"}
    plugin = KineticCanvasPlugin(manifest)
    plugin.config = {
        "mode": args.mode,
        "chime_style": args.chime_style,
        "wolfram_rule": args.rule,
        "demo_mode": True,
    }

    print("=" * 60)
    print("🎨 FIESTABOARD KINETIC CANVAS & ACOUSTIC SIMULATOR 🔊")
    print(f"Mode: {args.mode.upper()} | Steps: {args.steps}")
    print("=" * 60)

    for step in range(1, args.steps + 1):
        print(f"\n>>> [TRANSITION {step}/{args.steps}] <<<")
        result = plugin.fetch_data()

        if not result.available or not result.data:
            print(f"Error: {result.error}")
            return

        data = result.data
        print(f"📌 Titel:    {data['title']}")
        print(f"📖 Stil:     {data['mode']} — {data['description']}")
        print(f"🔊 Akustik:  {data['sound_profile']} ({data['total_clicks']} Klicks, {data['moving_modules']} bewegte Module, Dauer: {data['duration_sec']})")
        print(f"📊 Partitur: [{data['acoustic_sparkline']}] {data['acoustic_description']}")

        # Render Flagship & Note visually
        state = plugin.state_manager.load()
        f_matrix = state.get("previous_flagship", [])
        n_matrix = state.get("previous_note", [])

        if f_matrix:
            render_terminal_matrix(f_matrix, "VESTABOARD FLAGSHIP")
        if n_matrix:
            render_terminal_matrix(n_matrix, "VESTABOARD NOTE")

        if step < args.steps:
            time.sleep(0.5)


if __name__ == "__main__":
    main()
