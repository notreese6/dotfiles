---
name: unattended-run
description: >-
  Use when working through an approved plan with nobody watching: overnight,
  over a weekend, or while the user is in meetings. Starts from an approved
  plan, or makes one first with plan-iteration. Reads freely, writes only
  locally unless the plan names the network write, re-reads the plan at every
  step so it stays on course for the north star, builds each item on its own
  local branch to its agreed shape, parks anything that needs a person, and
  ends with a run report the user can review in one sitting. Fires on: run the
  plan, go, work on this while I'm away, start the run, unattended run,
  overnight run.
---

# Unattended run

The user approves a plan, leaves, and comes back to review. Between those two
points nobody answers questions, so everything here is built so that the run
never needs to ask one, and nothing it does is hard to undo.

If a private counterpart skill is installed (`unattended-run-local`), it names
one organization's systems, limits and off-limits actions. Load it too.

On an autorun box, `autorun-start` applies as well; where the two differ, its
rules win.

## The plan is the anchor

A long run outlives its own context. Details from planning get summarised away,
and a run that works from memory drifts: it widens an item, fixes something
nearby, or makes a decision the user never saw. So the plan file, not memory,
decides what happens.

**Re-read the plan file** (`<notes>/reports/<project>/<date>/run-<HHMM>-plan.md`):

- at the start of every item;
- after any context compaction or summary;
- before any action the current item's entry does not name;
- whenever the work feels like it needs something the item did not mention.

Each time, check three things. Is this inside the item's shape? Is it allowed
by the item's approvals? Does it move the part of the north star the item
serves? If any answer is no, do not do it. Write it down as a new TODO or a
question for the user, and carry on with the item as planned.

**The north star decides between options the plan allows. It never adds work
to the plan.** Something that would clearly help the north star but is not in
the plan goes in the report as a recommendation for the next plan.

Keep a short **run log** at the bottom of the run report: each item's start,
each re-read of the plan and what it changed, each checkpoint, and each thing
set aside. A run that dies leaves the trail, and the user can see whether the
plan held.

## Before starting

Do this while the user is still around if possible. A missing input found at
the start costs a minute; found halfway through the night, it costs the night.

1. **An approved plan must exist.** If there is none, run `plan-iteration` first
   and get it approved. The approval is the last decision a person makes in this
   run.
2. **Read the plan, the north star and `current/<project>.md`.**
3. **Preflight.** For every item, check what it needs and that it can be
   reached:
   - each service it reads from is signed in, or has a named fallback or "skip";
   - every input it needs is present locally;
   - the working tree is clean, and the base commit is noted;
   - disk space is enough for what it will write.
4. **Count shared limits.** For anything the plan lets the run consume (jobs,
   quota, spend), count current use against the limit and confirm the run's
   budget fits.
5. **Know the way out.** Settle the one path by which results leave this
   machine (normally the notes sync). Settle where an alert goes if something
   scheduled breaks while nobody is watching.
6. **Prove the fence.** If the run depends on the harness blocking publish,
   push or send commands, run one harmless blocked command and confirm the
   harness refuses it, not the agent. A file-system sandbox does nothing to
   stop network writes.

Anything that fails here drops its item, and the reason goes in the report.

## Access: read freely, write locally, everything else only by name

| Kind | Rule |
|---|---|
| **Reading** | Always allowed: files, repositories, logs, dashboards, databases (read-only), job status, documentation. |
| **Local writes** | Allowed inside the run's worktrees, the run's report folder and scratch space. Nowhere else. |
| **Writes over the network** | Only those the plan names for this item, exactly as named and no more often. That covers pushing, uploading or saving a change to a server, starting, re-running or cancelling jobs, database and storage writes, changing shared configuration, and anything a person would receive. Anything not named is parked as a question. |
| **Speaking as the user** | Never. Messages, comments, tickets, reviews and mail are drafted into the report for the user to send. |

The only network write that never needs naming is the notes sync, because it
is how results reach the user.

### Never, even locally

- Delete anything outside the run's own worktrees and scratch, or delete with a
  path built from a variable. List leftovers in the report instead.
- Rewrite git history, force anything, or touch `main` or any branch the run
  did not create.
- Change the machine: shell profiles, scheduled tasks, services, installed
  packages, or system settings.
- Read, print or copy a credential into a log, a file or the transcript.
- Point a test or cleanup at the user's real instance of anything (their
  terminal server, their database, their running jobs). Use an isolated one.
- Run anything that can wait on a prompt. Pass every answer up front. If a step
  stops for input anyway, kill it, log it, and move on.

### When the plan does approve a network write

- **Check before the write, not after.** Every guard that could stop the write
  runs first. A check that fires once the damage is done is a report, not a
  guard.
- **Snapshot, confirm, write, confirm.** Save the current state, check the
  snapshot matches what is live, write, then check the result.
- **Bring inputs up to date first.** Anything that ships whole files must be
  rebased or synced to head, or it silently undoes other people's work. Pass
  every target explicitly; never rely on a default client, workspace or branch.
- **Confirm it was accepted.** A tool that printed an ID and exited cleanly has
  not proved the receiving system took the work. Poll until that system says so.
