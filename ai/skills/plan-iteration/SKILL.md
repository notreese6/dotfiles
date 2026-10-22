---
name: plan-iteration
description: >-
  Use when choosing what to work on next for a project over a stretch of time:
  an unattended run, the rest of a day, overnight, a weekend or a week. Opens
  by realigning: folds the last run's outcomes and the user's decisions into
  the notes, cleans up the live rollup, and agrees the project's north star
  (recommends it or a change to it; the user approves). Then picks the items
  that move the project furthest in the time available, says for each one what
  "done" means and what it may do without a person, and gets the plan approved.
  Fires on: make a plan, plan the run, what should we work on,
  plan the next iteration, queue up work, what can you do while I'm away,
  north star, what are we building toward.
---

# Plan an iteration

The work goes in a loop: **plan, unattended run, review, plan again.** Each
pass through the loop can leave the notes, the goal and the project a little
further apart. This skill is where they are pulled back together. Every plan
starts by realigning them, and only then chooses work.

This chooses **what** to work on. **How** to build a single item is a separate
kind of planning, done when that item starts (`superpowers:writing-plans`).
Keep them apart: an iteration plan that turns into an implementation plan
takes the whole window to write, and the run never starts.

An iteration is any stretch of work with a start and an end: overnight, an
afternoon, a weekend. Nothing here assumes a time of day.

If a private counterpart skill is installed (`unattended-run-local`), it names
one organization's systems, limits and off-limits actions. Load it too.

**No ramp-up.** Plan the full amount the time allows, from the first run. A
cautious first run that does two small things wastes a whole run.

## Standing rules (from what has made these loops drift before)

- **The repository and live systems are the truth. The notes are memory.**
  When the two disagree, fix the notes and say so.
- **Derive every number** from its source each time. Never copy one forward
  from an earlier note or report.
- **Take dates from the clock or from git**, never from an earlier note.
- **Unknowns get written down, not guessed:** `UNKNOWN -- <who> to confirm`.
- **Recommend, don't list options.** Every question to the user leads with
  the recommended option.

## 1. Realign

Run `daily-notes-sync pull`, then read all of `<notes>/current/<project>.md`.

### a. Bring in the last run

Read the newest run report under `<notes>/reports/<project>/`, if one exists.
Then check what has happened to each item since: merged, rejected, still
waiting on the user, parked. Use version control and the review
system, not the report alone. Then:

- Record each outcome in `current/` and in today's dated note. Finished items
  become Accomplishments. Rejected items get the reason, then are dropped or
  become new TODOs.
- Record each decision the user made in review under today's `## Notes`,
  as `**Decided (<user>, <YYYY-MM-DD>):**` with the reason. If a decision changes what the
  project is for, it feeds into step c.
- Questions from the report that are still open come first in the planning
  questions.

Then refresh the two live sections of `current/`:

- **Blockers.** Check each row's link against the system it points at
  (review, merge request, bug, ticket). A row that has merged,
  closed or been abandoned leaves the table. Its outcome goes in
  today's Accomplishments, which keeps the link. A row waiting more than a week
  becomes a question: nudge, escalate, or drop.
- **State.** Rewrite it from live data, not from the last State: the
  a few lines on how the project stands and where to look next, and the newest
  report. Stamp it with the date and time, and copy it into today's dated file
  under `## State`.

### b. Clean up current/

Run the light pass of `daily-notes-hygiene`, which checks for work already
done, duplicates, stale In Progress items, wrong markers and out-of-date
pointers. Apply changes the evidence proves. Put the rest to the user in the
planning questions.

When `current/` has more than about 30 open items, or the light pass finds
more than a handful of problems, recommend a full `daily-notes-hygiene` pass
before planning. A plan chosen from a list nobody trusts is a plan built on
guesses.

### c. Agree the north star

