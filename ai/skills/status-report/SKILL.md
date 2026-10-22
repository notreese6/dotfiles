---
name: status-report
description: >-
  Use when writing a "where things stand" report about a project for managers
  and other teams: a status update, an impact summary, a project review, or a
  monthly or quarterly update.
  Digs through notes and data for what the project was, what changed, the
  numbers before and after, who uses it, why it matters to the organization,
  and what comes next, then writes a long report and a short mail from the
  same facts. Fires on: status report, status update, where things stand,
  impact report, monthly update, update for my manager, write up the project,
  how far we've come.
---

# Status and impact reports

A status report is read by people who were not in the work. Most of them read
one paragraph and one table. So the report has two jobs, in this order: make the
change and its value obvious in the first screen, and back every claim with a
number and a source for the few who keep reading.

If a private counterpart skill is installed (`status-report-local`), it adds one
organization's house format, vocabulary, goals and audience. Load it too.

## What makes these fail

- **Organised by activity instead of outcome.** "This month I worked on A, B and
  C" makes the reader do the work of deciding what it means. Lead with what is
  different now and why anyone should care.
- **No before.** "Search answers in 300 ms" means nothing alone. "1.2 s in one
  region -> 300 ms in all four regions" lands.
- **Numbers without a source or a denominator.** They get quoted back, and the
  first one that turns out wrong discredits the rest.
- **Impact that is claimed rather than shown.** "Improves quality" is a slogan.
  "Caught a double-charge bug in staging three weeks before it would have
  reached customers" is evidence.
- **Too long in the mail.** Past two screens, readers stop at the summary. The
  long version belongs on a linked page.

## Procedure

### 0. Confirm the window and the north star -- recommend, then ask

Two things decide what goes in and how every number reads, and both are the
author's call, so ask before gathering anything. Give a recommendation with each
and the reason for it, so the answer can be one word.

- **The window the report covers.** Usually the reporting period, or everything
  since the last report. Look for the last report first and say when it was.
  Every "before" number has to sit at the start of that window.
- **The north star.** The outcome the project exists to deliver and the target it
  is measured against. Read it from the `## North Star` section of
  `<notes>/current/<project>.md`. If there is none, offer to agree one first (the
  realign step of `plan-iteration`) rather than inventing one for the report. The mission line, the
  "where we are" numbers and the "why it matters" section all come from it, and
  every "Next" step comes from the open TODOs in `current/`.

### 1. Learn the house format before writing a word

Read a few reports this audience already likes and match their shape; readers
parse a familiar shape faster. Note what the good ones share and what the weak
ones do wrong. Save what you learn as a study next to the report, so the next report
starts from it.

### 2. Gather the facts, every one with a source

Write a facts file before the report. Each fact gets where it came from (a note
date, a query, a link, a document). Cover:

| Area | What to find |
|---|---|
| Starting point | What existed at the start of the window, and what was broken |
| Timeline | Dated milestones from the notes: first working version, each big expansion, when manual steps became automatic |
| Before -> after | The same measures at both ends: reach (users, teams, regions), speed, cost, error rate, effort saved |
| Accomplishments | The big things that landed, each with its number and scope (who and what it reached) |
| Who uses it | Teams and people using it today and what they get; who could use it next |
| Goals | The project's north star and targets (with the reason for each target), the managers' goals, the organization's goals in its own words |
| Bottom line | Cost removed, hours saved, problems caught early, risk reduced -- only what can be shown |
| Next | Next steps with the month each is expected, longer-term direction, what would unlock more value |
| Asks | Decisions, approvals or help needed, from whom, by when |
| Gaps | Everything you could not verify, so the report does not imply it |

Sources, in order of trust: data you can query, dated notes, tracker items, the
current code and configuration, then memory. Read the notes in full for the
period, not the last few days -- the starting point is the part most often lost.

### 3. Write the long report

Saved where the notes rules put reports. Structure:

1. **Title** in the house format, with the reporting window.
2. **Mission** -- one sentence: the outcome the project exists to deliver, and
   for whom.
3. **Where we are** -- one paragraph: where it started, where it is now, the
   headline number, why it matters to the organization's goal, and the one thing
   needed from the reader. Write this last.
4. **At a glance** -- a Before | Now | Change table, 4-8 rows, units and dates on
   every number.
5. **Highlights** -- a handful at most: what changed, its number, who did it,
   and the evidence. A long list means it has not been prioritised yet.
6. **How we got here** -- a short dated timeline. A first report earns its keep here:
   it records the starting point while someone still remembers it.
