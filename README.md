# dotfiles

Personal shell and editor config, plus a toolkit that gives every AI coding agent you use the same rules, a shared daily-notes habit, and a few small hooks. Every piece is optional, and nothing replaces a file of yours without asking first.

```bash
git clone https://github.com/<your-username>/dotfiles ~/dotfiles
cd ~/dotfiles
./install.sh --dry-run     # see exactly what it would do, change nothing
```

## Why this exists

- **Agents read different files and drift apart.** Claude Code, Codex CLI and Cursor each load rules from their own place. Here the rules are assembled once and every agent is pointed at the result, so there is one copy to edit.
- **Work gets lost between sessions and machines.** The daily-notes habit has the agent record what it finished and keeps those notes in step across your machines through a private git repo.
- **A model has no clock.** It reuses whatever date it saw earlier in the conversation, so a hook restates the current date every turn.
- **Borrowing someone's dotfiles usually means replacing yours.** Here every part is opt-in, and anything replaced is backed up first. You can take the daily notes and nothing else.

## What's in the box

| Part | What it gives you | Installed by |
|---|---|---|
| `tmux/` | `~/.tmux.conf`, a dev-layout script, a clipboard helper | `./install.sh tmux` |
| `vim/` | `~/.vimrc` | `./install.sh vim` |
| `bash/` | `~/.bashrc`, `~/.bash_profile`, an SSH clipboard shim | `./install.sh bash` |
| `ai/` | rules, daily notes, hooks, skills, six commands in `~/.local/bin` | `./install.sh ai` |

The shell and editor config is notreese's own set of preferences, so those three targets are off unless you ask for them. The `ai/` toolkit is the part meant to be reused.

## Contents

