---
name: unattended-run
description: >-
  Use when working through an approved plan with nobody watching: overnight,
  over a weekend, or while the user is in meetings. Starts from an approved
  plan, or makes one first with plan-iteration. Builds each item on its own
  local branch, logs as it goes, ends with a realign,
  never publishes, parks anything that needs a person, and ends with a run
  report the user can review in one sitting. Fires on: run the plan, go,
  work on this while I'm away, start the run, unattended run, overnight run.
---

# Unattended run

The user approves a plan, leaves, and comes back to review. Between those two
points nobody answers questions, so everything here is built so that the run
never needs to ask one, and nothing it does is hard to undo.

If a private counterpart skill is installed (`unattended-run-local`), it names
one organization's systems, limits and off-limits actions. Load it too.

On an autorun box, `autorun-start` applies as well; where the two differ, its
rules win.

## Before starting

1. **An approved plan must exist.** Look for today's
   `<notes>/reports/<project>/<date>/run-<HHMM>-plan.md`. If there is none, run
   `plan-iteration` first and get it approved. The approval is the last
   decision a person makes in this run.
2. Read the plan, the north star, and `current/<project>.md`.
3. Confirm the working tree is clean. Note the base commit that each item will
   start from.

## The rules for the whole run

**Never block on a person.** When an item needs a decision the plan did not
make, record the question with its options and a recommendation under "Needs
you" in the run report. Then stop that item and move to the next one. Never
guess at an answer that would be hard to undo.

**Never publish.** No pushes and no merges to shared branches. No merges,
tickets, ticket comments, chat messages, emails or reviews. Prepare everything
up to the point where it is ready to send. The run report says what is ready
and where. Pushing the notes repository with `daily-notes-sync` is the only
exception.

**Git: one local branch per item.** Branch
`run/<YYYY-MM-DD>-<HHMM>/<item-slug>` from the base, in its own worktree
(`superpowers:using-git-worktrees`). **Local commits on these branches are
allowed without review**, because nothing on them leaves the machine. That is
the only exception to the commit review gate. The review happens when the user
asks to merge or open a merge request from a branch. Never commit to `main` or
any other branch, and never push.

**Shared resources only as the plan allows.** Anything that costs money, uses
someone else's capacity, or writes to a production system happens only if the
plan names it, and only as much as the plan names.

**Gates hold.** An item whose plan says "stops before X" stops before X, even
when everything is green and X looks safe.

## Each item

1. **Plan the build.** Use `superpowers:writing-plans` for anything bigger
   than a small fix. Write the implementation plan into the run's report folder,
   not into the repository: a plan committed to a repository becomes a document
   nobody asked for.
2. **Build it.** Use `superpowers:subagent-driven-development` and
   `superpowers:test-driven-development`, following the user's code rules and
   the project's conventions. Where superpowers and the user's rules disagree,
   the user's rules win.
3. **Verify** with `superpowers:verification-before-completion`. Run the tests
   for what changed, and the full suite once per item before calling it done.
   An item is done only when its "done when" holds and the evidence is in hand.
4. **Log it** in today's dated note and in `current/` as soon as it lands, as
   the daily-notes rules require. Do not save it up for the end.
5. **Time-box it.** If an item has used twice its estimate, or the same failure
   has come back three times, stop. Record what was tried and what was learned,
   leave the branch as it is, and move on.

When `superpowers:finishing-a-development-branch` offers to merge, push or open
a merge request, the answer in a run is always **keep the branch**.

When the planned items are done, start on the stretch items in order. If time
is left after those, run `adversarial-review` on the riskiest finished items,
fix what it confirms, and put what is still open in the report.

## The run report

Write `<notes>/reports/<project>/<date>/run-<HHMM>-report.md`. The date and time
are those of the plan. Start the report when the first item starts, and update
it after each item, so that a run that dies still leaves a report. It is read
in one sitting, so keep it short.

1. **Bottom line**: two or three sentences on what landed, what needs the
   user, and anything that went wrong.
2. **One table, one row per item:**

   | # | Item | Result | Where | How it was verified | Needs you |
   |---|---|---|---|---|---|

   Result is one of `done`, `partial`, `stopped at gate`, `parked`, or
   `not started`. Where is the branch name or report path,
   with the exact command to see the change (for example,
   `git diff main...run/<date>-<time>/<item>`).
3. **Needs you**: each decision, with its options and a recommendation, in the
   form of an AskUserQuestion, so the user can answer them all at once.
4. **What moved**: any north star measure that changed, before and after, with
   its source. If nothing could be measured, say so.
5. **Not verified**: anything the run could not check against a live system.

**End with a realign**, so the next plan starts from notes that match reality:

1. Run the light `daily-notes-hygiene` pass over the items this run touched.
2. Make sure every item's state in `current/` matches the report, and that
   the TODOs the run uncovered are added. Add a Blockers row, with its link,
   for everything the run left waiting on a person. Write anything the run
   learned the hard way under today's `## Notes` as `**Learned:**`.
3. Rewrite `## State` in `current/` from live data, stamped with the date and
   time, and copy it into today's dated file.
4. Point `current/` at the report and run `daily-notes-sync`.

The review that follows feeds the next `plan-iteration`, whose first step
brings this report's outcomes back into the notes.

## When the user comes back

Start with the run report. When the user says "MR this" or "merge this" about a
branch, the normal commit and review rules apply again from that point: show
the diff and the message, and wait.
