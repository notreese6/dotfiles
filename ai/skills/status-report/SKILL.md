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
  how far we've come, update since our last one-on-one, a short list for a
  wide audience, full project update.
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
- **The wrong length for the reader.** A wide audience that does not know the work stops reading after two screens, so the long version belongs on a linked page. People who work in the area want the detail: cutting the hard problems to one line each makes the work look smaller, not clearer.

## Procedure

### 0. Confirm the purpose, the audience, the window and the north star -- recommend, then ask

Four things decide what goes in, how deep it goes and how every number reads. All four
are the author's call, so ask in one message before gathering anything, with a
recommendation and its reason for each, so the answer can be one word each.

- **The purpose and the reaction wanted.** What the report is for (inform, show what a body of work achieved, ask for a decision, build adoption) and what the reader should think or do afterwards. A report meant to show what the work achieved is a story of change and who benefits, not a neutral status; settling this first changes what is selected.
- **The audience.** Who reads it, what they already know, what they decide or do
  with it, and where it will be sent. The profiles below give the defaults. If the
  author names a group or mailing list, find the last report that went to that
  audience (see "Where it goes") rather than guessing. If the readers include the
  author's own organization, find how that organization uses the work.
- **The window the report covers.** Usually the reporting period, everything since
  the last report, or since the last one-on-one with the reader (find that date in the
  calendar or notes), or the whole life of the project. Say when the last report was.
  Every "before" number has to sit at the start of the window.
- **The north star.** The outcome the project exists to deliver and the target it
  is measured against. Read it from the `## North Star` section of
  `<notes>/current/<project>.md`. If there is none, offer to agree one first (the
  realign step of `plan-iteration`) rather than inventing one for the report. The mission line, the
  "where we are" numbers and the "why it matters" section all come from it, and
  every "Next" step comes from the open TODOs in `current/`.

**Audience profiles.** Pick one, then adjust. The facts are the same for all of them;
the depth, the vocabulary and the lead are not.

- **Whole project, full update** (a new owner, a milestone, a handover): window is
  the whole project. Tell it as a story in chapters: the situation before, the problem,
  what was done, the result. Long form, with the full numbers.
- **Manager, since the last one-on-one** (technical): window is since that meeting.
  Lead with what was accomplished and what it changes for the manager's goals; give the
  mechanism (what was found, how it was fixed), the numbers with denominators, the
  risks and the decisions needed. Technical vocabulary is fine.
- **Wide audience that knows nothing about it** (a top-five list for a whole
  organization): at most five headlines in plain words, each saying what changed, why
  it matters to the reader, and one before-and-after number. No internal names,
  tools, paths or acronyms the reader has not met. Short.
- **A known team or list** (a regular status mail): lead with what changed and who it
  helps, show how in two or three examples, say who uses it, what is next and how the
  reader can help. Medium length, light jargon. A wide list gets direction, not status: leave out blockers,
  named individuals and anything not yet decided. That detail belongs in the one-on-one or the notes.

### 1. Read the whole project first, whatever the window

The window decides what is reported as new. It does not limit what is read. Before
writing anything, read **all of the following for the whole project, outside the window
too**, and write down what was read:

- **Every meeting and one-on-one record** (recaps and transcripts), not only recent
  ones. What the readers say they care about, in their words, is the most important
  input: it tells you which items to lead with and why they matter. Collect, per
  person, what they care about, what they asked for, what they would count as a win, and
  what they pushed back on, with dated quotes.
- **Every accomplishment recorded since the project began, read in full.** Not the
  first line of each: the best ones are found in the detail (the number, the cause, what was
  fixed and how), and a truncated read misses them. On a long project, extract them with a
  script into one file per date range and give each range to a parallel reader that returns every
  entry with a before-and-after number, a root cause or a new capability, quoted with its date. Then
  read those returns yourself and pick the strongest. Record the count read against the count that
  exist. The window is then applied to this set, so the starting point, the chain of causes
  behind each gain and the things that went wrong are not lost.
- **The last reports sent to this audience, and the replies**, to see what landed.
- **The decisions already recorded** (the `Decided` entries in the notes): the headline measure, what to leave out, what wording the author has ruled out. They override your defaults. When the author states a decision in conversation, record it in the notes so the next session finds it.
- **The north star and any targets with their reasons.**

**Start this as soon as the audience is known, in the background while other work goes on.** It is the slowest step and the one most often skipped. Read the primary record, not only recaps: a recap is someone's paraphrase, and the strongest claims (who uses the work and why, what someone asked for, what was decided) need the original words. The newest record wins: where a later meeting changed a plan, the earlier note is history.

Save a context file next to the report listing: what was read (counts), what could not
be read (access denied, not recorded) and what that leaves open, and the per-person
summary. Do not write the report from the window alone, and do not start the outline until this file exists.

