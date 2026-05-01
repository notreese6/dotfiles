#!/usr/bin/env bash
# ============================================================
# install.sh — symlink dotfiles from this repo into $HOME.
# Idempotent. Anything it would overwrite is moved to
# ~/.dotfiles-backup/<timestamp>/ first.
#
# Usage:
#   ./install.sh              # install everything
#   ./install.sh tmux         # install only the tmux configs
#   ./install.sh --dry-run    # show what would happen, change nothing
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

for _cmd in git ln mkdir mv readlink date; do
  command -v "$_cmd" >/dev/null 2>&1 || {
    echo "install.sh: required command not found: $_cmd" >&2
    exit 1
  }
done
unset _cmd

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$HOME/.dotfiles-backup/$(date +%Y%m%d-%H%M%S)"

for _dir in tmux vim bash; do
  [ -d "$DOTFILES_DIR/$_dir" ] || {
    echo "install.sh: expected '$_dir/' next to install.sh — is the repo intact?" >&2
    echo "  DOTFILES_DIR=$DOTFILES_DIR" >&2
    exit 1
  }
done
unset _dir

DRY_RUN=false
TARGETS=()

# ---- Parse args ---------------------------------------------
for arg in "$@"; do
  case "$arg" in
    --dry-run|-n) DRY_RUN=true ;;
    -h|--help)    sed -n '2,12p' "$0"; exit 0 ;;
    *)            TARGETS+=("$arg") ;;
  esac
done

# Default to all known targets when none are specified.
if [ ${#TARGETS[@]} -eq 0 ]; then
  TARGETS=(tmux vim bash)
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

  # Back up anything in the way.
  if [ -e "$dst" ] || [ -L "$dst" ]; then
    if $DRY_RUN; then
      warn "would back up $dst -> $BACKUP_DIR/"
    else
      mkdir -p "$BACKUP_DIR" && mv "$dst" "$BACKUP_DIR/"
      warn "backed up existing $dst -> $BACKUP_DIR/"
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


# ---- Dispatcher ---------------------------------------------
for target in "${TARGETS[@]}"; do
  case "$target" in
    tmux)  install_tmux ;;
    vim)   install_vim ;;
    bash)  install_bash ;;
    *)     err "unknown target: $target"; err "known: tmux vim bash"; exit 1 ;;
  esac
done

echo
if $DRY_RUN; then
  info "Dry run complete — nothing was changed."
else
  info "Done. Backups (if any): $BACKUP_DIR"
  echo
  echo "Next steps:"
  echo "  - Open tmux and press 'prefix + I' to install plugins"
  echo "  - Reload an existing tmux session with 'prefix + r'"
fi
