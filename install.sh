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

# Naming targets on the command line is itself an answer, so the per-target
# question is skipped: `./install.sh vim` has already said which one you want.
EXPLICIT_TARGETS=true

# Set per target by want_target when it asked and was told yes. Suppresses the
# per-file prompt for that target only; a run that names its targets on the
# command line never sets it, so those files are still confirmed one by one.
#
# The reset before each target cannot currently be observed: EXPLICIT_TARGETS is
# fixed for a whole run, so either every target is asked (and sets this itself)
# or none is. It stays because that reasoning is about today's control flow, and
# a target installed without passing through want_target would silently inherit
# the previous one's consent.
TARGET_CONFIRMED=false

# Set when the tmux target actually runs, so the closing tmux hint is only shown
# to someone who has a tmux config from here to reload.
INSTALLED_TMUX=

# Default to all known targets when none are specified.
if [ ${#TARGETS[@]} -eq 0 ]; then
  TARGETS=(tmux vim bash ai)
  EXPLICIT_TARGETS=false
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

  # The per-target question already named this exact file and was answered yes.
  # Asking again per file is the same consent collected twice, and a second
  # prompt that always follows the first is one people learn to mash through.
  $TARGET_CONFIRMED && return 0

  printf "  %s?%s replace %s — a copy goes to %s/ [y/N] " \
    "$c_yellow" "$c_reset" "$dst" "$BACKUP_DIR" >&2
  read -r reply || return 1

  case "$reply" in
    [yY]|[yY][eE][sS]) return 0 ;;
    *)                 return 1 ;;
  esac
}


# ---- would_replace: files a target clobbers that are not ours -
# Echoes one destination per line: those that exist and are not already the
# symlink we would create. A path we already own is not a loss, and listing it
# would pad the warning until nobody reads it.
#
# Args: $1 target name.
# Prints: zero or more paths.
would_replace() {
  local src dst

  while IFS='|' read -r src dst <&3; do
    [ -n "$dst" ] || continue
    # -e is false for a broken symlink, so -L too: a dangling link is still
    # something of the user's that we are about to overwrite.
    if [ -e "$dst" ] || [ -L "$dst" ]; then
      [ "$(resolve_link "$dst")" = "$(physical_path "$src")" ] || echo "$dst"
    fi
  done 3<<EOF
$(links_for "$1")
EOF
}


# ---- already_ours: is this target fully installed already? ---
# True when every destination exists and already points where we would point
# it. Distinct from would_replace being empty, which is also true when the
# files simply are not there — "nothing of yours is there to replace" reads as
# "the file does not exist", and saying that about a working symlink is wrong.
#
# Args: $1 target name.
# Returns: 0 when every destination is already our link, 1 otherwise
#          (including a target with no destinations at all).
already_ours() {
  local src dst total=0 ours=0

  while IFS='|' read -r src dst <&3; do
    [ -n "$dst" ] || continue
    total=$((total + 1))
    [ "$(resolve_link "$dst")" = "$(physical_path "$src")" ] && ours=$((ours + 1))
  done 3<<EOF
$(links_for "$1")
EOF

  [ "$total" -gt 0 ] && [ "$ours" -eq "$total" ]
}


# ---- resolve_link: where a symlink points, or "" ------------
# `readlink -f` is GNU-only, so this reads the one hop we care about and
# normalises it, because the two sides of the comparison can spell the same
# file differently: on macOS /var is itself a symlink to /private/var, so a link
# recorded as one and a source computed as the other never match as strings, and
# a file we already own would be reported as one about to be lost.
#
# Args: $1 a path.
# Prints: the link target for a symlink with its directory resolved, otherwise
#         nothing.
resolve_link() {
  [ -L "$1" ] || return 0

  physical_path "$(readlink "$1")"
}


# ---- physical_path: a path with its directory resolved -------
# Only the directory is resolved. Resolving the leaf too would follow the very
# link being compared and make everything look identical to itself.
#
# Args: $1 a path.
# Prints: the same path with symlinked parents collapsed, or unchanged when the
#         parent does not exist.
physical_path() {
  local parent leaf

  parent="$(dirname "$1")"
  leaf="$(basename "$1")"

  [ -d "$parent" ] || { echo "$1"; return 0; }

  echo "$(cd "$parent" && pwd -P)/$leaf"
}


# ---- describes_target: what a target actually does to you ----
# "install tmux" is not what any of these do — tmux is already installed or it
# is not, and nothing here changes that. What they do is put notreese's config
# where yours is. The prompt says so.
#
# Args: $1 target name.
# Prints: a one-line description, or the bare name for an unknown target.
describes_target() {
  case "$1" in
    tmux) echo "replace your tmux config with this repo's" ;;
    vim)  echo "replace your vim config with this repo's" ;;
    bash) echo "replace your bash config with this repo's" ;;
    ai)   echo "install three commands: ai-rules and ai-setup (build the rules your AI agents read) and daily-notes-sync (keeps ~/daily-notes in step across machines)" ;;
    *)    echo "$1" ;;
  esac
}