### 2. Learn the house format before writing a word

Read a few reports this audience already likes and match their shape; readers
parse a familiar shape faster. Note what the good ones share and what the weak
ones do wrong. Save what you learn as a study (a section of the context file is enough),
so the next report starts from it. If this audience has no earlier report, say so, and use
the closest one you can find.

### 3. Gather the facts, every one with a source

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

**Show how, not only how much.** For each gain, record: the situation before (with
the number and date), the problem and its cause in plain words, what was done, and the
result (with the number and date). A reader who sees the mechanism believes the number;
a bare "more is covered" is a claim. The most convincing items are specific: one test
that had nothing and now has something, one failure that used to be silent and is now
loud.

**Keep a list of claims to soften or leave out.** Check each headline number for these
before it is used, and write the safer wording beside it:

- a figure that bundles several changes (use a single-change figure);
- a before or after that includes things outside the compared set, or a comparison between
  things that are not alike;
- a recovery presented as growth;
- a result measured on one item, stated as a whole-system effect;
- "first ever" when it is only the first in one context;
- use or adoption claimed with no recorded user;
- any cost, hours saved or count of manual steps that is not in the sources;
- two definitions of one measure mixed in one series;
- superlatives and claims of uniqueness that the sources do not support, and a true figure
  framed as a shortfall (lead with the gain and put the overlap or the gap in a note);
- a baseline or headline taken from a different definition or period than the
  rest of the report, or one that does not match what the reader can check elsewhere;
- a target stated without the measure it applies to;
- a plan stated as decided, a "coming soon", or a use described that the person never confirmed.

Sources, in order of trust: data you can query, dated notes, tracker items, the
current code and configuration, then memory. Read the notes for the
whole project, not the last few days -- the starting point is the part most often lost.

### 4. Sort the facts, then agree an outline before drafting

Mark every fact as **story** (what changed, how it was done, who benefits, where it is going) or **tracking** (current status, blockers, who is waiting on whom, requests to named people, problems of the last day or two). A report for a broad list is built from story only. Tracking belongs in the one-on-one, the notes or a direct message; in a broad mail it makes the work look smaller.

Then show the author a short outline before writing the long version (two outlines, one led by the story and one by the table, when the audience has no earlier report to copy): the headline, the one or two stories that carry it (each with its sources), the direction in a few lines, and the readers' own use. It takes minutes to approve, and every change after that is wording instead of substance.

### 5. Write the long report

Saved where the notes rules put reports. Structure:

1. **Title** in the house format, with the reporting window.
2. **Mission** -- one sentence: the outcome the project exists to deliver, and
   for whom.
3. **Where we are** -- one paragraph: where it started, where it is now, the
   headline number, why it matters to the organization's goal, and the one thing
   needed from the reader. Write it last and place it first.
4. **At a glance** -- a Before | Now | Change table, 4-8 rows, units and dates on
   every number, so a skimmer gets the result without reading further.
5. **Where it started, and why it changed** (a whole-project update) -- the situation
   before with its numbers, the problem and what it cost, and why the change was made,
   in the reader's terms. Then the work and its result, chapter by chapter.
6. **Highlights** -- a handful at most: what changed, its number, who did it,
   and the evidence. A long list means it has not been prioritised yet.
7. **How we got here** -- a short dated timeline. A first report earns its keep here:
   it records the starting point while someone still remembers it.
8. **Who uses it, and who can** -- the readers' own organization first, then partner teams, then others, each use told as a need, a response and a result (see the impact rules), and the next adopters.
9. **Where to look** -- when the report points at a dashboard, data or tool: the links, what each one answers, how to drill in, and how long each kind of detail is kept.
10. **Why it matters** -- tie to the organization's goals in their own words, with
    one or two concrete examples.
11. **What's next** -- direction first (see the impact rules), plus the target and why that target.
12. **Actions and decisions** -- only when the report exists to ask for something: the asks (owner, what, by when), the decisions made and pending.
13. **Risks and blockers** -- only for a reader who can act on them, each with an owner and what would unblock it.
14. **Appendix** -- the definitions, and where a reader can check each figure (a dashboard or page they can open). Provenance only the author can open (notes, internal paths) and what could not be verified go in a separate section addressed to the author and marked not to send: readers cannot open those, and a link they cannot follow is worse than none.

### 6. Write the short mail from the long report

If there is a longer version, link it near the top. Length follows the reader. For a wide
audience that does not know the work, two screens at most: title, mission, the "where we
are" paragraph, the at-a-glance table, the highlights with one line each, references. For a
team that works in the area, as long as the reader keeps gaining from it: the headline, a compact
before-and-after table and the direction on the first screen, and the hard problems told with their mechanism.
The first screen says what it was, why it changed (a sentence or two on what was wrong before), and what it is now. A mail that exists to inform carries no offers and no requests; being helpful is implied by the work. The mail may carry a subset of the long report's rows, with the same numbers. Nothing in the mail that is not in the long version. If the asks are the point of the mail, put
them first as well.