- [Install](#install)
- [Taking only part of it](#taking-only-part-of-it), including [the smallest install: only daily notes](#the-smallest-install-only-daily-notes)
- [The AI toolkit](#the-ai-toolkit): [rules](#rules-modules), [your own rules](#the-private-layer-your-own-rules), [an existing rules file](#when-you-already-have-a-rules-file), [daily notes](#daily-notes), [hooks](#hooks), [skills](#skills), [unattended machines](#unattended-machines), [every command](#every-command), [undoing it](#undoing-it)
- [Common questions](#common-questions)
- [Per-tool notes](#per-tool-notes): tmux, vim, bash
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Install

You need `git` and `python3` 3.7 or newer (the `ai` tooling is Python with no packages to install). The tmux config wants `tmux` 3.1 or newer.

Once you have cloned it and looked at the dry run, install for real from the repo directory:

```bash
./install.sh
```

A bare `./install.sh` asks one question per target. `tmux`, `vim` and `bash` default to **no**, because saying yes puts this repo's config where yours is. `ai` defaults to **yes**, because on its own it only adds commands and then asks its own questions before it touches any rules file.

```
[!] replace your bash config with this repo's — these are YOURS and get replaced:
      ~/.bashrc
      (a copy of each goes to ~/.dotfiles-backup/20260730-183900/)
 ?  bash [y/N]
```

- **Answering no skips that target completely.** No links, no backups.
- **Answers are remembered** in `~/.config/ai-notes/config.json`, so re-running pre-fills them.
- **Naming a target skips its question.** `./install.sh vim ai` installs exactly those two. `--yes` answers yes to everything.
- **The installer also asks "Make this an AUTORUN box?"** Answer `n` unless you run agents unattended (see [Unattended machines](#unattended-machines)).
- **Anything already at a destination** is moved to `~/.dotfiles-backup/<timestamp>/`, with the path mirrored underneath it. Nothing prunes that directory, so clear old ones out yourself.

Afterwards:

- **macOS only:** the shell config assumes bash. `chsh -s /bin/bash`, then open a new terminal.
- **tmux:** open tmux and press `prefix + I` (capital i, so `Ctrl-b` then `Shift-i`) once to fetch the plugins.

## Taking only part of it

| You want | Run | What changes on your machine |
|---|---|---|
| Just the daily notes | `./install.sh ai`, then answer as in the next section | commands, a config directory, a rules block, skills, two hooks. No shell or editor files |
| Your own rules, shared across agents and machines | `./install.sh ai`, say no to `misc`, put your files in the [private layer](#the-private-layer-your-own-rules) | the same as above, plus your rules |
| notreese's general working rules too | answer yes to the `misc` question | adds the contents of `ai/rules/misc.md` to what your agents read |
| tmux, vim or bash config | `./install.sh tmux` (or `vim`, `bash`) | replaces the matching dotfiles, with backups |

### The smallest install: only daily notes

```bash
./install.sh ai
```

Naming `ai` means the tmux, vim and bash questions are never asked. These are the prompts you will meet, in order, and the answers that give you daily notes and nothing else:

| Prompt | Answer |
|---|---|
| Backup directory | Enter |
| Make this an AUTORUN box? | `n` |
| Private local-rules git remote | blank, or your own private rules repo (see below) |
| Agent targets | the agents you use, e.g. `claude`. The default is all three |
| *If you already have a rules file:* `clobber` or `additive` | `additive` keeps your file exactly as it is |
| Include the daily-notes rules, skill and reminder hook | `y` |
| Daily-notes path | where notes should live. Avoid `~/Documents` on macOS, which agents can be silently blocked from |
| Daily-notes git remote | a **private** SSH URL, or blank to keep notes on this machine only |
| Inherit ALL of notreese's general working rules | `n` |

Check it worked:

```bash
daily-notes-sync status
```

**What that install did to your machine.** This is the complete list:

| Where | What |
|---|---|
| `~/.local/bin/` | six symlinks: `ai-rules`, `ai-setup`, `ai-hooks`, `daily-notes-sync`, `autorun-mode`, `mcp-sync` |
| `~/.config/ai-notes/` | `config.json` (your answers) and `rules.md` (the assembled rules) |
| Each agent's rules file, e.g. `~/.claude/CLAUDE.md` | with `additive`, a generated block is appended and your text stays. With `clobber`, it becomes a symlink to `rules.md` |
| Each agent's skills directory, e.g. `~/.claude/skills/` | symlinks to this repo's skills (see [Skills](#skills)) |
| Each agent's hook file, e.g. `~/.claude/settings.json` | two hooks merged in (see [Hooks](#hooks)) |
| Your notes directory | cloned from your remote if the directory is empty. It is never turned into a git repository for you |

It does **not** touch `.bashrc`, `.vimrc`, `.tmux.conf`, or any setting in your agents' config files other than the `hooks` key.

## The AI toolkit

### How the pieces fit

```
 ai/rules/*.md ──(the modules you said yes to)──┐
                                                ├──> ~/.config/ai-notes/rules.md ──> each agent's rules file
 your private layer: local_rules/*.md ──────────┘

 ai/skills/*  ────────────────────────────────────> each agent's skills directory   (loaded on demand)
 ai/hooks/*   ────────────────────────────────────> each agent's hook config         (run on events)
```

`ai-setup` asks the questions and saves the answers. `ai-rules apply` assembles `rules.md` and puts it where each agent reads it. Re-run `ai-setup` any time: every prompt is pre-filled with your current answer, so pressing Enter keeps it.

### Rules: modules

Each file in `ai/rules/` is a module you can switch on or off as a whole.

| Module | What it holds | Default |
|---|---|---|
| `universal.md` | how this system works, chiefly "the live rules file is generated, so edit the source" | always on |
| `daily-notes.md` | the daily-notes habit: what to log, where, and when | on |
| `misc.md` | one person's general working rules: writing style, code conventions, commit review | off |

The choice is per module, not per rule. You cannot take half of `misc.md`; take it or leave it. To borrow only some of it, copy those sections into your own private-layer file.

### The private layer: your own rules

Your own rules go in a directory outside this repo, `~/.config/ai-notes/local_rules/` by default (the `local_rules_dir` setting). Every `*.md` file there is added to the assembled rules, in a `LOCAL` block at the end. A few things to know:

- **It is for anything that is yours, not only company rules.** Personal preferences and work-specific rules both belong here. The only difference from a module is that nothing in it is asked about, since you put it there on purpose.
- **It does not have to live in this repo, and should not.** Keep it outside the clone so it can never be committed to a public repo by accident. `ai/local_rules/` exists only as a gitignored fallback.
- **It can be a private git repo.** Give `ai-setup` an SSH URL and it clones it, but only when the directory is empty, so a clone can never overwrite rules that exist nowhere else. The repo needs at least one `*.md` that is not `README.md`, which is skipped on purpose.
- **Files use the same options as modules**, in a declaration on line 1. `<!-- ai-rules: order=40 -->` sets the position; `default=off` shelves a file without deleting it.
- **It can carry skills too.** A `skills/` directory inside it is linked the same way as this repo's.

### When you already have a rules file

If a configured agent already has a real rules file, `ai-setup` asks how to treat it:

| | `clobber` (what Enter gives you) | `additive` |
|---|---|---|
| Your `~/.claude/CLAUDE.md` | replaced by a symlink to `~/.config/ai-notes/rules.md` | stays your real file |
| Your own text | no longer read. A copy is in the backup directory; move it into the private layer to keep it | untouched |
| What is added | everything, as the whole file | a block between `### BEGIN ai-rules` and `### END ai-rules`, which a re-run replaces. Text you write below it moves above it on the next run |
| Editing the file by hand | edits are lost on the next `ai-rules apply`. Edit the source instead | edit anywhere outside the block |

A backup is made either way. With no existing file there is nothing to ask, and the two modes behave the same.

**Cursor is the odd one.** It reads its rules from a settings box, not a file, so the text is parked at `~/.config/ai-notes/cursor-user-rules.txt` and you paste it into Cursor's User Rules by hand whenever it changes materially.

### Daily notes

A folder of dated work notes that your agent keeps for you and that syncs across machines through a private git repo.

- **Layout:** `<notes>/<YYYY-MM-DD>/<project>.md` for each day's record, and `<notes>/current/<project>.md` for what is open right now. Each day's file has Accomplishments, In Progress, TODOs and Meetings.
- **What the agent does:** logs finished work as it lands, keeps TODOs sorted by priority marker (`[!]` urgent, `[>]` next, `[ ]` open, `[~]` later), and pulls before it writes so two machines cannot silently diverge.
- **The remote must be private.** These are work notes.

`daily-notes-sync` does the git work:

| Command | Does |
|---|---|
| `daily-notes-sync status` | reports where the notes live and whether syncing is set up. Changes nothing |
| `daily-notes-sync pull` | brings in other machines' work and lists what changed. Commits nothing, so it is the check to run before writing |
| `daily-notes-sync` | pull, commit everything, push |
| `daily-notes-sync sync -m "…"` | the same, with your own commit message |

Three things it deliberately will not do:

- **Resolve a conflict.** Both sides are prose someone wrote, so it aborts, names the files and exits non-zero. Your working tree is left as it was.
- **Fail because the network did.** A push it cannot deliver leaves the commit local and exits 0. It goes out on the next sync.
- **Create a repository.** If the notes directory is not a repo it prints the `git init` line for you to run.

Leave the remote blank and notes still get written and committed locally. They just do not reach another machine until you add a remote.

### Hooks

Two small scripts from `ai/hooks/`, wired into each agent by `ai-hooks`:

| Hook | Fires | Does |
|---|---|---|
| `date-context` | when you submit a prompt | tells the model the current date and time, because a model has no clock and reuses stale dates across midnight |
| `notes-reminder` | when the agent finishes a turn | once per session, if nothing has been written to today's notes, asks the agent to log substantial work. Silent when the daily-notes module is off or no notes path is set |

**Where they go.** Each agent keeps hooks inside a config file that also holds your other settings, so `ai-hooks` merges one key and leaves the rest byte-identical:

| Agent | File |
|---|---|
| Claude Code | `~/.claude/settings.json`, under `hooks` |
| Codex CLI | `~/.codex/hooks.json` |
| Cursor | `~/.cursor/hooks.json` |

`ai-hooks` only writes to the agents you named in `ai-setup` (the `agents` setting), and says which ones it left alone. Each hook is an absolute path into this clone, so do not move the clone afterwards without editing those paths.

**What happens to hooks you already have.** Yours are never changed. Hooks on other events are untouched, and if the event a hook needs (`UserPromptSubmit` or `Stop` for Claude Code) already runs a hook of yours, ours is added after it so both run. Re-running is safe: a hook already wired is skipped. `ai-hooks status` shows what each agent runs, and says when ours sits after yours. The one case it won't merge is an event or `hooks` key that isn't in the shape the agent writes, such as a single object where a list belongs. It reports that, leaves the file as it was, and exits 1; `install.sh` shows a warning and carries on.

### Skills

Skills are instructions an agent loads only when a task matches, unlike rules, which are always in context. `ai-rules apply` symlinks `ai/skills/*` (and any in your private layer) into each agent's skills directory. It only touches names it ships: a skill of yours with the same name is left alone and reported.

| Skill | Tied to a module? |
|---|---|
| `daily-notes` | yes: linked only while the daily-notes module is on, and removed when you turn it off |
| `bug-and-comms` | no: always linked |
| `autorun-start` | no: always linked |

### Unattended machines

Skip this unless you run agents with nobody watching.

`autorun-mode on` marks a machine as an unattended box. It gives the agent its own config directory, loads extra rules from `ai/autorun/autorun.md` (never wait on a human, stay in the writable workspace, never publish, never rebuild the shared rules, tag every note `[AUTORUN]`), writes deny-rules for force-pushes, and puts a red `[AUTORUN]` badge on your prompt. With `bwrap` installed and a workspace declared by an optional site profile outside this repo, it also installs a sandbox wrapper around the agent. `autorun-mode off` reverses it and `autorun-mode status` reports. The role is stored per machine in `config.json`, and `--yes` can never grant it.

The bash config looks for `bash/machine-role.sh` in `$DOTFILES_DIR` or `~/Cloned/dotfiles`. On an autorun box, clone there or export `DOTFILES_DIR` from `~/.bashrc.local`.

### Keeping MCP servers in step

Claude Code rewrites `~/.claude.json` freely, which can take hand-edited MCP (Model Context Protocol) server definitions with it. `mcp-sync` keeps the definitions in a file you own, `~/.config/ai-notes/mcp-servers.json`, grouped however you like:

| Command | Does |
|---|---|
| `mcp-sync status` | reports every way the live config and your file disagree. Changes nothing |
| `mcp-sync apply` | makes the live config match your file. Servers not in your file survive and are named |
| `mcp-sync adopt <name> --group <group>` | copies a server you added by hand into your file |

### Every command

| Command | Purpose |
|---|---|
| `ai-setup [--dry-run]` | asks the questions, saves them, runs `ai-rules apply` |
| `ai-rules apply` | assembles the rules and writes each agent's file and skills |
| `ai-rules where` | prints every path in use on this machine |
| `ai-hooks install \| status` | wires or reports the hooks |
| `daily-notes-sync` | see [Daily notes](#daily-notes) |
| `autorun-mode on \| off \| status` | see [Unattended machines](#unattended-machines) |
| `mcp-sync status \| apply \| adopt` | see above |

### Undoing it

There is no uninstall command, so by hand:

1. **Rules:** with `clobber`, delete the symlink and copy your file back from `~/.dotfiles-backup/<timestamp>/`. With `additive`, delete the block between the `ai-rules` markers.
2. **Hooks:** remove the two entries pointing at `ai/hooks/date-context` and `ai/hooks/notes-reminder` from each hook file listed above.
3. **Skills:** `find ~/.claude/skills -maxdepth 1 -type l -lname '*/ai/skills/*'` lists the links; delete those. Repeat for `~/.codex/skills` and `~/.cursor/skills`.
4. **Commands:** `rm` the six symlinks in `~/.local/bin/`.
5. **Config:** `rm -r ~/.config/ai-notes`. Your notes directory is never touched by any of this.

## Common questions

**Can I take only the daily notes?** Yes. See [The smallest install](#the-smallest-install-only-daily-notes).

**Can I choose which rules I get?** Per module, not per rule. `daily-notes` and `misc` are separate yes/no questions. For a subset of `misc`, copy the parts you want into your own private-layer file.

**Can I add my own rules, and must they live in this repo?** Put them in the private layer, which is outside the repo. It is not only for company rules; it is for anything that is yours.

**What happens to my existing `CLAUDE.md`?** `ai-setup` asks. `additive` keeps it and appends a generated block. `clobber`, which is what Enter gives you, replaces it with a symlink and backs the original up. See [When you already have a rules file](#when-you-already-have-a-rules-file).

**Where does `~/.claude/CLAUDE.md` point after a `clobber`?** At `~/.config/ai-notes/rules.md`. Codex's `~/.codex/AGENTS.md` points at the same file, so the agents cannot drift apart.

**Can I edit `~/.claude/CLAUDE.md` directly?** Not under `clobber`: it is generated, and the next `ai-rules apply` overwrites your edit without saying so. Edit the module or your private-layer file, then run `ai-rules apply`.

**Does it install a hook, and where?** Yes, two: `date-context` always, and `notes-reminder`, which is silent unless daily notes are on. They land under `hooks` in `~/.claude/settings.json` and in the Codex and Cursor hook files. Your other hooks and settings are kept, and if you already have a hook on the same event, ours is added after it.

**Does it work across several machines?** Yes. Run the installer on each. Notes sync through their git remote, and a private rules repo is cloned wherever you give its URL.

## Per-tool notes

### tmux

- The prefix is the default `Ctrl-b`. Plugins come from TPM (Tmux Plugin Manager, https://github.com/tmux-plugins/tpm), which the installer clones; `prefix + I` installs them.
- `prefix + D` asks for a name and builds a dev workspace: three terminals on the left, an editor and a runner on the right. The script is `~/.tmux/scripts/dev-layout.sh`, also runnable as `tmuxdev <name>`.
- Splits: `prefix + |` and `prefix + -` open in the current directory. `prefix + h/j/k/l` moves between panes, `prefix + H/J/K/L` resizes, and `Ctrl-h/j/k/l` moves across vim and tmux together.
- Theme is Dracula (https://github.com/dracula/tmux), with git, CPU, RAM and time in the status bar.
- Sessions are saved every 15 minutes and restored when tmux starts, so a reboot does not lose your layout.
- The mouse is off on purpose, so your terminal keeps its own selection and scrollbar. `prefix + m` toggles it. To copy: `prefix + [`, `v` to select, `y` to copy.
- Copying goes through `tmux/scripts/clip.sh`, which picks `pbcopy`, `wl-copy`, `xclip` or `xsel`, and over SSH sends an OSC 52 (terminal clipboard escape) sequence. Terminal.app ignores that sequence, so connect with `sshc host` instead of `ssh host`.

### vim

- Minimal and plugin-free, so it behaves the same on every machine you log in to.
- 4-space indents, line numbers, incremental and smart-case search. Tap `Space` to clear search highlighting.
- `tj` and `tk` switch tabs. The built-in file explorer opens as a tree: `:e .` or `:Lex`.
- Yanks go to the system clipboard. Over SSH they route through `clip.sh`, so `sshc` is needed there too.
- Trailing whitespace is stripped on save for common code filetypes. Markdown is excluded, since double spaces at the end of a line mean something there.

### bash

- Works on macOS (system bash) and Linux. History is effectively unlimited, appended to `~/.bash_history` immediately, and `↑` walks only the current shell's history.
- `set -o vi` gives vi keys at the prompt: `Esc` for normal mode. Readline is set to complete case-insensitively and to list all matches on the first Tab.
- The prompt shows `(branch)` inside a git repo, and its `$` is green after success and red after a failure.
- Aliases and helpers: `tmuxdev`, and `sshc` for SSH with a working remote clipboard (it runs `osc52-shim`, which the `bash` target installs to `~/.local/bin`).
- `~/.bash_profile` sources `~/.bashrc`, so login and non-login shells match.
- Machine-specific or private settings go in `~/.bashrc.local`, which is sourced if present and ignored by git.

## Troubleshooting

**`Illegal variable name.` or other parse errors when sourcing `~/.bashrc`.** You are not in bash. Run `bash`, or `chsh -s /bin/bash` and open a new terminal. `echo $SHELL` shows your login shell, not the one you are typing in; `ps -p $$` shows the current one.

**`chsh` is locked by IT.** Common on managed machines. In order of cleanliness:
1. Set your terminal emulator to launch `/bin/bash -l` directly.
2. Rely on `tmux.conf`, which already pins `default-shell` to bash.
3. Add this to `~/.cshrc` so interactive csh hands off to bash: `if ( $?prompt ) then` / `if ( -x /bin/bash ) exec /bin/bash -l` / `endif`.

**tmux still starts my old shell after editing `tmux.conf`.** `default-shell` is read once per server. Run `tmux kill-server` and start again. This discards in-memory continuum state, but saved snapshots on disk survive.

**`prefix + D` does not build the layout.** The panes are probably running the wrong shell. Run `~/.tmux/scripts/dev-layout.sh testname ~` directly to see the error.

**An install said some hooks were not wired.** A hooks file or one of its events was not in the shape the agent normally writes, so `ai-hooks` left it alone. `ai-hooks install` prints which one. Put it in the normal shape, or move the file aside, and re-run.

**`ai-rules apply` refuses to run.** Either a module you switched on has no file behind it, or every layer of rules is empty. It writes nothing rather than replace your live rules with an incomplete set.

## Contributing

**Adding a tool.** Create `<tool>/` with config files that have no leading dot (`vim/vimrc`, not `vim/.vimrc`). In `install.sh`, list its files in `links_for`, add an `install_<tool>` function, and add the tool to the default `TARGETS`, the dispatcher's `case`, and `describes_target`. If it replaces something personal, also add it to `personal_target` so it defaults to off. Update the tables above.

**Adding a rules module.** Drop a file in `ai/rules/` with a declaration on line 1:

```markdown
<!-- ai-rules: order=40, default=off, prompt="Include the review-checklist rules" -->
```

The directory is globbed, so that file is the whole change. `AGENTS.md` has the full options and the other conventions for working in this repo.

**Tests.**

```bash
python3 -m unittest discover -s ai/tests -t ai/tests
```

**Local-only overrides.** Anything named `*.local` is ignored by git. Use it for machine-specific or secret values, and have the shared config source it if it exists, as `bash/bashrc` does with `~/.bashrc.local`.

**Before pushing to a public repo**, install the pre-commit leak scanner once per clone: `leak-check install-hook`.
