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
  Plans a day worked together as well as an unattended run, and never starts
  the work itself. Fires on: make a plan, plan the day, plan the run, what should we work on,
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

**Open with one AskUserQuestion holding these questions, each with its own
options**, so they are answered together:

1. **How the plan will be worked:** together, unattended, or together and then
   unattended. Exactly those three, with no times attached. A plan worked
   together skips the run-only parts (approved network writes, limits, alerts,
   preflight), because the user is there and the normal rules apply.
   Everything else is the same.
2. **When the work starts:** now, at a stated later time, and so on. Options
   are relative to now ("now", "in an hour"); the exact time goes in the
   free-text answer.
3. **When it ends and the user reviews it:** for example in a few hours,
   tomorrow, or after the weekend, with the exact time in the free-text answer.
4. **When work hands over to the run** (only for together and then
   unattended).

The timeframe options never assume a time of day from the clock, such as
"overnight" or "until morning". The user states the window, and the plan
records it in their words.

**This skill never starts work.** It ends once the plan is recorded. An
unattended run is started separately with `unattended-run`, which confirms the
plan's scope with the user before it begins.

**Where things live.** The work itself is the In Progress list in
`current/<project>.md`; each item there carries its shape. The plan is an entry
under `## Plans` in today's dated file: which In Progress items, in what order,
how they will be worked, and the approvals. Nothing is written twice.

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

- **One exists:** check what has been said since it was agreed (meetings,
  chats, decisions), then recommend either "unchanged", with one line on why it
  still holds, or a specific edit with the evidence for it: a decision from
  review, a meeting, a change of scope. The user approves or changes it. Most passes
  through the loop end at "unchanged", and that is correct.
- **None exists:** draft one from what the owners and users have said. That
  means meeting transcripts and recaps, chats, and the design and program
  pages they wrote, read again for this draft rather than recalled. Earlier
  reports come after those. Meetings and what people have communicated carry
  the most weight; the notes and the code show what was done, not what was
  wanted. When the material is large, research it in the background first.
  Take a baseline for each measure from the project's data. Where the owners
  disagree or have said nothing, keep that out of the north star and raise it
  as a TODO. Show the draft and write it only once the user approves.

Write any change to `current/`. Note it in today's dated note with the
reason, so the history of the goal can be traced.

Then compare the TODOs with the north star. A TODO no part of the north star
explains is a candidate to drop. A part of the north star that no TODO
serves is a gap. Both go into the planning questions. Do not label TODOs as
steps toward the north star; every TODO is one, and that is what makes it a
TODO.

## 2. Choose

Use the timeframe from the opening questions. Check what the run can reach
(repository state, credentials, tools, limits on shared resources). Anything it
cannot reach drops out here, not halfway through the run. Check the window
against the user's availability too: their calendar, and anything they have
said recently about being away. A review time they cannot keep is not a window.

### Take an inventory first

The TODO list is one source of work, not the only one. Before ranking, collect
candidates from all four:

1. **What the user owes other people**: replies, documents, reviews, reports
   and decisions someone is waiting on, with their due dates. Look in recent
   notes, meeting recaps and messages, not only in the TODOs.
2. **What runs or is scheduled during the window**: jobs, scheduled runs,
   deliveries and results that will land. Each one needs someone to notice if it
   goes wrong.
3. **Decisions waiting on the user**: the Blockers on them, and any question
   left open in State, the notes or an earlier plan.
4. **The open TODOs and In Progress items.**

**Check cheap facts now.** When a quick read-only check could show that an item
is already done, not needed, or a different size, do it while planning. An
answer found halfway through the run is an item the run should never have had.

### Rank

Do not rank by size or ease. Ranking, in order:

1. **Unblocks the user.** Anything that lets the user finish or send something
   when they are back: reviews to respond to, a fix someone is waiting on.
2. **Commitments the user owes**, by due date, overdue first.
3. **Moves a north star measure.** Prefer the item that moves the headline
   measure most, per hour of run time. **Check the claim before ranking on it:**
   follow the item's output to the measure and confirm it actually changes it.
   An item that does not move a measure is upkeep or a guardrail; say so, and
   rank it as one.
4. **Removes recurring cost.** Something that fails or needs hand-holding every
   day.
5. **Closes a gap.** A part of the north star nothing is working on yet.

**Anything that runs during the window gets watched.** When the inventory found
scheduled or running work, the plan includes a read-only watch item: check
times taken from the schedules, what counts as healthy, and that problems are
recorded rather than fixed.

Then filter on what can actually be done unattended:

| Class | Meaning | In the plan? |
|---|---|---|
| **Run** | Can be finished and verified with no person: code on a local branch, an analysis, a report, a branch ready for review | yes |
| **Run to a gate** | Can be prepared up to one action that needs approval (a production write, a merge, a message) | yes, and it stops at the gate |
| **Needs a person** | Needs a decision or a reply before any useful work | no; it goes to the questions in step 3 |