7. **Who uses it, and who can** -- teams, what they get, and the next adopters.
8. **Why it matters** -- tie to the organization's goals in their own words, with
   one or two concrete examples.
9. **What's next** -- items tagged by state, each with the month it is expected, plus the north-star target
   and why that target.
10. **Actions and decisions** -- the asks (owner, what, by when), the decisions
    already made and why, and the ones still pending. A reader should be able to
    act on this block without reading the rest.
11. **Risks and blockers** -- each with an owner and what would unblock it.
12. **Appendix** -- method, definitions, the sources table, what could not be
    verified.

### 4. Write the short mail from the long report

If there is a longer version, link it near the top. Two screens at most:
title, mission, the "where we are" paragraph, the at-a-glance table, the
highlights with one line each, actions and decisions, references. Nothing in the
mail that is not in the long version. If the asks are the point of the mail, put
them first as well.

### 5. Tailor per reader, without forking the facts

Different readers care about different rows: a skip-level manager about the
organization's goals and cost, a direct manager about targets, owners and risks,
a partner team about what they can use and how to start. Keep one set of facts;
reorder or add a short "for you" section rather than writing separate reports
that can drift apart.

## Rules for the numbers

- Before and after, with the change: `12,000 -> 18,000 items (+50%)`.
- A denominator whenever there is one: `412 of 1,000`, not `41.2%` alone.
- A date on every number, and the window it covers.
- Say where a number came from when it is not obvious: measured, queried,
  computed or estimated. An estimate labelled as one is useful; one that reads as
  measured is a liability.
- Ranges and floors beat invented precision: `20+`, `~3x`, `at least a day`.
- Never round in the direction that flatters.
- **Measure what the reader experiences, not what the system adds up.** For speed,
  that is how long until a recipe's text appears on screen, not the total server
  time of every request the page makes, which no person ever waits for.
- **ETAs in a report are a month, never a day** (`ETA March`, not `ETA 3/14`). A
  day-level ETA reads as a commitment, and it goes stale the day it slips. Dates of things that already happened, and fixed external deadlines, stay
  exact. This is for reports; elsewhere a real date is fine.

## Rules for impact

The point of the report is to show that the work made a difference. That only
works if it is believable.

- **Show the reach you can point at, not the reach you can imagine.** "The four
  teams that use it today" beats "every restaurant in the chain". Potential reach is a
  forecast; label it as one.
- **One concrete example beats three adjectives.** A specific problem caught, a
  specific hour saved, a specific team unblocked.
- **Connect to the goal the reader already has.** Find the organization's stated
  goals and targets, and use their words. A target is stronger with its reason.
- **Credit others by name for their part.** It is accurate, and it makes the
  rest of the claims more credible.
- **State misses and open risks plainly.** A report with no problems in it reads
  as incomplete, not as successful.
- **Understate rather than overstate.** An entry that reads smaller than the
  work costs a little; one that reads bigger costs the credibility of every other
  line.

## Formatting that survives mail clients, forwarding and wikis

- **Name what the reader gets, not how it was built.** No merge or pull requests,
  commits, branches, file paths or script names in a report that goes beyond the
  people working in the repo: say what the capability is and what changed. Link only
  what a reader must act on (a review to approve) or open (a dashboard, the page of
  record). A link into a private repo or personal notes is a dead link to them.
- **A link that does not exist yet is an `XXX - TODO` placeholder** saying what will
  go there (`Full write-up: XXX - TODO: link once the page exists`), never a
  guessed URL, a private link standing in for it, or a bare `<fill in>`. A reviewer can
  find every one before the report goes out by searching for `XXX - TODO`.

- Bold or capitalised section labels; a numbered list for the top items.
- Tables of five columns or fewer.
- Status as bracket tags (`[Done]`, `[In progress]`, `[At risk]`, `[Blocked]`),
  never colour alone.
- Full raw URLs, never masked links -- forwarding mangles masked links, and the
  reader wants to see where a link goes.
- Nothing that exists only in a screenshot.
- Expand every acronym at first use; the reader may not share the team's
  shorthand.

## Before it goes out

- [ ] Every number has a date and a source, and a denominator where one exists.
- [ ] The first paragraph alone answers: what changed, why it matters, what is
      needed.
- [ ] The Before | Now table compares the same measure at both ends.
- [ ] Nothing unverified is stated as fact; the gaps are listed.
- [ ] Names, teams and their credit are right.
- [ ] The mail is two screens or less and links the full report.
- [ ] The author sends it. Drafts are shown, not sent.
