# Unattended agent rules

Deliberately **not** in `ai/rules/`. That directory is globbed by `ai-rules
apply`, whose output is one assembled file shared by every machine — a module
placed there would reach all of them, which is the opposite of what this file
is for. `autorun-mode` imports it directly into the unattended machine's own
agent config, so it reaches that machine only.

You are running on a box whose role marker says `autorun`. Nobody is watching
this session while it runs.

**Invoke `/autorun-start` at the beginning of every session.** It reloads the
rules below explicitly, pulls the notes, reads all active project rollups, checks
MCP connectivity, and holds for your task. That is the standard start for every
autorun session.

## Never block on a human

There is no one to answer. Do not ask clarifying questions, do not wait for
approval, and do not leave a prompt open.

When you hit something that genuinely needs a decision, **write it down and
move on** rather than guessing: record it as an `[!]` TODO naming the decision
and what you would have asked, then pick up the next piece of work that does
not depend on it.

**Why:** an unattended agent that stops on a prompt does nothing until someone
finds it hours later, and one that guesses on a real fork produces work that
gets thrown away. Recording the question keeps both the progress and the choice.

## Stay inside the writable workspace

This machine declares one tree the agent may write to; everything else,
including the home directory, is read-only. Where a sandbox is active that is
enforced by the kernel, but treat it as a rule regardless — the sandbox may be
absent on a host with no runtime available.

Do not try to work around a read-only path. If work genuinely requires writing
outside the workspace, that is a decision for a human: record it as above.

## Never publish

The credentials on this machine belong to a person, so anything sent from here
goes out under their name and cannot be quietly taken back.

Do not push to shared branches, submit changelists, file or comment on tickets,
send mail or chat messages, or deploy. Prepare work to the point of
ready-to-send and record what is ready.

The exception is the notes repository itself — pushing that is how this
machine's work reaches anyone.

## Never rebuild the shared rules

Do not run `ai-rules apply` here. It rewrites the assembled rules file that
other machines read as their own instructions, so a change made unattended
would silently replace them.

If work produces a fact belonging in the global rules, do not apply it — write
it into the notes as a TODO for an interactive machine to make.

## Tag everything written to the notes

Every bullet this machine writes under `## Accomplishments`, `## In Progress`,
or `## TODOs` starts with `[AUTORUN]`, placed after any TODO marker:

```markdown
## Accomplishments
- [AUTORUN] Re-ran the failing arm64 repro; captured the exact fetch URL.

## TODOs
- [!] [AUTORUN] by 2026-08-11 — needs a human call: the fix touches shared
      test infrastructure rather than the product branch; confirm the owner.
```

The notes are shared with the machines a human actually uses, so the tag is
what separates unattended work from theirs. Commits from here are authored
distinctly for the same reason.

**How to apply:** tag as you write each bullet, not in a cleanup pass.
Everything else in the daily-notes rules — the marker set, the sort order,
reconciling the live rollup, pulling before writing — applies here unchanged.

## Memory here is local to here

Agent memory on this machine is stored on local disk, so a memory written here
is never seen elsewhere. Use it for facts about *this* box's runs. Anything
globally true belongs in the rules, which this machine may not rebuild — so
surface it in the notes instead.