Read the `## North Star` at the top of `current/<project>.md` (see "The north
star" below).

- **One exists:** recommend either "unchanged", with one line on why it still
  holds, or a specific edit with the evidence for it: a decision from review,
  a meeting, a change of scope. The user approves or changes it. Most passes
  through the loop end at "unchanged", and that is correct.
- **None exists:** draft one from what the owners and users have said
  (meeting recaps, design docs, earlier reports), with a
  baseline for each measure taken from the project's data. Show the draft and
  write it only once the user approves.

Write any change to `current/`. Note it in today's dated note with the
reason, so the history of the goal can be traced.

Then compare the TODOs with the north star. A TODO no part of the north star
explains is a candidate to drop. A part of the north star that no TODO
serves is a gap. Both go into the planning questions. Do not label TODOs as
steps toward the north star; every TODO is one, and that is what makes it a
TODO.

## 2. Choose

Ask for the window if it was not given: when the run starts, and when the
user will be back to review. Check what the run can reach (repository state,
credentials, tools, limits on shared resources). Anything it cannot reach
drops out here, not halfway through the run.

Rank the open TODOs and In Progress items. Do not rank by size or ease.
Ranking, in order:

1. **Unblocks the user.** Anything that lets the user finish or send something
   when they are back: reviews to respond to, a fix someone is waiting on.
2. **Moves a north star measure.** Prefer the item that moves the headline
   measure most, per hour of run time.
3. **Removes recurring cost.** Something that fails or needs hand-holding every
   day.
4. **Closes a gap.** A part of the north star nothing is working on yet.

Then filter on what can actually be done unattended:

| Class | Meaning | In the plan? |
|---|---|---|
| **Run** | Can be finished and verified with no person: code on a local branch, an analysis, a report, a branch ready for review | yes |
| **Run to a gate** | Can be prepared up to one action that needs approval (a production write, a merge, a message) | yes, and it stops at the gate |
| **Needs a person** | Needs a decision or a reply before any useful work | no; it goes to the questions in step 3 |

Fill the window, then add two or three **stretch items** in ranked order, so a
run that finishes early has more work to pick up. If there is time after
that, the run spends it on `adversarial-review` of the riskiest finished items.

For each item, write:

- **Item**: the TODO, in its words from `current/`.
- **Done when**: something checkable. "Tests pass and the new check fails on the
  broken input", not "improve X".
- **Produces**: a local branch, a report, or a measurement,
  and where it will land.
- **May do without asking**: the actions the run may take on its own.
- **Stops before**: the gated action, if there is one.
- **Size**: a rough estimate in hours, and the risk that it runs over.

## 3. Get approval

Present the plan as **one table**, one row per item:

| # | Item | Why now | Done when | Produces | Stops before | Size |
|---|---|---|---|---|---|---|

Below it, list the items left out and why. Then ask with **AskUserQuestion**,
recommended option first:

- the north star question from step 1c, if there is a change;
- one multi-select for the items to run;
- one question per item that needs a decision before it can start;
- the drop candidates and cleanup changes that were not proven in step 1.

The user's answers are the approval. Nothing in the plan may need a decision
after the user has left. If it does, the decision goes into this round of
questions, or the item stops at a gate.

## 4. Record it

1. Write the approved plan to
   `<notes>/reports/<project>/<YYYY-MM-DD>/run-<HHMM>-plan.md`, using the start
   date and time.
2. In `current/<project>.md`, move the approved items to In Progress and add a
   pointer to the plan.
3. Run `daily-notes-sync`.

The run starts from this file. `unattended-run` reads it and nothing else, so
anything said during planning that the run needs must be written in it.

## The north star

The north star is where the project is going when it is finished, written so
anyone can tell whether a piece of work moves toward it. It sits at the top of
`current/<project>.md` under `## North Star`. It has four parts and nothing else:

| Part | What it says | Shape |
|---|---|---|
| **Vision** | What is true for the people it serves when the project has done its job | 2-4 sentences, present tense, as if already done |
| **Scope** | What the project covers: systems, components, teams, platforms | a short list; everything in scope stays listed, done or not |
| **Measures** | How we would know we are there | metric, baseline (value, date, source), target and the reason for it |
| **Guardrails** | What must stay true on the way | constraints the work never trades away |

The vision is about the people it serves, not the machinery. "A library
member finds and reserves any book from their phone in under a minute" is a
vision. "A mobile app backed by a search index" is how it is built.

**It never contains:**

- **TODOs, next steps, gaps, blockers, known issues, open questions.** The test
  for every line: *would it still be true and worth saying after every
  current TODO is finished?* If not, it is a TODO.
- **Carve-outs for in-scope work that is not done yet.** Something in scope
  that is not done yet is a gap, and a gap is a TODO. Exclude only what the
  project has decided never to serve, and give the reason.
- **Features or tools that are means to the end.** A mobile app or a search
  index is a TODO. Name the outcome the feature delivers instead.
- **Dates, owners, ticket IDs, names of changes.**

A measure with no baseline yet still goes in, marked `XXX - TODO: not measured
yet`, and measuring it becomes a TODO. A target needs a reason: who set it,
and what it is anchored to. Prefer scope the project can grow into: what it
does first, and the wider set it is built to serve. A north star that changes
on every pass through the loop has turned into a status update.
