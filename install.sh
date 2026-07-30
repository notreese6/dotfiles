#!/usr/bin/env bash
# ============================================================
# install.sh — symlink dotfiles from this repo into $HOME.
# Idempotent. Anything it would overwrite is moved to
# ~/.dotfiles-backup/<timestamp>/ first.
#
# Usage:
#   ./install.sh              # install everything
#   ./install.sh vim ai       # install only these targets
#   ./install.sh --dry-run    # show what would happen, change nothing
#   ./install.sh --yes        # don't ask before replacing existing files
#
# Targets: tmux vim bash ai
#   ai also runs ai-setup, which prompts for the private local-rules
#   remote, the agents to write rules for, and the daily-notes path.
#
# Anything of yours that would be replaced is moved to
# ~/.dotfiles-backup/<timestamp>/ first, and an interactive run asks
# before touching each one. Answer n to keep what you have and skip it.
# ============================================================

# ---- Pre-flight ---------------------------------------------

if [ -z "${BASH_VERSION:-}" ]; then
  echo "install.sh: must be run with bash (try: ./install.sh)" >&2
  exit 1
fi

# Floor is 3.2 (macOS system bash).
if [ "${BASH_VERSINFO[0]}" -lt 3 ] \
   || { [ "${BASH_VERSINFO[0]}" -eq 3 ] && [ "${BASH_VERSINFO[1]}" -lt 2 ]; }; then
  echo "install.sh: bash >= 3.2 required (you have $BASH_VERSION)" >&2
  exit 1
fi

set -euo pipefail

if [ "$(id -u)" = 0 ]; then
  echo "install.sh: refusing to run as root. Run as your normal user." >&2
  exit 1
fi

if [ ! -w "$HOME" ]; then
  echo "install.sh: \$HOME ($HOME) is not writable" >&2
  exit 1
fi

for _cmd in git ln mkdir mv readlink date find wc; do
  command -v "$_cmd" >/dev/null 2>&1 || {
    echo "install.sh: required command not found: $_cmd" >&2
    exit 1
  }
done
unset _cmd

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for _dir in tmux vim bash ai; do
  [ -d "$DOTFILES_DIR/$_dir" ] || {
    echo "install.sh: expected '$_dir/' next to install.sh — is the repo intact?" >&2
    echo "  DOTFILES_DIR=$DOTFILES_DIR" >&2
    exit 1
  }
done
unset _dir

DRY_RUN=false
ASSUME_YES=false
TARGETS=()

# Counts files moved aside, so the closing summary can name the backup directory
# only when something is actually in it. The old line printed the path every
# time, including on runs that never created it.
BACKED_UP=0

# ---- Parse args ---------------------------------------------
for arg in "$@"; do
  case "$arg" in
    --dry-run|-n) DRY_RUN=true ;;
    --yes|-y)     ASSUME_YES=true ;;
    # Printed to the closing banner rather than to a fixed line number, which
    # silently truncated the help the moment the header above grew a line.
    -h|--help)    sed -n '2,/^# =\{10,\}$/p' "$0"; exit 0 ;;
    *)            TARGETS+=("$arg") ;;
  esac
done