# ---- personal_target: is this notreese's own config? --------
# The three dotfile targets are notreese's own preferences and are off unless
# asked for, the same way the misc rules module is: taking them replaces what
# you already use, and a default that costs the reader something should be the
# one they have to choose. The ai target only links three commands into
# ~/.local/bin and asks its own questions before touching a rules file, so it is
# the one that defaults on.
#
# Args: $1 target name.
# Returns: 0 when it is somebody's personal config, 1 otherwise.
personal_target() {
  case "$1" in
    tmux|vim|bash) return 0 ;;
    *)             return 1 ;;
  esac
}


# ---- want_target: ask whether to install one target ----------
# Names the files it would replace first, then asks. Answering no skips the
# target entirely, so nothing of the user's is touched.
#
# Args: $1 target name.
# Returns: 0 to install, 1 to skip.
want_target() {
  local target="$1" default reply clobbers

  default="$(configured_target "$target")"

  # Never answered before: notreese's config is off unless asked for.
  if [ -z "$default" ] && personal_target "$target"; then
    default=false
  fi

  # --yes is consent to everything, and naming a target on the command line is
  # consent to that one: `./install.sh vim` has already answered this question.
  # Neither may be overridden by the off-by-default rule, or the only ways to
  # ask for these on purpose would both silently do nothing.
  if $ASSUME_YES || $EXPLICIT_TARGETS; then
    return 0
  fi

  # Nobody to ask. A stored answer decides; without one, somebody's personal
  # config is not installed over yours by a run that could not ask — that is
  # exactly the unattended case where nobody would see it happen.
  if [ ! -t 0 ]; then
    [ "$default" = "false" ] && return 1
    return 0
  fi

  clobbers="$(would_replace "$target")"
  printf "\n" >&2
  if [ -n "$clobbers" ]; then
    warn "$(describes_target "$target") — these are YOURS and get replaced:"
    printf "%s\n" "$clobbers" | sed "s|^$HOME|~|; s|^|      |" >&2
    echo "      (a copy of each goes to $BACKUP_DIR/)" >&2
  elif already_ours "$target"; then
    info "$(describes_target "$target") — already installed from this repo, so this changes nothing"
  else
    # Deliberately about risk, not presence. This branch also covers a target
    # that is partly installed — some files ours, some absent — where claiming
    # "you have no $target config" would be plainly untrue.
    info "$(describes_target "$target") — nothing of yours would be replaced"
  fi

  if [ "$default" = "false" ]; then
    printf "  %s?%s %s [y/N] " "$c_yellow" "$c_reset" "$target" >&2
    read -r reply || return 1
    case "$reply" in
      [yY]|[yY][eE][sS]) TARGET_CONFIRMED=true; return 0 ;;
      *)                 return 1 ;;
    esac
  fi

  printf "  %s?%s %s [Y/n] " "$c_yellow" "$c_reset" "$target" >&2
  read -r reply || { TARGET_CONFIRMED=true; return 0; }
  case "$reply" in
    [nN]|[nN][oO]) return 1 ;;
    *)             TARGET_CONFIRMED=true; return 0 ;;
  esac
}


# ---- configured_target / remember_target ---------------------
# The answers live in the same machine-local JSON config the AI tools use, so a
# re-run pre-fills with what was chosen last time rather than asking cold. Read
# and written through airules, which owns that file's shape; nothing here parses
# JSON in bash.
#
# Args: $1 target name (and $2 "true"/"false" for remember_target).
# Prints: configured_target echoes "true", "false", or "" when never answered.
configured_target() {
  python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import airules
answered = airules.Config.load().targets.get(sys.argv[2])
print("" if answered is None else str(answered).lower())' "$DOTFILES_DIR/ai/lib" "$1" 2>/dev/null || echo ""
}

remember_target() {
  python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import airules
config = airules.Config.load()
config.targets[sys.argv[2]] = sys.argv[3] == "true"
config.save()' "$DOTFILES_DIR/ai/lib" "$1" "$2" 2>/dev/null || true
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

# ---- links_for: the src|dst pairs one target installs ---------
# Echoes one "source|destination" per line. Every target's file list lives here
# and nowhere else, so the installer and the announcement that says what will be
# replaced cannot drift apart — a list that only the installer knew would let
# the warning quietly stop naming a file it still clobbers.
#
# Args: $1 target name.
# Prints: zero or more "src|dst" lines. Nothing for an unknown target.
links_for() {
  case "$1" in
    tmux)
      echo "$DOTFILES_DIR/tmux/tmux.conf|$HOME/.tmux.conf"
      echo "$DOTFILES_DIR/tmux/scripts/dev-layout.sh|$HOME/.tmux/scripts/dev-layout.sh"
      echo "$DOTFILES_DIR/tmux/scripts/clip.sh|$HOME/.tmux/scripts/clip.sh"
      ;;
    vim)
      echo "$DOTFILES_DIR/vim/vimrc|$HOME/.vimrc"
      ;;
    bash)
      echo "$DOTFILES_DIR/bash/bashrc|$HOME/.bashrc"
      echo "$DOTFILES_DIR/bash/bash_profile|$HOME/.bash_profile"
      echo "$DOTFILES_DIR/bash/osc52-shim|$HOME/.local/bin/osc52-shim"
      ;;
    ai)
      echo "$DOTFILES_DIR/ai/bin/ai-rules|$HOME/.local/bin/ai-rules"
      echo "$DOTFILES_DIR/ai/bin/ai-setup|$HOME/.local/bin/ai-setup"
      echo "$DOTFILES_DIR/ai/bin/daily-notes-sync|$HOME/.local/bin/daily-notes-sync"
      ;;
  esac
}


