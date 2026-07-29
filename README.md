# dotfiles

Personal config files for the tools I use day-to-day.

## What's here

| Tool | Path in repo | Symlinked to |
| --- | --- | --- |
| tmux | `tmux/tmux.conf` | `~/.tmux.conf` |
| tmux dev layout | `tmux/scripts/dev-layout.sh` | `~/.tmux/scripts/dev-layout.sh` |
| tmux clipboard helper | `tmux/scripts/clip.sh` | `~/.tmux/scripts/clip.sh` |
| vim | `vim/vimrc` | `~/.vimrc` |
| bash | `bash/bashrc` | `~/.bashrc` |
| bash login | `bash/bash_profile` | `~/.bash_profile` |
| AI agent rules | `ai/` | assembled into each agent's rules file |

More to come (git, …).

> **README revamp pending.** The `ai/` tooling is being built out and this file
> still describes only the original tools. Rewrite once that work lands.

## Install

### 1. Get the files

```bash
git clone https://github.com/<your-username>/dotfiles ~/dotfiles
cd ~/dotfiles
```

If you downloaded files manually instead of cloning, the executable bit on shell scripts probably got dropped:

```bash
chmod +x install.sh tmux/scripts/dev-layout.sh tmux/scripts/clip.sh
```

### 2. Run the installer

```bash
./install.sh
```

The installer symlinks each file from the repo into your home directory. Edits you make to files in the repo show up immediately — no copying step. Anything that was already at the destination gets backed up to `~/.dotfiles-backup/<timestamp>/` before being replaced, so nothing you wrote by hand is ever lost silently.

Other modes:

```bash
./install.sh --dry-run    # show what would happen, change nothing
./install.sh tmux         # install only one tool
```

### 3. Make bash your default shell (macOS only)

macOS defaults to zsh. To make bash the login shell so the prompt and history settings here actually apply to new terminals:

```bash
chsh -s /bin/bash      # no sudo needed
exec bash              # or open a new terminal
echo $SHELL            # verify it now reads /bin/bash
```

### 4. Install tmux plugins

