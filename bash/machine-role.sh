# ============================================================
# machine-role.sh — decide what kind of box this is, then set
# the environment that follows from the answer.
#
# Sourced by bash/bashrc. Safe to source twice.
# ============================================================
#
# Where this machine's state lives differs by site: an ordinary machine keeps it
# under ~, while a machine whose home is a shared network volume must keep it on
# local disk instead. The optional site profile declares the answer in a
# shell-sourceable file, which this reads directly.
#
# Deliberately NOT a pointer file written by `autorun-mode`. Writing one would
# mean writing into the shared home — which an autorun box is forbidden to do,
# and which is only ever correct while every machine happens to resolve to the
# same path. Reading the site's own declaration has neither problem, and costs
# an interactive shell one small file read rather than a Python startup.
NV_SITE_ENV="${XDG_CONFIG_HOME:-$HOME/.config}/autorun-mode/site/site.env"

# Resolve this machine's autorun state directory.
#
# Args:
#     None
#
# Returns:
#     Writes the directory to stdout. Falls back to the XDG default when no
#     pointer has been written, which is correct for a machine that has never
#     run `autorun-mode`.
#
# Raises:
#     None
nv_state_dir() {

    local dir="${AUTORUN_STATE_DIR:-}"

    # Sourced in a subshell so the site's variables never leak into the
    # interactive environment; only the resolved path comes back.
    if [ -z "$dir" ] && [ -r "$NV_SITE_ENV" ]; then
        dir=$( . "$NV_SITE_ENV" >/dev/null 2>&1; echo "${AUTORUN_STATE_DIR:-}" )
    fi

    if [ -n "$dir" ]; then
        echo "$dir"
    else
        echo "${XDG_STATE_HOME:-$HOME/.local/state}/autorun-mode"
    fi
}

# Read this machine's role.
#
# Args:
#     $1 (str): the resolved state directory.
#
# Returns:
#     Writes "autorun" or "interactive" to stdout. An absent, empty, or
#     unrecognized marker reads as "interactive" — the safe default, since an
#     unattended box must be opted into deliberately and never by accident.
#
# Raises:
#     None
nv_machine_role() {

    local role=""

    [ -r "$1/machine-role" ] && role=$(tr -d '[:space:]' < "$1/machine-role" 2>/dev/null)

    case "$role" in
        autorun) echo "autorun"     ;;
        *)       echo "interactive" ;;
    esac
}

# Apply the environment implied by the AUTORUN role.
#
# Args:
#     $1 (str): the resolved state directory.
#
# Returns:
#     Nothing. Exports CLAUDE_CONFIG_DIR, PATH and NV_ROLE_BADGE as side effects.
#
# Raises:
#     None
nv_apply_autorun_env() {

    # The agent's whole config directory moves onto this machine's own state
    # directory, so its settings, credentials and session state never race
    # another machine's copies across a shared home.
    export CLAUDE_CONFIG_DIR="$1/claude-autorun"

    # The sandbox shim shadows the real agent binary by sitting earlier in PATH,
    # so an ordinary `claude` is confined without anyone having to remember a
    # different command. Added only while the role is autorun, which is what
    # makes `autorun-mode off` take effect without uninstalling anything.
    if [ -d "$1/autorun-bin" ]; then
        PATH="$1/autorun-bin:$PATH"
        export PATH
    fi

    # Red, bracketed, and impossible to miss at the start of every prompt.
    export NV_ROLE_BADGE='\[\e[1;31m\][AUTORUN]\[\e[0m\] '
}

NV_STATE_DIR="$(nv_state_dir)"
export NV_MACHINE_ROLE="$(nv_machine_role "$NV_STATE_DIR")"
export NV_ROLE_BADGE=""

if [ "$NV_MACHINE_ROLE" = "autorun" ]; then
    nv_apply_autorun_env "$NV_STATE_DIR"
fi

# Anything else this site needs in an interactive shell. Hostnames, employer
# tooling and naming conventions belong there rather than here: this file ships
# in a public repo and has to mean something on a machine that has never heard
# of them.
if [ -r "${NV_SITE_ENV%/*}/site.sh" ]; then
    source "${NV_SITE_ENV%/*}/site.sh"
fi