# ---- link_all: install every file a target owns --------------
# Args: $1 target name.
link_all() {
  local src dst

  # The list is read on fd 3, not through a pipe. A pipeline would run this loop
  # in a subshell with stdin bound to the pipe, so confirm_replace's `[ -t 0 ]`
  # would see "not a terminal" and auto-approve every replacement without ever
  # asking — silently clobbering files the prompt exists to protect.
  #
  # IFS split on | rather than word-splitting, so a path containing a space
  # stays one argument.
  while IFS='|' read -r src dst <&3; do
    [ -n "$src" ] && link "$src" "$dst"
  done 3<<EOF
$(links_for "$1")
EOF
}


install_tmux() {
  info "Installing tmux config"
  link_all tmux

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
  link_all vim
}

install_bash() {
  info "Installing bash config"
  link_all bash
}

install_ai() {
  info "Installing AI rules + tooling"
  link_all ai

  if $DRY_RUN; then
    warn "would run ai-setup (prompts for local-rules remote, agents, rule modules, notes path and remote)"
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
info "Targets: ${TARGETS[*]}"
echo "  These are notreese's dotfiles. tmux, vim and bash put NOTREESE'S config where YOURS is,"
echo "  so they are off unless you say yes. ai installs the tooling and asks again before it"
echo "  touches any rules file."
echo "  Pick a subset by naming it (e.g. ./install.sh vim ai), or see every file first with --dry-run."

# Listed before anything is asked, so the reader knows the full cost of saying
# yes to everything before answering the first question. The per-target lists
# below repeat the relevant ones at the moment of each decision; this is the
# whole picture, which is the thing you want before you start.
if ! $EXPLICIT_TARGETS; then
  at_risk=""
  for t in "${TARGETS[@]}"; do
    found="$(would_replace "$t")"
    [ -n "$found" ] && at_risk="$at_risk$found
"
  done

  if [ -n "$at_risk" ]; then
    echo
    warn "these files of yours would be replaced if you say yes to everything:"
    printf "%s" "$at_risk" | sed "s|^$HOME|~|; s|^|      |"
    echo "      (each is copied to $BACKUP_DIR/ first, and each target is asked about separately)"
  fi

  # The agent rules files are not in the lists above, because the ai target
  # links three commands and it is ai-setup that writes those files. Saying so
  # here anyway: leaving the biggest one off a list headed "what gets replaced"
  # would be the omission that matters most.
  case " ${TARGETS[*]} " in
    *" ai "*)
      echo
      echo "  The ai target also writes your AI agent rules files (~/.claude/CLAUDE.md and"
      echo "  the like). It asks separately whether to replace those with a link to this"
      echo "  repo's rules, or to keep your file and append to it."
      ;;
  esac
fi
$ASSUME_YES && warn "--yes: replacing existing files without asking (originals still go to $BACKUP_DIR/)"
echo


# ---- Dispatcher ---------------------------------------------
for target in "${TARGETS[@]}"; do
  case "$target" in
    tmux|vim|bash|ai) ;;
    *) err "unknown target: $target"; err "known: tmux vim bash ai"; exit 1 ;;
  esac

  # Asked before anything is touched, and after being told exactly which of your
  # files it would replace. A dry run reports rather than asks — it changes
  # nothing, so there is nothing to consent to.
  TARGET_CONFIRMED=false
  if ! $DRY_RUN && ! want_target "$target"; then
    warn "skipping $target"
    remember_target "$target" false
    continue
  fi

  $DRY_RUN || remember_target "$target" true

  case "$target" in
    tmux)  install_tmux; INSTALLED_TMUX=yes ;;
    vim)   install_vim ;;
    bash)  install_bash ;;
    ai)    install_ai ;;
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
  # Only for a target that actually ran. A next step for something the user
  # just declined reads as though it happened anyway.
  if [ -n "$INSTALLED_TMUX" ]; then
    echo
    echo "Next steps:"
    echo "  - Open tmux and press 'prefix + I' to install plugins"
    echo "  - Reload an existing tmux session with 'prefix + r'"
  fi
fi
