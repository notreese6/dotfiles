#!/usr/bin/env bash
# ============================================================
# clip.sh — cross-platform "send stdin to the system clipboard".
# Used by ~/.tmux.conf bindings so copy-mode yanks work the same
# on macOS and Linux. Falls back to a no-op if no tool is found,
# so tmux never errors out.
#
#   pbcopy            macOS
#   wl-copy           Wayland (modern Linux desktops)
#   xclip / xsel      X11 (everything else on Linux)
# ============================================================

if   command -v pbcopy  >/dev/null 2>&1; then exec pbcopy
elif [ -n "${WAYLAND_DISPLAY:-}" ] && command -v wl-copy >/dev/null 2>&1; then
  exec wl-copy
elif command -v xclip   >/dev/null 2>&1; then exec xclip -selection clipboard -in
elif command -v xsel    >/dev/null 2>&1; then exec xsel  --clipboard --input
else
  cat >/dev/null   # silently swallow if no clipboard tool is available
fi