# Default to all known targets when none are specified.
if [ ${#TARGETS[@]} -eq 0 ]; then
  TARGETS=(tmux vim bash ai)
fi


# ---- Output helpers -----------------------------------------
if [ -t 1 ]; then
  c_blue=$'\033[1;34m'; c_green=$'\033[1;32m'
  c_yellow=$'\033[1;33m'; c_red=$'\033[1;31m'; c_reset=$'\033[0m'
else
  c_blue=""; c_green=""; c_yellow=""; c_red=""; c_reset=""
fi
info() { echo "${c_blue}==>${c_reset} $*"; }
ok()   { echo "  ${c_green}✓${c_reset} $*"; }
warn() { echo "  ${c_yellow}!${c_reset} $*"; }
err()  { echo "  ${c_red}✗${c_reset} $*" >&2; }


# ---- Backup location ----------------------------------------
# Settled before any target runs, because every target can displace files and one
# answer has to hold for all of them. On a machine that has never run ai-setup
# there is no config to read, so this is where the value first gets chosen —
# resolving it lazily meant the answer only took effect on the NEXT install.
configured_backup_root() {
  python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import airules
print(airules.Config.load().backup_dir or "")' "$DOTFILES_DIR/ai/lib" 2>/dev/null || echo ""
}

# An explicit AI_SETUP_BACKUP_DIR wins: a caller that named a location meant it.
BACKUP_ROOT="${AI_SETUP_BACKUP_DIR:-}"

if [ -z "$BACKUP_ROOT" ]; then
  BACKUP_ROOT="$(configured_backup_root)"
fi

if [ -z "$BACKUP_ROOT" ]; then
  BACKUP_ROOT="$HOME/.dotfiles-backup"

  # Only worth asking when there is someone to answer and nothing is configured.
  if ! $DRY_RUN && ! $ASSUME_YES && [ -t 0 ]; then
    printf "  %s?%s backup directory for anything replaced [%s] " \
      "$c_yellow" "$c_reset" "$BACKUP_ROOT" >&2
    if read -r reply && [ -n "$reply" ]; then
      # Expand a leading ~, then anchor anything still relative to $HOME. A bare
      # word would otherwise be relative to wherever install.sh was run from,
      # scattering backups into the repo or the current directory.
      reply="${reply/#\~/$HOME}"
      case "$reply" in
        /*) BACKUP_ROOT="$reply" ;;
        *)  BACKUP_ROOT="$HOME/$reply" ;;
      esac
    fi
  fi
fi

BACKUP_DIR="$BACKUP_ROOT/$(date +%Y%m%d-%H%M%S)"

# ai-setup records the root so the choice survives to the next run; ai-rules
# files into this run's directory rather than starting one of its own.
export AI_SETUP_BACKUP_DIR="$BACKUP_ROOT"
export DOTFILES_BACKUP_DIR="$BACKUP_DIR"


# ---- confirm_replace: ask before clobbering an existing file -
# Returns 0 to go ahead, 1 to keep what is there. Auto-yes when --yes was
# given or stdin is not a terminal, so provisioning and CI behave as before;
# an interactive run is the only one that stops to ask.
confirm_replace() {
  local dst="$1" reply

  $ASSUME_YES && return 0
  [ -t 0 ] || return 0

  printf "  %s?%s replace %s — a copy goes to %s/ [y/N] " \
    "$c_yellow" "$c_reset" "$dst" "$BACKUP_DIR" >&2
  read -r reply || return 1

  case "$reply" in
    [yY]|[yY][eE][sS]) return 0 ;;
    *)                 return 1 ;;
  esac
}


# ---- link: symlink $1 -> $2 (with backup if needed) ---------
link() {
  local src="$1" dst="${2/#\~/$HOME}"

  [ -e "$src" ] || { err "missing source: $src"; return 1; }

  # Already correctly linked? Nothing to do.
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    ok "already linked: $dst"
    return 0
  fi

  $DRY_RUN || mkdir -p "$(dirname "$dst")"

  # Back up anything in the way — and ask first, since anything reached here is
  # a file the user wrote themselves, not one of ours from an earlier run.
  if [ -e "$dst" ] || [ -L "$dst" ]; then
    if $DRY_RUN; then
      warn "would move your $dst -> $BACKUP_DIR/${dst#"$HOME"/}"
      BACKED_UP=$((BACKED_UP + 1))
    elif ! confirm_replace "$dst"; then
      warn "kept your existing $dst — skipped"
      return 0
    else
      # Mirror the path under $HOME rather than flattening to the basename, so
      # two files that share a name cannot overwrite each other in here and it
      # stays obvious where each one came from.
      local kept="$BACKUP_DIR/${dst#"$HOME"/}"
      mkdir -p "$(dirname "$kept")" && mv "$dst" "$kept"
      BACKED_UP=$((BACKED_UP + 1))
      warn "moved your $dst -> $kept"
    fi
  fi

  if $DRY_RUN; then
    ok "would link $dst -> $src"
  else
    ln -s "$src" "$dst"
    ok "linked $dst -> $src"
  fi
}


# ---- Per-tool install steps ---------------------------------
# To add a new tool: write install_<tool>(), add a case to the
# dispatcher, and add it to the default TARGETS list above.

install_tmux() {
  info "Installing tmux config"
  link "$DOTFILES_DIR/tmux/tmux.conf"             "$HOME/.tmux.conf"
  link "$DOTFILES_DIR/tmux/scripts/dev-layout.sh" "$HOME/.tmux/scripts/dev-layout.sh"
  link "$DOTFILES_DIR/tmux/scripts/clip.sh"       "$HOME/.tmux/scripts/clip.sh"

  # TPM (tmux plugin manager) lives at ~/.tmux/plugins/tpm.
  if [ ! -d "$HOME/.tmux/plugins/tpm" ]; then
    if $DRY_RUN; then
      warn "would clone TPM into ~/.tmux/plugins/tpm"
    else
      info "Cloning TPM into ~/.tmux/plugins/tpm"
      git clone https://github.com/tmux-plugins/tpm "$HOME/.tmux/plugins/tpm"
    fi
  else
    ok "TPM already present"
  fi
}

install_vim() {
  info "Installing vim config"
  link "$DOTFILES_DIR/vim/vimrc" "$HOME/.vimrc"
}

install_bash() {
  info "Installing bash config"
  link "$DOTFILES_DIR/bash/bashrc"       "$HOME/.bashrc"
  link "$DOTFILES_DIR/bash/bash_profile" "$HOME/.bash_profile"
}

install_ai() {
  info "Installing AI rules + tooling"
  link "$DOTFILES_DIR/ai/bin/ai-rules" "$HOME/.local/bin/ai-rules"
  link "$DOTFILES_DIR/ai/bin/ai-setup" "$HOME/.local/bin/ai-setup"

  if $DRY_RUN; then
    warn "would run ai-setup (prompts for local-rules remote, agents, notes path)"
    return 0
  fi

  info "Running ai-setup"

  # `set -e` at the top already aborts on a failure here, so this is not about
  # the exit status — it is about saying why. ai-setup exits non-zero
  # deliberately (a backup it will not destroy, a remote it could not clone),
  # and bare errexit would end the run with no summary line, leaving its last
  # message looking like one more note rather than the reason nothing installed.
  # Testing the command in a condition also suspends errexit, so the message
  # gets printed instead of the shell exiting first.
  if ! "$DOTFILES_DIR/ai/bin/ai-setup"; then
    err "ai-setup did not finish; no rules were written"
    exit 1
  fi
}


# ---- Announce the plan --------------------------------------
# Names the targets rather than their files: --dry-run already lists every path
# exactly, and repeating the list here is a second copy that would drift.
info "Installing: ${TARGETS[*]}"
echo "  Pick a subset by naming it (e.g. ./install.sh vim ai), or see every file first with --dry-run."
$ASSUME_YES && warn "--yes: replacing existing files without asking (originals still go to $BACKUP_DIR/)"
echo


# ---- Dispatcher ---------------------------------------------
for target in "${TARGETS[@]}"; do
  case "$target" in
    tmux)  install_tmux ;;
    vim)   install_vim ;;
    bash)  install_bash ;;
    ai)    install_ai ;;
    *)     err "unknown target: $target"; err "known: tmux vim bash ai"; exit 1 ;;
  esac
done

echo
if $DRY_RUN; then
  info "Dry run complete — nothing was changed."
  if [ "$BACKED_UP" -gt 0 ]; then
    info "$BACKED_UP existing file(s) of yours would be moved to $BACKUP_DIR/"
  fi
else
  # Counted from the directory rather than from BACKED_UP: ai-rules runs as a
  # child process and files its own backups in here too, so a counter kept in
  # this shell under-reports every run that installs the ai target.
  kept=0
  if [ -d "$BACKUP_DIR" ]; then
    kept=$(find "$BACKUP_DIR" -type f | wc -l | tr -d ' ')
  fi

  if [ "$kept" -gt 0 ]; then
    info "Done. $kept file(s) of yours were moved to $BACKUP_DIR/"
  else
    info "Done. Nothing of yours was replaced, so no backup was needed."
  fi
  echo
  echo "Next steps:"
  echo "  - Open tmux and press 'prefix + I' to install plugins"
  echo "  - Reload an existing tmux session with 'prefix + r'"
fi
