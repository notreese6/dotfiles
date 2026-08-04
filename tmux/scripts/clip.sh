#!/usr/bin/env bash
# ============================================================
# clip.sh — cross-platform "send stdin to the system clipboard".
# Used by ~/.tmux.conf bindings and vim/vimrc so copy behaves
# the same on macOS, Linux, and over SSH.
#
#   pbcopy            macOS
#   wl-copy           Wayland (modern Linux desktops)
#   xclip / xsel      X11 (everything else on Linux)
#   OSC 52            over SSH — see below
#
# Over SSH this emits an OSC 52 escape sequence. Terminal.app
# does NOT implement OSC 52, so the local end of the connection
# must be wrapped in bash/osc52-shim, which intercepts the
# sequence and calls pbcopy on the Mac. Use `sshc host`, not
# plain `ssh host`, or the copy goes nowhere.
# ============================================================

osc52() {
    # Hand stdin to the terminal (or to osc52-shim) as an OSC 52 escape sequence.
    #
    # The far end of the connection owns the clipboard worth writing to, and this
    # is only bytes on the wire, so it survives ssh, tmux, and nesting.
    #
    # Args:
    #     None. Reads the payload from stdin.
    #
    # Returns:
    #     Nothing on stdout. Writes the escape sequence to the controlling
    #     terminal, falling back to stdout when there is no writable /dev/tty
    #     (tmux run-shell, cron, and anything else detached from a terminal).
    #
    # Raises:
    #     None. Clipboard failures must never break the pipeline that calls this.

    local payload

    # macOS base64 has no -w0, so strip the wrapping newlines instead of
    # suppressing them — the sequence must be a single unbroken line.
    payload=$(base64 | tr -d '\n')

    if [ -w /dev/tty ]; then
        printf '\033]52;c;%s\007' "$payload" > /dev/tty
    else
        printf '\033]52;c;%s\007' "$payload"
    fi
}

# Over SSH the clipboard worth writing to belongs to whichever machine is running
# the terminal, NOT this one — so OSC 52 wins even where pbcopy or xclip exist
# here, because those would silently fill a clipboard nobody is looking at.
if   [ -n "${SSH_CONNECTION:-}${SSH_TTY:-}" ]; then osc52
elif command -v pbcopy  >/dev/null 2>&1; then exec pbcopy
elif [ -n "${WAYLAND_DISPLAY:-}" ] && command -v wl-copy >/dev/null 2>&1; then
  exec wl-copy
# Guarded on DISPLAY because a headless box often still HAS xclip installed,
# and running it with no display hangs or errors instead of copying — which
# would look like the copy worked right up until the paste.
elif [ -n "${DISPLAY:-}" ] && command -v xclip >/dev/null 2>&1; then
  exec xclip -selection clipboard -in
elif [ -n "${DISPLAY:-}" ] && command -v xsel  >/dev/null 2>&1; then
  exec xsel --clipboard --input
else
  # Drain stdin before complaining: the caller is piping into us and would take
  # SIGPIPE if we exited without reading, turning a clipboard miss into a broken
  # pipe in whatever called us.
  cat >/dev/null

  # Say so on stderr and exit non-zero. A copy that disappears quietly is worse
  # than one that fails, because the only symptom is a paste that produces
  # something stale — long after the context that would explain it is gone.
  printf '[-] clip.sh: no clipboard on %s — copy discarded (no pbcopy/wl-copy, and no DISPLAY for xclip/xsel)\n' \
         "$(hostname -s 2>/dev/null || echo 'this host')" >&2
  exit 1
fi
