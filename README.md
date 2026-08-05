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

### What a bare `./install.sh` asks

**These are notreese's dotfiles.** `tmux`, `vim` and `bash` do not install those programs — they put *this repo's* config where *yours* is. Most people cloning this will not want that, so **they are off unless you say yes**:

```
[!] replace your bash config with this repo's — these are YOURS and get replaced:
      ~/.bashrc
      (a copy of each goes to ~/.dotfiles-backup/20260730-183900/)
 ?  bash [y/N]
```

Press enter at every prompt and nothing of yours is touched.

| Target | Default | What it actually does |
|---|---|---|
| `tmux` | **no** | replaces `~/.tmux.conf` and the two helper scripts |
| `vim` | **no** | replaces `~/.vimrc` |
| `bash` | **no** | replaces `~/.bashrc` and `~/.bash_profile` |
| `ai` | yes | links three commands into `~/.local/bin`; asks again before touching any rules file |

`ai` defaults on because it replaces nothing on its own — it installs the tooling, and every rules file it would write is its own separate question.

- **Answer no and that target is not touched at all** — no links, no backups, nothing.
- **Your answer is remembered** in `~/.config/ai-notes/config.json`, so a re-run pre-fills it and a declined target stays declined, including on unattended re-runs.
- **Only files at risk are listed.** Anything already pointing at this repo is not a loss, so it is left out — otherwise the warning would fire on every routine re-run and stop being read. A dangling symlink *is* listed; it is still yours, pointing where you chose.
- **`./install.sh vim ai` skips the questions** — naming a target is answering it. So does `--yes`. `--dry-run` reports and asks nothing.

Whatever gets replaced goes to `~/.dotfiles-backup/<timestamp>/` either way.

### Before running the `ai` target

Nothing has to exist up front — `./install.sh ai` works on a bare machine and asks for the rest. What it asks, and what you need ready if you want to answer it:

| Prompt | Needed beforehand | If you skip it |
|---|---|---|
| Private local-rules git remote | A repo you can clone over SSH with **at least one `*.md` that is not `README.md`**, and working SSH auth to that host | Leave blank. The shareable modules still apply; drop `*.md` files into `~/.config/ai-notes/local_rules/` by hand instead |
| Agent targets | Nothing | Defaults to the agents whose directories already exist (`~/.claude`, `~/.codex`), falling back to `claude` |
| One question per rules module | Nothing | Each module supplies its own default — `daily-notes` yes, `misc` no. Saying yes to `daily-notes` is followed immediately by where notes live and which remote they sync with; saying yes to `misc` **replaces** what your agent files hold now, so that prompt names each file first. Whatever is there is backed up either way |
| Daily-notes git remote | A **private** repo you can clone over SSH | Leave blank and notes stay on this machine — everything else still works, nothing syncs |

The private rules remote is only cloned when the local-rules directory is empty, so existing `*.md` files always win over the remote — a clone can never overwrite rules that exist nowhere else. Clear the directory if you want the remote to take over.

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

Shared rules for AI coding agents (Claude Code, Codex CLI, Cursor), assembled from opt-in modules plus a private layer, so one set of rules can be reused everywhere without leaking anything private and without forcing notreese's opinions on anyone who clones this.

- `ai/rules/` — the shareable modules. The directory is **globbed**, so adding a module means adding a file and nothing else. What ships:

  | Module | Holds | Included when |
  |---|---|---|
  | `universal.md` | How this rules system itself works — chiefly that the agent files are generated, so edits belong in the repo | Always; it declares `required` |
  | `daily-notes.md` | The daily-notes discipline: what to log, where, and when | declares `default=on` |
  | `misc.md` | One person's general working rules — writing style, code conventions, commit gating | declares `default=off` |

  The split is the point: you can inherit the daily-notes habit without inheriting the opinions.

  **Each module declares its own metadata on line 1**, in an HTML comment that rendered markdown never shows:

  ```markdown
  <!-- ai-rules: order=40, default=off, prompt="Include the review-checklist rules" -->
  ```

  | Entry | Means | Default |
  |---|---|---|
  | `order=N` | sort position, for assembly *and* for the order `ai-setup` asks | 50 |
  | `default=on` / `off` | the answer used before anyone has been asked | `off` |
  | `required` | never asked about, never off | absent |
  | `prompt="..."` | the question asked; quote it if it contains a comma | built from the `# ` heading |

  Declaring nothing is valid — the module is then asked about, and off until you say yes. `ai-setup` asks about each module in `order` position and records the answers under `modules` in the config, in that same order. `ai-rules apply` wraps each one in markers naming its file, so the assembled document says where every section came from.

  **A module the config switched on whose file has gone away is a hard error** — `ai-rules apply` writes nothing rather than quietly assembling rules that are short a whole discipline.