The installer clones [TPM](https://github.com/tmux-plugins/tpm) for you. To install the plugins listed in `tmux.conf`, open tmux and press:

```
prefix + I       (capital i — `Ctrl-b` then `Shift-i`)
```

You'll see TPM fetching plugins; takes a few seconds. Done once per machine.

### 5. Sanity check

```bash
ls -la ~/.bashrc ~/.bash_profile ~/.vimrc ~/.tmux.conf \
       ~/.tmux/scripts/dev-layout.sh ~/.tmux/scripts/clip.sh
```

All six should show up as symlinks (`->`) pointing back into `~/dotfiles/`.

## Prerequisites

Required:

- `tmux` 3.1 or newer (`brew install tmux`)
- `git` (for cloning TPM and the repo itself)
- `python3` 3.7 or newer — the `ai` tooling is Python, stdlib only, no packages to install

Recommended (used by some configs but not strictly required):

- `eza` — pretty file listings (`brew install eza`)

### Before running the `ai` target

Nothing has to exist up front — `./install.sh ai` works on a bare machine and asks for the rest. What it asks, and what you need ready if you want to answer it:

| Prompt | Needed beforehand | If you skip it |
|---|---|---|
| Private local-rules git remote | A repo you can clone over SSH, and working SSH auth to that host | Leave blank. The universal rules still apply; drop `*.md` files into `ai/local_rules/` by hand instead |
| Agent targets | Nothing | Defaults to the agents whose directories already exist (`~/.claude`, `~/.codex`), falling back to `claude` |
| Daily-notes path | Nothing yet — the sync tooling is not built | Defaults to `~/daily-notes`. It is recorded in the config and otherwise unused for now |

The private rules remote is only cloned when the local-rules directory is empty, so an existing `ai/local_rules/*.md` always wins over the remote — a clone can never overwrite rules that exist nowhere else. Clear the directory if you want the remote to take over.

## Per-tool notes

### tmux

- Default prefix is unchanged (`Ctrl-b`).
- Plugins are managed by [TPM](https://github.com/tmux-plugins/tpm). The installer clones it; `prefix + I` inside tmux installs the rest.
- `prefix + D` opens a name prompt and builds a pre-laid-out dev workspace (3 terminals on the left, editor + runner on the right). The script behind it lives at `tmux/scripts/dev-layout.sh` and can also be run from a plain shell as `tmuxdev <name>`.
- Theme is [Dracula](https://github.com/dracula/tmux); status bar shows session, git status, CPU, RAM, and time.
- Sessions are auto-saved every 15 min via `tmux-continuum` and auto-restored on tmux startup, so reboots and crashes don't lose work.
- Copy-mode yanks pipe through `tmux/scripts/clip.sh`, which auto-picks `pbcopy` (macOS), `wl-copy` (Wayland), `xclip`, or `xsel` — whichever is available.

### vim

- Minimal, portable, no-plugins. Works the same on every machine you SSH into.
- 4-space indents, line numbers, search highlighting (tap `Space` in normal mode to clear), bash-style command-line tab completion.
- Tab navigation via `tj` / `tk`. Optional buffer-workflow mappings (`bn` / `bp`) are commented out at the bottom of `vimrc` if you want to try them.
- Built-in `netrw` file explorer is configured for tree-view with the banner hidden — open with `:e .` (or `:Lex` for a persistent sidebar).
- Trailing whitespace is stripped on save for `c`, `python`, `zig`, `go`, `rust`, `sh`, `vim`, `lua`, `javascript`, `typescript`. Markdown is excluded on purpose (double-space EOLs are meaningful there).

### bash

- Cross-platform: works on macOS (system `/bin/bash`) and Linux. No installs assumed.
- History is effectively unlimited (1M lines), with `↑` walking only this shell's history while every command is appended to `~/.bash_history` immediately — so no command is lost when shells overlap.
- `set -o vi` puts vi keybindings on the command line itself (press `Esc` for normal mode, then `0`, `$`, `b`, `w`, `cw`, `dd`, `/` for history search, etc.).
- Git-aware prompt: shows `(branch)` when in a repo, hides otherwise. Prompt's `$` is green on success, red on the last command's failure.
- One alias only: `tmuxdev` → `~/.tmux/scripts/dev-layout.sh`. The `tmux` prefix means tab-completion finds it after `tmu<Tab>`.
- `~/.bash_profile` just sources `~/.bashrc`, so login shells (default on macOS Terminal) and non-login shells (default in tmux panes) behave the same.

### ai

Shared rules for AI coding agents (Claude Code, Codex CLI, Cursor), assembled from two layers so one set of rules can be reused everywhere without leaking anything private.

- `ai/AGENTS.md` — the universal, shareable rules. Edit these in one place; every agent gets them.
- `ai/local_rules/` — the private, per-context layer (work-specific rules, internal conventions). **The directory is tracked but its contents are ignored**, so the layer exists on every clone and never reaches this repo. Drop `*.md` files in and they get merged in locally, in filename order — prefix them (`10-`, `20-`) to control that order. **`README.md` is skipped**, so the directory can document itself without the documentation becoming instructions; this matters because a repo created through a web UI ships a boilerplate README, and it is markdown like everything else.
- `ai/lib/`, `ai/bin/` — the assembler and its setup command.
- `ai/tests/` — `python3 -m unittest discover -s ai/tests -t ai/tests`

The two commands:

- `ai-setup` — asks where things live (private rules remote, which agents, notes path), writes the answers to `~/.config/ai-notes/config.json`, then runs `ai-rules apply`. Re-running it edits settings: every prompt is pre-filled with what is already configured, so pressing enter keeps it. `--dry-run` reports what it would write and stops. Non-interactive when stdin is not a terminal, which is how `install.sh` drives it.
- `ai-rules apply` — merges the two layers into **one** file at `~/.config/ai-notes/rules.md` and symlinks each agent's rules path to it, so nothing is duplicated and the agents cannot drift apart.

Anything already at an agent's path that this tool did not put there is copied to `<path>.bak` first. That backup is written once and never overwritten — if one is already there the run stops and says so, because it holds the only copy of whatever was there before, while the assembled file can be rebuilt from the sources at any time. Remove it yourself once you are happy.

## Troubleshooting

### `Illegal variable name.` (or other parse errors) when sourcing `~/.bashrc`

You're not in bash. The bashrc has a guard at the top that bails with a clear message — but only if the parser gets that far. To check what shell you're actually in:

```bash
ps -p $$        # current shell process
echo $0
echo $SHELL     # NOTE: this is your *login* shell, not the current one
```

`$SHELL` is set from `/etc/passwd` by `chsh`; it doesn't reflect what you're typing into right now. Fix: `chsh -s /bin/bash` and start a new terminal, or just type `bash` to drop into a subshell.

### `chsh` is locked by IT (`You may not change the shell`)

Common at managed shops (especially HPC / hardware-engineering environments where csh or tcsh is policy). `sudo chsh` won't help — the lock is upstream in PAM/LDAP. Three workarounds, in order of cleanness:

1. **Configure your terminal emulator to launch bash directly.** gnome-terminal: Preferences → Profile → "Run a custom command instead of my shell" → `/bin/bash -l`. iTerm2: Profile → General → Command → Custom Shell → `/bin/bash`.

2. **Force tmux to use bash regardless of `$SHELL`.** Already in `tmux.conf`:
   ```
   set -g default-shell /bin/bash
   set -g default-command /bin/bash
   ```

3. **Have csh hand off to bash on launch.** Add to `~/.cshrc` (NOT bashrc):
   ```csh
   if ( $?prompt ) then
       if ( -x /bin/bash ) exec /bin/bash -l
   endif
   ```
   `$?prompt` ensures only interactive csh sessions are hijacked — cron jobs and scp aren't affected.

### tmux still spawns my old shell after editing `tmux.conf`

`prefix + r` reloads most options live, but `default-shell` and `default-command` are read once at server start. To pick them up, fully restart the server:

```bash
tmux kill-server
tmux
```

(Heads-up: discards in-memory `tmux-continuum` state. Saved snapshots on disk survive.)

### `$SHELL` inside tmux still says `/bin/csh` but I'm in bash

`$SHELL` is inherited from the parent process — child bash doesn't overwrite it. The bashrc here exports `SHELL=$BASH` at load time to correct this. If something downstream is still seeing csh, confirm bashrc actually loaded: `echo $BASH_VERSION` should print a version string.

### `prefix + D` doesn't build the dev layout

Most likely the panes are running the wrong shell (see above) — `dev-layout.sh` needs bash. Run it directly to surface any errors:

```bash
~/.tmux/scripts/dev-layout.sh testname ~
```

It will fail loudly if tmux isn't on PATH, the name has `.` or `:`, the directory doesn't exist, or the window is below 80×20 cells.

## Adding a new tool

1. Create a folder for it: `mkdir <tool>` (e.g. `vim/`).
2. Drop the config file(s) inside, dropping any leading dot from the filename — `vim/vimrc`, not `vim/.vimrc`. Files without leading dots are easier to browse on GitHub.
3. Add an `install_<tool>` function in `install.sh` that calls `link` for each file:
   ```bash
   install_vim() {
     info "Installing vim config"
     link "$DOTFILES_DIR/vim/vimrc" "$HOME/.vimrc"
   }
   ```
4. Add the tool to the dispatcher's `case` statement and to the default `TARGETS=(...)` list at the top.
5. Update the table in this README.

## Local-only overrides

Anything ending in `.local` is ignored by git (`.gitignore`). Use this for machine-specific or secret values that shouldn't go in the public repo. Pattern: have your shared config source the local file if it exists.

For example, in a future `bash/bashrc`:

```bash
[ -f ~/.bashrc.local ] && source ~/.bashrc.local
```

Then put work-laptop-only or personal-only stuff in `~/.bashrc.local`.