### 7. Tailor per reader, without forking the facts

Use the audience profile from step 0 to set depth, vocabulary and the lead. Keep one set
of facts; reorder, shorten or add a short "for you" section rather than writing separate
reports that can drift apart. When one set of facts has to serve two audiences (a
detailed update for the manager and a five-line version for the wider list), write the
detailed one first and derive the short one from it, using only claims that survived the
soften list.

### 8. Where it goes

Find the distribution the last report to this audience went to: search the mailbox for
that report and read its To, Cc and Bcc, and look for the page of record it links.
Propose that list and ask the author to confirm. If none is found, say so, then propose one
from the author's own organization (its reporting lines) plus the people the records show the
author discussed the work with, label it a proposal, and ask the author to confirm. Note other groups the author receives related mail from, as
candidates, without claiming they are the right ones.

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
- **Be humble, and credit others for their specific part.** Name the person and what
  they did ("designed the original approach", "suggested the change that unblocked
  the work"), once, in a sentence or two after the results, not a list of every name
  and not before the work. Thank people for design, unblocking and sustained help, not for
  routine duties, and do not credit anyone in a way that makes the author's own work look
  smaller. Take the credit that is due without superlatives, and say plainly when a miss
  was the project's own. Collect who helped, and how, during the whole-project read so the
  thanks come from the record, not from memory.
- **Pick the hard problems.** Readers who know the field respect problems that were hard: a design that had to satisfy several constraints at once, a scaling limit found and removed, data that would otherwise have been lost. They discount a one-line fix however much time it cost. For each highlight ask whether an expert in the area would call it hard, and drop the ones that would not.
- **Tell each use as a need, a response and a result.** Someone had a need, it was met quickly with a small change that also helped others, and the result is reusable. Do not say what someone could not do, and do not list their requests as requests. The reader should finish thinking "we could use that too" without being asked. The pattern: not "A group made two requests; both are answered", but "A group needed something, got it quickly in a form others can reuse, and the result is available to anyone with a similar need."
- **Direction, not status, for what is next.** Each next step is one sentence of direction followed by two to four concrete examples. Say "we expect" rather than give a schedule unless a decision with a date is recorded. Add no new baselines or numbers here, and name a target only for a measure whose target someone with authority has set, saying who set it. Avoid deficit wording ("not there yet"): lead with what exists and say where it goes.
- **Trace every claim about a person, a team or a plan to what they said or decided**, the way a number traces to its source. A recap is the author's paraphrase, so check it against the original before relying on it. Do not state what someone chose or prefers unless those are their words; describe what they do with the work. An inference goes to the author as a question, not into the report.
- **State misses plainly, and scope them to the reader.** A report with no problems in it reads
  as incomplete, not as successful. Say in a line or two what the project itself broke and has closed. In the long report, list open risks that a reader can act on. Open defects, unresolved blockers and problems that may be gone tomorrow stay out of a broad mail.
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
- Refer to people by full name, and avoid assuming pronouns.
- Full raw URLs, never masked links -- forwarding mangles masked links, and the
  reader wants to see where a link goes.
- Nothing that exists only in a screenshot.
- Expand an acronym at first use unless every reader uses it daily; a reader outside the
  team may not share its shorthand, and expanding the team's own terms reads as odd.

## Before it goes out

- [ ] The audience, window and depth were agreed, and the whole project (meetings,
      accomplishments, past reports) was read, with what was read recorded.
- [ ] Every number has a date and a source, and a denominator where one exists.
- [ ] The soften list was applied: no bundled, inflated or one-job number is stated as general.
- [ ] The first paragraph alone answers: what changed, why it matters, what is
      needed.
- [ ] The Before | Now table compares the same measure at both ends.
- [ ] Nothing unverified is stated as fact; the gaps are listed.
- [ ] Names, teams and their credit are right.
- [ ] A broad mail contains story only: no blockers, no today's problems, no asks aimed at named people.
- [ ] Every claim about a person's use or a plan traces to what they said or decided, newest record first.
- [ ] An outline was agreed before the long draft, and the draft was read once as each type of reader on the list: would anyone be misdescribed, or find nothing in it for them?
- [ ] The length fits the reader (two screens for a wide audience, more for a team that works in the area, with the headline and the table on the first screen).
- [ ] Nothing in what is sent points at something the readers cannot open (notes, internal paths, private links).
- [ ] The recipients were confirmed against a past report to this audience.
- [ ] The author sends it. Drafts are shown, not sent.