- **The private layer** — work-specific rules, internal conventions. Lives at `~/.config/ai-notes/local_rules/` by default, **outside this repo on purpose**: cloning a private repo into a tracked directory here nests two repos, and the `.gitignore` that ships `ai/local_rules/` (`*` plus `!.gitignore`) then lands inside the clone, where it ignores every rule file the clone exists to carry. Drop `*.md` files in and they get merged in locally. **It reads exactly like `ai/rules/`** — same glob, same `README.md` skip, the same `<!-- ai-rules: order=N -->` declaration, and the same per-file markers naming where each rule came from. Ordering is by declared `order` then filename, so the `10-`/`20-` prefix convention still works as a tie-break. The one difference: nothing here is ever asked about, because a private file is machine-local and was put there on purpose — so it applies unless it declares `default=off`, which shelves it without deleting it. **`README.md` is skipped**, so the directory can document itself without the documentation becoming instructions; this matters because a repo created through a web UI ships a boilerplate README, and it is markdown like everything else. If a configured remote produces no rules — a repo holding only that README counts as empty — setup says so rather than reporting success with no private layer.
- `ai/local_rules/` — the in-repo fallback, still gitignored so anything dropped there can never reach this repo. Nothing defaults to it any more; point `local_rules_dir` at it if you want it used. Rules left there while the config points elsewhere are reported, not silently ignored.
- `ai/lib/`, `ai/bin/` — the assembler and its setup command.
- `ai/tests/` — `python3 -m unittest discover -s ai/tests -t ai/tests`

The two commands:

- `ai-setup` — asks where things live (private rules remote, which agents, notes path), writes the answers to `~/.config/ai-notes/config.json`, then runs `ai-rules apply`. Re-running it edits settings: every prompt is pre-filled with what is already configured, so pressing enter keeps it. `--dry-run` reports what it would write and stops. Non-interactive when stdin is not a terminal, which is how `install.sh` drives it.
- `ai-rules apply` — merges the selected modules and the private layer into **one** file at `~/.config/ai-notes/rules.md` and symlinks each agent's rules path to it, so nothing is duplicated and the agents cannot drift apart.

#### Daily notes

A private git repo of dated work notes (`<notes>/<date>/<project>.md`, where `<notes>` is the directory you name during setup) kept in step across several machines, with the agent pulling before it writes so two machines cannot silently diverge, and stopping to ask on a real conflict rather than picking a winner.

`ai-setup` asks whether to include the daily-notes rules — the module declares its default as **yes**, since including it only appends a section. Say yes and it also asks where the notes live and which remote they sync with. Say no and nothing else about notes is asked or recorded.

**`daily-notes-sync`** is the third tool, installed alongside the other two:

| Command | Does |
|---|---|
| `daily-notes-sync pull` | reports what changed on the other machines and **commits nothing** — the freshness check to run *before* writing a note |
| `daily-notes-sync` | pull, commit everything, push |
| `daily-notes-sync sync -m "…"` | same, with your own commit message |

Three things it deliberately will not do:

- **Resolve a conflict.** Both sides are prose someone wrote, so it aborts the rebase, names the files, and exits non-zero. Your working tree is left byte-identical — nothing half-merged, no conflict markers.
- **Fail because the network did.** A push it cannot deliver leaves the commit local and exits **0**; the note goes out on the next sync. Blocking someone's work over a wifi drop is worse than a stale remote.
- **Create a repository.** If the notes directory is not a repo, it says so and prints the `git init` line for you to run. Whether a directory of your notes becomes a repository is your decision — `ai-setup` takes the same position, and will clone into an empty directory but never `init` or repoint an existing one.

**The remote must be private.** These are work notes; put them somewhere you would put work.

Anything already at an agent's path that this tool did not put there is moved into a timestamped directory under `~/.dotfiles-backup/` first, and the run prints where. One directory per run, paths mirrored under it as they sit under `$HOME`, so nothing collides and nothing is overwritten. Nothing prunes it, so delete old ones yourself once you are happy.

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
