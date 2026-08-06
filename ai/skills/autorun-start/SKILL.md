---
name: autorun-start
description: >-
  Session startup for an autorun (unattended-agent) box. Invoke at the start of
  every autorun session: reloads the core constraints, orients the agent, pulls
  the notes, reads every active project's current/ rollup, checks MCP and tool
  connectivity, and presents a status summary before waiting for a task. Before
  committing to a long run, runs a readiness check and holds for "go". Fires on:
  /autorun-start, start the session, are we in autorun mode, how are things looking,
  ready to go.
---

# Autorun session startup

Invoke this at the start of every session on an autorun box. It reloads the core
rules, orients the agent, checks what's reachable, and presents status — all before
doing any work.

## Core rules — re-read and hold for the whole session

These are the same constraints in `ai/autorun/autorun.md`, restated here so they
load explicitly at the top of every session.

**Never block on a human.** Nobody is watching. Do not ask clarifying questions
or wait for approval. When you hit something that needs a decision, write it as an
`[!] [AUTORUN]` TODO naming exactly what the decision is and what you would have
asked, then pick up the next piece of work that does not depend on it. An agent
that stops on a prompt does nothing until someone finds it hours later.

**Stay inside the writable workspace.** Write only to what the site rules
designate writable — typically this box's local disk (daily-notes repo, session
scratchpad). The shared home directory is read-only. Where a sandbox is active
that is enforced at the kernel; treat it as a rule regardless. Do not try to work
around a read-only path: if the work genuinely requires writing outside the
workspace, record it as a human decision and move on.

**Never publish.** The credentials on this box belong to a person. Do not push
to shared branches, submit changelists, file or comment on tickets, send chat
messages or email, or deploy anything. Prepare work to the point of
ready-to-send and record what is ready and where it lives. The one exception: the
**daily-notes-repo push specifically** is how work from this box reaches anyone —
allow it; forbid everything else.

**Never rebuild the shared rules.** Do not run `ai-rules apply` here. It rewrites
the assembled rules file that other machines read as their own instructions. If
work produces a fact that belongs in the global rules, write it into the notes as a
TODO for an interactive machine.

**Tag every note entry `[AUTORUN]`**, placed after any TODO marker:
`- [>] [AUTORUN] ...`. This separates unattended work from the human's entries in
shared notes. Tag each bullet as you write it, not in a cleanup pass.

**Memory here is local.** Agent memory on this machine stays on local disk;
nothing written here is visible elsewhere. Use it for facts about this box's runs.
Anything globally true belongs in the rules, which this box may not rebuild —
surface it in the notes instead.

## Phase 1 — Orient (run immediately on invocation)

Do this in order before anything else:

1. Check `$NV_MACHINE_ROLE`. If it is not `autorun`, say so and stop — these
   constraints are wrong for an interactive session.
2. Run `daily-notes-sync pull`. Report what came in (files changed, already
   current, or any conflict).
3. Get today's date: `date +%F`.
4. Read every file under `current/` in the notes directory. Get the full picture
   of what is in flight across all active projects before writing anything.
5. Present a status block:
   - Today's date and machine role
   - One-line summary per active project derived from the rollups
   - Any `[!]` items due within 7 days or overdue (first occurrence in this
     session per project only — do not repeat on later prompts)
   - MCP connectivity summary (see Phase 2)
6. **Stop and wait.** Do not guess at what work to do; do not start anything.

## Phase 2 — Check tool connectivity (part of Phase 1 output)

Check which MCP servers are connected vs unauthenticated and fold the result into
the Phase 1 status block as a compact table. For each dark server, say what it
would unlock if re-authed (Confluence = internal design docs, NVBugs = bug
tracker, Glean = internal search, GitLab = code review + CI, etc.). Do not block
on this — surface it once and continue.

## Phase 3 — Readiness check (when the user assigns a task)

Before committing to a long run, verify that what the task needs is actually
reachable. Present the results as a table before accepting "go":

| What | Check | Result |
|---|---|---|
| Source tree | Locate the relevant root; confirm it is present and readable | path + sync date |
| Version control reads | Confirm read-only ops work (e.g. `p4 info`, `git log`) | client / remote |
| Disk headroom | `df -h` on the writable workspace | free GB |
| Network reads | GitLab / GitHub / internal network access | reachable / blocked |
| Write paths | Confirm daily-notes and scratch dirs are writable | paths confirmed |
| MCPs this task needs | List which servers the task specifically wants; confirm status | connected / dark |

Also identify at this stage any repos worth cloning for the task (name, purpose,
proposed path on local disk). Name them explicitly and wait for approval before
cloning anything.

If something critical is missing, say so before accepting. A night wasted on a
missing credential is worse than a short pause.

## Phase 4 — Scope and confirm before starting a long run

Before starting, restate in your own words:

1. Priorities in order — what "done" looks like for each
2. Concrete methods — which source paths, which repos, which tools
3. What you cannot reach — blocked items and what would unblock them
4. Repos proposed for cloning (from Phase 3), pending approval
5. Hard constraints you will honor for this run (no submit, no push except
   daily-notes, stay in workspace, etc.)
6. **Hold for "go"** — do not start work until the user explicitly says so

Once you have "go": run until the work is exhausted or the user stops you. Update
the daily notes as findings land; never wait for the user mid-run; park any
decision that needs a human as an `[!] [AUTORUN]` TODO and keep moving.
