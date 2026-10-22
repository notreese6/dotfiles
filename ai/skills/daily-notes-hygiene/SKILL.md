---
name: daily-notes-hygiene
description: >-
  Use to clean up a project's live rollup in the daily notes so it matches
  reality again: TODOs that are already done, duplicates, wrong or stale
  markers, In Progress items nobody has touched, report pointers that are out of
  date, and TODOs measured against the north star. Proposes every change with
  its evidence, applies only what the user approves, and never touches dated
  history. Fires on: notes hygiene, clean up the notes, current/ is stale, tidy
  the TODOs, are the TODOs up to date, groom the backlog. Its light pass runs inside
  plan-iteration's realign step and at the end of every unattended run.
---

# Daily notes hygiene

`current/<project>.md` is only useful while it is true. Left alone, it only
grows: finished work stays in it, the same TODO appears twice in different
words, and the two items that matter get lost under a dozen that don't. This
pass makes it true again.

It works only on `current/` (and today's dated file, when an item finishes
today). **Dated files are history and are never edited.**

## Procedure

### 0. Load

1. Run `daily-notes-sync pull`.
2. Resolve the project name against `current/` and `PROJECT-RENAMES.md`.
3. Read all of `current/<project>.md`, including its `## North Star`. Then read
   the dated notes since the last hygiene pass (or the last two weeks), the
   newest report folder, and the repository's recent history (`git log`, and
   merged changes).

### 1. Check every item

| Check | What it looks for | Evidence |
|---|---|---|
| **Already done** | an open item that a dated note, commit or merge shows as finished | the note line or commit, quoted |
| **Duplicate** | two items about the same thing, often with different diagnoses | both lines; keep the more accurate one and fold in what is new |
| **Superseded** | an item a later decision has made wrong | the decision, quoted |
| **Stale In Progress** | In Progress with no activity in the notes or history for more than about a week | the last date it was touched |
| **Markers** | a dated item within 7 days that is not `[!]`; a passed date not marked `OVERDUE`; too many `[!]` items; bare `- ` bullets; a list out of order | the item |
| **Vague** | an item with no way to tell when it is done | the item; propose a "done when" |
| **Closed blocker** | a Blockers row whose review, merge request, bug or ticket has merged, closed or been abandoned | the live status from that system; move the outcome to Accomplishments and drop the row |
| **Missing or bare link** | a blocker with no URL, or an entry that names a review, merge request, bug or ticket by bare ID | the full URL to put in |
| **Stale State** | a `## State` older than the last run or plan, or one that contradicts live data | the live value |
| **History in current/** | an entry carrying its own long history instead of a pointer | the dated note or report to point at |
| **Plans** | a plan still `active` whose items are all done, or older than the last run; an `Active plan:` line that names a plan that is not active; an In Progress item with no "done when"; a plan restating a shape instead of naming the item | the plan entry and the items |
| **Pointers** | a report pointer that is not the newest date folder holding that report; a dead link or path | the newer path |
| **Serves nothing** | a TODO that no part of the north star explains | the item; ask whether to drop it, or which part of the north star it serves |
| **Nothing serves it** | a part of the north star with no TODO working toward it | that part; propose the TODO |

The last two checks need a north star. If there is none, say so and skip them.
Do not invent one: it is agreed in the realign step of `plan-iteration`.

### 2. Propose

Show **one table**, grouped by the kind of change:

| # | Item (short) | Problem | Proposed change | Evidence |
|---|---|---|---|---|

Then use **AskUserQuestion** with a multi-select per group (recommended
changes first), so the user approves a group in one answer instead of
one at a time. Drops and "serves nothing" items are always asked about; they are never
applied by default.

### 3. Apply

1. Apply only what was approved.
2. Re-sort the TODO list by the daily-notes rules: `[!]`, `[>]`, `[ ]`, `[~]`;
   dated items first within each tier.
3. An item that is finished goes into the dated file for the day it actually
   finished, as an Accomplishment. If that day is not today, it goes into
   today's file with a note of when it landed. Past dated files are never
   edited.
4. Run `daily-notes-sync`. Report the count before and after, for example
   "12 open -> 9 open: 2 done, 1 duplicate".

## The light pass

`plan-iteration` runs this pass when it realigns, and `unattended-run` runs it
when a run ends. It covers only the items in question: the last run's items,
or what has moved since the last plan.

- Mark finished items done and add the TODOs that came up.
- Drop Blockers rows whose link has merged or closed. Fill in
  missing links.
- Fix markers and pointers.
- Point `current/` at the newest plan or run report.

Changes the evidence proves need no approval. Anything that needs judgement
goes to the user: duplicates where the two items disagree, drops, and items
that serve no part of the north star. In a run, nobody is there to ask, so
those wait for the next plan.

Do a full pass when the light pass keeps finding the same kind of problem,
when `current/` has more than about 30 open items, or when the user asks.