- **Before pausing shared automation, list what is queued**, and restore it
  afterwards.
- **Approvals with conditions are followed to the letter.** "Do X once Y
  happens" does not happen if Y does not. Leave X ready to run and say so.

## Each item

1. **Re-read the item** in the plan: its shape, approvals, "done when" and
   time box.
2. **Check for overtaking work.** If the item depends on someone else's change
   in flight, check its status first. If that change would make this item
   redundant, record it and move on.
3. **Plan the build.** Use `superpowers:writing-plans` to turn the agreed shape
   into steps. Anything bigger than a small fix gets this. Write the plan into
   the run's report folder, not the repository. Where the shape left a choice
   open, use the default written in the plan.
4. **Build it** on branch `run/<YYYY-MM-DD>-<HHMM>/<item-slug>`, in its own
   worktree (`superpowers:using-git-worktrees`), with
   `superpowers:subagent-driven-development` and
   `superpowers:test-driven-development`. **Local commits on these branches are
   allowed without review**, because nothing on them leaves the machine. That is
   the only exception to the commit review gate. Extend existing code rather
   than writing a second version of it. Follow the user's code rules and the
   project's conventions. Where superpowers and the user's rules disagree, the
   user's rules win.
5. **Verify it like a sceptic** (`superpowers:verification-before-completion`).
   - Run the tests for what changed, and the full suite once before calling it
     done.
   - Validate against everything the change will meet later: every variant a
     scheduled job builds, not just the one in front of you.
   - Dry-run changes to automation against the real system, not only against a
     test double.
   - A claim that something is absent needs a positive control or a raw read.
     A tool that fails quietly looks exactly like "nothing there".
   - Check how old a result is before calling it stuck or missing; some systems
     are just slow to publish.
   - Keep "could not reproduce" separate from "refuted", and mark a guess as a
     guess.
   - A failure that only shows up on your change is yours until shown
     otherwise.
6. **Out-of-scope findings are recorded, not fixed.** Anything noticed outside
   the item becomes a TODO or a note in the report.
7. **Log it** in today's dated note and in `current/` as soon as it lands, and
   update the run report. Copy any evidence from systems that expire their
   logs into the report folder.
8. **Time-box it.** Every command that can hang gets a timeout. If an item has
   used twice its estimate, or the same failure has come back three times,
   stop. Record what was tried and what was learned, leave the branch, and
   move on.

When `superpowers:finishing-a-development-branch` offers to merge, push or open
a merge request, the answer in a run is always **keep the branch**.

**Order:** start the slowest external work first, so its results are in when
the user returns. Then the planned items, then the stretch items in order. If
time is left, run `adversarial-review` (change scope) on the riskiest finished
items. Fix confirmed findings that fall inside an item's shape, and report the
rest.

**When a call fails:** retry once. Then decide whether the failure is temporary
(rate limit, timeout, signed out) or permanent, and record the cheapest next
step that would work. Do not turn a single transient error into a question
for the user.

## The run report

Write `<notes>/reports/<project>/<date>/run-<HHMM>-report.md`. The date and time
are those of the plan. Start it when the first item starts, and update it after
each item, so that a run that dies still leaves a report. Write its index
before anything else lands in the folder, and keep scratch out of it. It is read
in one sitting, so keep it short.

1. **Bottom line**: two or three sentences on what landed, what needs the user,
   and anything that went wrong.
2. **Not done**: what was planned but did not happen, and why. This goes first,
   so the gaps are seen before the successes.
3. **One table, one row per item:**

   | # | Item | Result | Where | How it was verified | Needs you |
   |---|---|---|---|---|---|

   Result is one of `done`, `partial`, `stopped at gate`, `parked`, or
   `not started`. Where is the branch name or report path, with the exact
   command to see the change (for example,
   `git diff main...run/<date>-<time>/<item>`).
4. **Needs you**: each decision, with its options and a recommendation, in the
   form of an AskUserQuestion, so the user can answer them all at once. Drafts
   of anything to send go here too.
5. **What moved**: any north star measure that changed, before and after, with
   its source. If nothing could be measured, say so.
6. **Not verified**: anything the run could not check against a live system,
   and every guess, labelled as one.
7. **Left behind**: files, branches, jobs still running, and when to look at them.
8. **Run log**: from "The plan is the anchor".

**End with a realign**, so the next plan starts from notes that match reality:

1. Run the light `daily-notes-hygiene` pass over the items this run touched.
2. Make sure every item's state in `current/` matches the report, and that the
   TODOs the run uncovered are added. Add a Blockers row, with its link, for
   everything the run left waiting on a person. Write anything the run learned
   the hard way under today's `## Notes` as `**Learned:**`.
3. Rewrite `## State` in `current/` from live data, stamped with the date and
   time, and copy it into today's dated file.
4. Point `current/` at the report and run `daily-notes-sync`.

The review that follows feeds the next `plan-iteration`, whose first step
brings this report's outcomes back into the notes.

## When the user comes back

Start with the run report. When the user says "MR this" or "merge this" about a
branch, the normal commit and review rules apply again from that point: show
the diff and the message, and wait.
