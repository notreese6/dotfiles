#!/usr/bin/env bash
# ============================================================
# dev-layout.sh — build a pre-laid-out dev workspace in tmux.
#
#   Outside tmux: creates a new SESSION named $NAME and attaches.
#   Inside tmux:  creates a new WINDOW named $NAME and switches to it.
#
# Layout:
#   ┌──────────┬──────────────────────────────┐
#   │  term 1  │                              │
#   │          │           editor             │
#   ├──────────┤            (75%)             │
#   │  term 2  │                              │
#   │          ├──────────────────────────────┤
#   ├──────────┤                              │
#   │  term 3  │      runner (25%)            │
#   └──────────┴──────────────────────────────┘
#   ←  35%  →  ←           65%               →
#
# Usage:
#   dev-layout.sh                  # name = "dev",     cwd = $PWD
#   dev-layout.sh myproj           # name = "myproj",  cwd = $PWD
#   dev-layout.sh myproj ~/code/x  # name = "myproj",  cwd = ~/code/x
#
# Notes:
#   - When run from a shell, we pass the real terminal size to
#     `new-session -x/-y` so the detached session is built at the
#     correct dimensions instead of the 80x24 default.
#   - Splits use absolute cell counts (computed from the window's real
#     size), not percentages. Tmux's percentage handling on splits is
#     inconsistent across versions; absolute counts are reliable.
# ============================================================

set -euo pipefail

command -v tmux >/dev/null 2>&1 || {
  echo "dev-layout.sh: tmux not found on \$PATH" >&2
  exit 1
}

NAME="${1:-dev}"
PROJECT_DIR_RAW="${2:-$PWD}"

# '.' and ':' confuse tmux's target-spec parser.
case "$NAME" in
  *[.:]*|"")
    echo "dev-layout.sh: name must be non-empty and cannot contain '.' or ':' (got: '$NAME')" >&2
    exit 1
    ;;
esac

if [ ! -d "$PROJECT_DIR_RAW" ]; then
  echo "dev-layout.sh: directory not found: $PROJECT_DIR_RAW" >&2
  exit 1
fi
PROJECT_DIR="$(cd "$PROJECT_DIR_RAW" && pwd)"


# ---- Step 1: get a window to work in -----------------------

if [ -n "${TMUX:-}" ]; then
  # Already in tmux — open a new window in the current session.
  WINDOW_ID=$(tmux new-window -n "$NAME" -c "$PROJECT_DIR" \
                -P -F "#{window_id}")
else
  # If a session with this name exists, just attach (idempotent).
  if tmux has-session -t "=$NAME" 2>/dev/null; then
    tmux attach-session -t "$NAME"
    exit 0
  fi
  # Create a new session at the real terminal size.
  TTY_SIZE=$(stty size 2>/dev/null || echo "24 80")
  TTY_ROWS=$(echo "$TTY_SIZE" | awk '{print $1}')
  TTY_COLS=$(echo "$TTY_SIZE" | awk '{print $2}')
  WINDOW_ID=$(tmux new-session -d -s "$NAME" -n "$NAME" \
                -c "$PROJECT_DIR" \
                -x "$TTY_COLS" -y "$TTY_ROWS" \
                -P -F "#{window_id}")
fi


# ---- Step 2: compute target cell counts --------------------

# First (and only) pane in the new window — will become term 1.
TERM1=$(tmux list-panes -t "$WINDOW_ID" -F "#{pane_id}" | head -n 1)
tmux select-pane -t "$TERM1" -T "term 1"

WIN_W=$(tmux display-message -p -t "$TERM1" '#{window_width}')
WIN_H=$(tmux display-message -p -t "$TERM1" '#{window_height}')

# Splits collapse silently below this size.
if [ "$WIN_W" -lt 80 ] || [ "$WIN_H" -lt 20 ]; then
  echo "dev-layout.sh: window too small for layout (${WIN_W}x${WIN_H}, need >=80x20)" >&2
  tmux kill-window -t "$WINDOW_ID" 2>/dev/null || true
  exit 1
fi

LEFT_W=$(( WIN_W * 35 / 100 ))           # left column width
EDITOR_W=$(( WIN_W - LEFT_W - 1 ))       # right column (minus border)
TERM_H=$(( WIN_H / 3 ))                  # one third of the window height
RUNNER_H=$(( WIN_H * 25 / 100 ))         # runner ≈ 25% of window height


# ---- Step 3: build the splits ------------------------------

EDITOR=$(tmux split-window -h -l "$EDITOR_W" \
           -t "$TERM1" -c "$PROJECT_DIR" -P -F "#{pane_id}")
tmux select-pane -t "$EDITOR" -T "editor"

RUNNER=$(tmux split-window -v -l "$RUNNER_H" \
           -t "$EDITOR" -c "$PROJECT_DIR" -P -F "#{pane_id}")
tmux select-pane -t "$RUNNER" -T "runner"

# Below term 1 in the left column (will host term 2 + term 3).
LOWER_H=$(( WIN_H - TERM_H - 1 ))
TERM2=$(tmux split-window -v -l "$LOWER_H" \
          -t "$TERM1" -c "$PROJECT_DIR" -P -F "#{pane_id}")
tmux select-pane -t "$TERM2" -T "term 2"

TERM3=$(tmux split-window -v -l "$TERM_H" \
          -t "$TERM2" -c "$PROJECT_DIR" -P -F "#{pane_id}")
tmux select-pane -t "$TERM3" -T "term 3"


# ---- Step 4: focus the editor & surface the window ---------

tmux select-pane -t "$EDITOR"

if [ -n "${TMUX:-}" ]; then
  tmux select-window -t "$WINDOW_ID"
else
  tmux attach-session -t "$NAME"
fi