### Lay it out against the clock

For each item, note what it needs as input and when that input exists: a job
that has to finish, results that land at a known time, an answer from another
item. Order the items by when they can start, with the slowest outside work
started first. An item placed before its input exists does its work on
incomplete data.

Then check capacity: add up the estimates, and the waits between them, against
the window. If the plan does not fill it, keep adding from the ranked inventory.
Then add two or three **stretch items** in ranked order, so a run that finishes
early has more work to pick up. If there is time after
that, the run spends it on `adversarial-review` of the riskiest finished items.

For each item, write:

- **Item**: the TODO, in its words from `current/`.
- **Done when**: something checkable. "Tests pass and the new check fails on the
  broken input", not "improve X".
- **Produces**: a local branch, a report, or a measurement,
  and where it will land.
- **Reads**: what the run may read. Reading is always allowed; list it so the
  run knows where to look.
- **Writes over the network**: every action that changes something beyond this
  machine's working copies. That covers pushing, uploading or saving a change
  to a server, starting or cancelling jobs on shared systems, database or
  storage writes, and anything sent to a person. Name each one and how many.
  Anything not named here is not allowed.
- **Stops before**: the gated action, if there is one.
- **Size**: a rough estimate in hours, and the risk that it runs over.

### Shape what gets built

A TODO says what is wrong or missing. It does not say what to build. An item
that builds or changes something needs a **shape** agreed before the run, so
the run builds what the user wants, the way the user wants it.

For each such item, work it out with the user. This is the same ground
`superpowers:brainstorming` covers, condensed into this one planning sitting,
because nobody will be there to ask during the run.

| Part | What it settles |
|---|---|
| **Purpose** | which part of the north star it serves, and what is different for someone when it is done |
| **What gets built** | the pieces, where each one lives, and how they connect to what exists |
| **Reuse first** | the existing code, module or tool it extends rather than replaces. Building a second version of something that exists needs a stated reason. |
| **Not built** | what is deliberately left out of this item, so the run does not widen it |
| **Decisions** | each choice that changes what gets built, as a question with options and a recommendation. Choices left to the run are written down with the default it will use. |
| **How we will know** | the "done when", stated as something a reviewer can run |

Small fixes need no shape: the "done when" is enough. When a shape grows past
about a screen, the item is too big for one run. Split it, or make "shape it"
the item.

The run builds to the shape. A decision it needs that the shape did not make
is parked for the user, not made on the spot.

## 3. Get approval

**Review the draft before showing it.** Read it as a stranger would and ask:
does every commitment due in or soon after the window have an item or a reason?
Is everything running in the window watched? Does each item's input exist by the
time it starts? Does each "moves a measure" claim hold? Is the window full? Is
every open decision either answered by the plan or in the questions below? Is
the review time one the user can keep? Fix what fails, then present it.

Present the plan as **one table**, one row per item:

| # | Item | Why now | Done when | Writes over the network | Stops before | Size |
|---|---|---|---|---|---|---|

Below it, list the items left out and why. Then ask with **AskUserQuestion**,
recommended option first:

- the north star question from step 1c, if there is a change;
- one multi-select for the items to run;
- the shape decisions for each item that builds something;
- every write over the network the plan asks for, so each one is approved by
  name;
- the drop candidates and cleanup changes that were not proven in step 1;
- the run's limits: how much of each shared resource it may use, measured
  against what is already in use, and what to free up first;
- where an alert goes if something scheduled breaks while nobody is watching,
  and the one path by which results leave the machine.

The user's answers are the approval. Nothing in the plan may need a decision
after the user has left. If it does, the decision goes into this round of
questions, or the item stops at a gate.

## 4. Record it

1. **In `current/<project>.md`:** move the approved items into In Progress,
   in order, each with its "done when" and, if something will be built, its
   shape indented under it. Put the stretch items at the top of TODOs as
   `[>] stretch`. Set State's `Active plan:` line.
2. **In today's dated file, under `## Plans`:** add the plan entry. If an
   earlier plan is still active, mark it `replaced by HH:MM`.

   ```markdown
   ### 18:00 — unattended — active
   Window: 18:00 – 08:00 (user back 08:30) · agreed 17:40 by the user
   Items, in order: 1. <In Progress item>  2. <In Progress item>
   Stretch: <TODO>, <TODO>
   Writes over the network: 1. <item>: <what>, <how many>  2. none
   Stops before: 1. <action>
   Limits: <resource> <n> of <limit> · Alerts: <where> · Results leave via: notes sync
   ```

   A plan worked together needs only the first three lines.
3. **Decisions** made while planning go under today's `## Notes` as
   `**Decided (<user>, <YYYY-MM-DD>):**`.
4. Run `daily-notes-sync`.

Anything said during planning that the work needs must be written in one of
those places. `unattended-run` reads them and nothing else.

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
