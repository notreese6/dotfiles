---
name: status-report
description: >-
  Use when writing a "where things stand" report about a project for managers
  and other teams: a status update, an impact summary, a project review, or a
  monthly or quarterly update.
  Digs through notes and data for what the project was, what changed, the
  numbers before and after, who uses it, why it matters to the organization,
  and what comes next, then writes the update in the form the author chooses
  (a few spoken minutes in a meeting, a message to one person, an email to a
  team, a company-wide post) from one set of facts, with an author-only
  evidence file beside it. Fires on: status report, status update, where things stand,
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

## Core rules (re-read before writing and again before sending)

1. **Accuracy first.** Every claim traces to the record, and a separate reader checks each one (step 6).
2. **Sell with evidence.** Before and after, the mechanism, the hard problems, who benefits; no adjectives doing the work of evidence.
3. **Every reader finds what is in it for them,** limited to reach you can point at.
4. **Altitude.** Story and direction for a broad audience: no blockers, today's problems, identifiers (ticket and change numbers, test names, release numbers, product codenames), sizes, or asks for work or anyone's time.
5. **Fit the form, the length and the window.** The length the author chose (step 0) holds; failing that, the form sets it (spoken: about three minutes and at most three numbers; email: about 1,000 to 1,500 words, with at most about one number per 15 words and a dozen exact dates). Every "before" is at the window start, or is the nearest earlier figure, dated.
6. **People.** Their own words or a recorded decision; the weakest verb the record supports; specific, humble credit.
7. **Plans are directions, not promises.** Nothing unscheduled is stated as expected.
8. **Read the whole project and the recorded decisions first,** keep an evidence file, and send nothing with a placeholder or a link readers cannot open.
9. **The author sends; the agent never does, for any form.** Do not send, post, schedule or save a draft in any mail or chat tool, whatever the form or length (a spoken script and a one-line direct message included). The deliverable is a file shown to the author.
10. **When rules collide, this order wins:** accuracy and recorded decisions; then the chosen length (or the form's guide); then the required pieces (reader benefit, credit, where to look), cut to a clause each if needed; then the strict reader's marks. A private skill's house format, for the audiences it lists, sets the sections and their order; these rules still govern what goes inside them.

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

### 0. Confirm the purpose, form, length, audience, window, north star and what to leave out -- recommend, then ask

Seven things decide what goes in, how deep it goes and how every number reads. All seven
are the author's call, so ask in one message before gathering anything, with a
recommendation and its reason for each, so the answer can be one word each. A light read of `current/` and the last report to the audience is allowed first, to ground the recommendations. When the author cannot be asked, record the answers as assumptions at the top of the evidence file and continue.

- **The purpose and the reaction wanted.** What the report is for (inform, show what a body of work achieved, ask for a decision, build adoption) and what the reader should think or do afterwards. Name the reader types (the people doing the work, their team, managers, the wider organization, the company) and, for each, how the work helps them: every reader should be able to see what is in it for them, and come away informed, impressed by the work and curious to use it. A report meant to show what the work achieved is a story of change and who benefits, not a neutral status; settling this first changes what is selected.
- **The form.** A few spoken minutes in a meeting, a message to one person, an email to a team, or a company-wide post. It sets structure (step 7) and the default length.
- **The length, and how skimmable.** Length: short (about 300 words: the headline and a few bullets), standard (the form's guide in step 7), or long (the holistic picture: more chapters, the hard problems at full length). Reading mode: skim-first (every item opens with a bold headline that states the outcome, so the headlines alone carry the story, with bullets under them and a table or bulleted measures for the numbers) or read-through (the same headlines, each followed by a short paragraph). The two are independent. The shorter or more skimmable, the harder the delete test in step 4: keep only the details that carry a headline. The longer, the more hard problems keep their mechanism. The number and date budgets in step 7 scale with the length chosen. Recommend a pair from how the last report to this audience was read (replies, forwards).
- **What to leave out for this audience.** Parts of the true story this audience should not carry: what the project replaced, its own infrastructure history, fixes to its own earlier mistakes, experiments that did not become the product. Recommend from the readers' recorded view (a reviewer's steer, the last reply). A part that is left out is replaced by at most a clause where the reader still needs it ("now collected nightly" in place of the history of what it replaced), and wording that implies the omitted part goes too. Leaving something out never licenses a false statement: the accuracy rules apply to what remains.
- **The audience.** Who reads it, what they already know, what they decide or do
  with it, and where it will be sent. The profiles below give the defaults. If the
  author names a group or mailing list, find the last report that went to that
  audience (see "Where it goes") rather than guessing. If the readers include the
  author's own organization, find how that organization uses the work. Set the
  technical depth as one of four levels: no context (plain words, no internal
  names); an adjacent team (their own terms, the mechanism in a clause); works in
  the area (the constraint and mechanism of each hard problem, numbers with
  denominators); a peer expert (the constraint, the alternatives rejected and why).
  Depth sets vocabulary and how much mechanism each story gets; it never changes
  which facts are true.
- **The window the report covers.** Usually the reporting period, everything since
  the last report, or since the last one-on-one with the reader (find that date in the
  calendar or notes), or the whole life of the project. Say when the last report was.
  Every "before" number has to sit at the start of the window. When no figure exists at the start, describe the starting state in a sentence and date any later "before" figure; never imply it is the start. Prefer the nearest recorded figure before the start, labelled with its date, over a figure from the middle of the window; a figure from before the start is fine when the same definition applies.
- **The north star.** The outcome the project exists to deliver and the target it
  is measured against. Read it from the `## North Star` section of
  `<notes>/current/<project>.md`. If there is none, offer to agree one first (the
  realign step of `plan-iteration`) rather than inventing one for the report. The mission line, the
  "where we are" numbers and the "why it matters" section all come from it, and
  every "Next" step comes from the north star and recorded decisions (open TODOs are candidates; one they do not back goes to the author as a question).

**Audience profiles.** Pick one, then adjust. The facts are the same for all of them;
the depth, the vocabulary and the lead are not.

- **Whole project, full update** (a new owner, a milestone, a handover): window is
  the whole project. Tell it as a story in chapters: the situation before, the problem,
  what was done, the result, in the default shape of step 5 ("where it stands and how we got here"). Length per the length chosen in step 0 (about 1,200 words for a standard team email), with the full numbers.
- **Manager, since the last one-on-one** (technical): window is since that meeting.
  Lead with what was accomplished and what it changes for the manager's goals; give the
  mechanism (what was found, how it was fixed), the numbers with denominators, the
  risks and the decisions needed. Technical vocabulary is fine. Put first the decision that matters most to the manager's goals, directly under the table; small items go below it or out. A recommendation is the author's: label it as such, and when the author gave none, list the decision with its options and the record's facts and offer no recommendation. Length is about that of a team update: mechanism and numbers instead of breadth.
- **Wide audience that knows nothing about it** (a top-five list for a whole
  organization): at most five headlines in plain words, each saying what changed, why
  it matters to the reader, and one before-and-after number. No internal names,
  tools, paths or acronyms the reader has not met. Short: about 150 to 300 words in all, with a table of at most three rows or none, one line of credit and one pointer; past 300 words a wide audience stops reading; the word limit counts the body, not the subject line or links.
- **A known team or list** (a regular status mail): lead with what changed and who it
  helps, show how in two or three examples, say who uses it, what is next and where to look or
  who to ask (only when a link or owner exists). Medium length, light jargon. A wide list gets direction, not status: leave out blockers,
  asks (core rule 4) and anything not yet decided. Naming people for credit, or as users of the work, is expected. The rest belongs in the one-on-one or the notes.

### 1. Read the whole project first, whatever the window

The window decides what is reported as new. It does not limit what is read. Before
writing anything, read **all of the following for the whole project, outside the window
too**, and write down what was read:

- **Every meeting and one-on-one record** (recaps and transcripts), not only recent
  ones. What the readers say they care about, in their words, is the most important
  input: it tells you which items to lead with and why they matter. Collect, per
  person, what they care about, what they asked for, what they would count as a win, and
  what they pushed back on, with dated quotes; keep it to about five lines per person.
- **Every accomplishment recorded since the project began, read in full.** Not the
  first line of each: the best ones are found in the detail (the number, the cause, what was
  fixed and how), and a truncated read misses them. On a long project, extract them with a
  script (writing to the session's scratch directory) into files of about 100 entries each (split on entry boundaries outside code blocks, and do not cap the number returned per file; a sub-bullet belongs to its entry) and give each file to a parallel reader that returns every
  entry with a before-and-after number, a root cause or a new capability, quoted with its date. Then
  read those returns yourself and pick the strongest. Readers may share one read-only extract and write nothing but their return. Give every reader the same brief: for each entry a verbatim quote, the date and file, the figure with its denominator, whether it was later corrected, retracted or superseded (with the later date), who is credited, and a count of entries read; re-check each quote you use against the original. Record the count read against the count that
  exist, and explain any difference from a count the author gave (merged entries, empty ones, headlines). An entry is one dated bullet under Accomplishments; its sub-bullets belong to it. The window is then applied to this set, so the starting point, the chain of causes
  behind each gain and the things that went wrong are not lost.
- **The last reports sent to this audience, and the replies**, to see what landed. An unsent draft or a report to a different audience shows what the author has said; use it to check, never as a source.
- **The decisions already recorded** and the author's recorded statements (the `Decided` entries and any other lead-in the notes use for the author's statements; read the whole Notes section of each recent day, not only the lines that start with `Decided`): the headline measure, what to leave out, what wording the author has ruled out. They override your defaults. When the author states a decision, or a fact about who uses the work and what it is for, record it in the notes with the date, marked as the author's statement, so the next session can use it as a source; write it only when the author actually said it (an inference is a question, not a statement). A use or plan with no source in the record and no statement from the author goes to the author as a question. A recorded decision on what to include or omit, or on the headline measure, binds the update on what it decides (a headline figure, what to omit); choices it did not make, such as the shape for a different form, follow the audience profile; it binds even when the figure is hard to re-derive: if a decision names the figures to include, include them, and apply the delete test (step 4) to everything else. Never substitute another figure for a decided headline: use the decided one and list the conflicting reading as a before-sending item; use the note's own wording as the source.
- **The north star and any targets with their reasons.**

**Start this as soon as the audience is known, in the background while other work goes on.** It is the slowest step and the one most often skipped. Read the primary record, not only recaps: a recap is someone's paraphrase, and the strongest claims (who uses the work and why, what someone asked for, what was decided) need the original words. The newest record wins: where a later meeting changed a plan, the earlier note is history.

Start the evidence file next to the update, listing in its context section: what was read (counts), what could not
be read (access denied, not recorded) and what that leaves open, and the per-person
summary. Do not write the report from the window alone, and do not start the outline until this file exists. Keep the evidence file in this order: assumptions, before-sending items, context (what was read and not read, the per-person summary), the format study (step 2), the outline (step 4), the facts with their sources (step 3), claims with their supporting quotes, claims softened or left out, unverified items, verifier rounds, strict-reader scores; create it with the assumptions, the context and the before-sending items before the outline, and add the claims and quotes as step 6 produces them. There is one evidence file: the facts file (step 3), the format study (step 2) and the context are sections of it.

### 2. Learn the house format before writing a word

Read a few reports this audience already likes and match their shape; readers
parse a familiar shape faster. Note what the good ones share and what the weak
ones do wrong. Save what you learn as a study (a section of the evidence file is enough),
so the next report starts from it. If this audience has no earlier report, say so, and use
the closest one you can find. If the author names a draft they like, use its shape, never its facts.

### 3. Gather the facts, every one with a source

Write a facts file before the report (it may be a section of the evidence file). Each fact gets where it came from (a note
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
| Next | Next steps (a month only where a dated decision records one), longer-term direction, what would unlock more value |
| Asks | Decisions, approvals or help needed, from whom, by when |
| Gaps | Everything you could not verify, so the report does not imply it |

**Show how, not only how much.** For each gain, record: the situation before (with
the number and date), the problem and its cause in plain words, what was done, and the
result (with the number and date). A reader who sees the mechanism believes the number;
a bare "more is covered" is a claim. The most convincing items are specific: one test
that had nothing and now has something, one failure that used to be silent and is now
loud.

**Keep a list of claims to soften or leave out** (in the evidence file, list the claims you left out as well as the ones you softened; start from any recorded list of claims not to make, and use a listed figure only when the reason it is listed does not apply). Check each headline number for these
before it is used, and write the safer wording beside it:

- a figure that bundles several changes (use a single-change figure);
- a before or after that includes things outside the compared set, or a comparison between
  things that are not alike;
- a recovery presented as growth;
- a result measured on one item, stated as a whole-system effect;
- "first ever" when it is only the first in one context (say "the first on this platform");
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
current code and configuration, then memory. Recaps and drafts are leads, not sources, until checked against a dated note or the original. Read the notes for the
whole project, not the last few days -- the starting point is the part most often lost.

**The facts file is a bank of options, not the outline.** Make it cover everything important about the project, including what this update will leave out, because feedback, a different audience or a change of headline later means picking from it instead of re-reading the record. For each fact keep: the claim with its definition, the source and date, whether it was checked against the original or carried from a note, the safe wording (and wording to avoid), which audiences or forms it suits, and whether the current update uses it. Group the facts by theme, so a pivot is a quick pick, and give the history and the open tracking items their own groups marked as not for a broad audience, so they are findable but never leak into one. Record the open definition questions (for example, a figure whose denominator differs between two sources) beside the facts they affect. Keep it after the update is sent: a revision starts from it, changes the update's wording from it, and records what changed and why in the evidence file. New facts (a meeting, a data pull) are added to it with their source before they reach the update, so a figure never enters the update without a row in the file.

### 4. Sort the facts, then agree an outline before drafting

Mark every fact as **story** (what changed, how it was done, who benefits, where it is going) or **tracking** (current status, blockers, who is waiting on whom, requests to named people, problems of the last day or two). A report for a broad list is built from story only. Per-item counts, incident detail and operational mechanics are tracking unless they explain something the reader will see. Test each sentence: if the reader's belief or decision would not change were it deleted, cut it. Definitions and reconciliations between two figures go in the evidence file; the update gives the headline's definition in one clause. Tracking belongs in the one-on-one, the notes or a direct message; in a broad mail it makes the work look smaller. The outline names the headline, the stories and the direction; the opening paragraph is written from it after the body.

Then apply the leave-out setting from step 0: delete each part of the story the author said this audience should not carry, keep at most a clause where the reader still needs it, and cut any wording that implies it.

Then show the author a short outline before drafting (two outlines, one led by the story and one by the table, when the audience has no earlier report to copy): the headline, the one or two stories that carry it (each with its sources), the direction in a few lines, and the readers' own use. It takes minutes to approve, and every change after that is wording instead of substance. When the author cannot be asked (an unattended or test run), record the outline as an assumption in the first lines of the evidence file and treat the recorded `Decided` entries as the agreed outline.

### 5. Write the update

The deliverable is the update in the form the author chose, saved under `reports/<project>/<date>/` as the notes rules put reports. Before drafting, read step 7 (the form's length and shape) and the impact rules below; the delete test is in step 4. Write a separate long report only when a page of record will be published or the audience asks for depth; otherwise the evidence lives in the author-only file and the update stands alone. The structure below suits a written update; a spoken one keeps the order and cuts to the headline, one or two stories and the direction. For a whole-project update, tell the work once, as chapters with the dated timeline folded in, instead of repeating it as separate Highlights and How-we-got-here sections; keep Who uses it separate. The required pieces (reader benefit, where to look, credit) are a line or two each: fold them into the sections they belong to instead of adding blocks, so the update stays inside its length guide. The structure below is the full menu, not a list of required blocks. A whole-project team update uses the default shape below ("where it stands and how we got here"), where the table is optional. For any other team email of about 1,200 words the default is: the opening paragraph, a table of four to six rows, each a result the readers care about and never a milestone date (a table counts toward both the number and the date budget), four or five chapters of about 100 words each, who uses it with each reader's benefit, where to look, what is next, and credit.

The menu:

1. **Title** in the house format, with the reporting window.
2. **Mission** -- one sentence: the outcome the project exists to deliver, and
   for whom. Fold it into the first sentence of the opening paragraph or the paragraph after it, not a block of its own, so the
   first screen holds the headline, the result and where it is going.
3. **Where we are** -- the opening paragraph, three sentences: what it is and where it started, the
   headline result with its number, and where it is going; why it matters to the organization's goal
   goes in the paragraph after it. It carries a request only when the update's purpose is a decision
   (step 0). Write it last and place it first.
4. **At a glance** -- a Before | Now | Change table, 4-6 rows (a wide post: three at most, or none), units and dates on
   every number, so a skimmer gets the result without reading further. Where a row has no like-for-like start, give the "before" as a short phrase for the starting state instead of a number, or leave the row out; never fill a cell with "n/a". For a window with no start figure, a table is optional: a wide post uses headlines with one number each instead. A row measured on one job or test is allowed when it is labelled as such. A comparison of two runs that ran different things says what each ran, in the row, or is left out. A list of what produced a gain includes only changes that landed between the "before" and "now" measurements; list later changes separately as later.
5. **Where it started, and why it changed** (a whole-project update) -- the situation
   before with its numbers, the problem and what it cost, and why the change was made,
   in the reader's terms. Then the work and its result, chapter by chapter.
6. **Highlights** (omit when the work is told as chapters) -- a handful at most: what changed, its number, who did it,
   and the evidence. A long list means it has not been prioritised yet.
7. **How we got here** (omit when the timeline is folded into the chapters) -- a short dated timeline. A first report earns its keep here:
   it records the starting point while someone still remembers it.
8. **Who uses it, and who can** -- the readers' own organization first, then partner teams, then others, each use told as a need, a response and a result (see the impact rules), and the next adopters.
9. **Where to look** -- when the report points at a dashboard, data or tool (use the links the author gave or the newest record shows as current; an older note's link may have been replaced; when a link's title is unconfirmed, describe it neutrally rather than guessing a label; every link the author gave or recorded that the readers can open belongs in this section, and one they cannot open becomes a before-sending item): the links, what each one answers, how to drill in, and how long each kind of detail is kept.
10. **Why it matters, for each reader** -- for each type of reader named in step 0, the sentence that says how this helps them: the people doing the work, their team, managers and their goals, the organization and the company. Use their own terms, one concrete example each where you can, and only reach you can point at.
11. **What's next** -- direction first (see the impact rules), plus the target and why that target.
12. **Actions and decisions** -- only when the report exists to ask for something: the asks (owner, what, by when), the decisions made and pending.
13. **Risks and blockers** -- only for a reader who can act on them, each with an owner and what would unblock it.
14. **Appendix** (when the update stands alone, put each definition inline where the term first appears and keep the rest in the evidence file) -- the definitions, and where a reader can check each figure (a dashboard or page they can open). Provenance only the author can open (notes, internal paths) and what could not be verified go in the evidence file, never in the update file: readers cannot open those, and a link they cannot follow is worse than none.

**The default shape for a whole-project team update: "where it stands and how we got here".** Use it when the audience is a team that works in the area and the window is the whole project. Every section opens with a bold headline sentence that states the outcome, with bullets under it (in read-through mode, a short paragraph under each headline), and the headings name the move, not the topic.

1. **Where it stands.** The snapshot: what it is, the headline result with its number and date, and the north star with its target, so the first screen says where it is and where it is going. In skim-first mode the top-level measures go here as bullets.
2. **Why we [left / replaced / built] <the before>, and what we got.** Name the move in the heading. Each bullet is a bold headline, then the before with its number and date, what it cost, what was done, and the like-for-like result. If nothing was replaced, use "Why we built this": the need and what exists now, with no comparison. This section goes when the leave-out setting says to omit what the project replaced; the one clause the reader still needs moves into the first section.
3. **How we got <the gain>.** Three to six bullets (the length setting decides how many), each a hard problem: a bold headline naming the problem solved ("Getting the data back out"), then the constraint, why it was hard, what fixed it and the number. Choose by the hard-problem test.
4. **Who is using it.** Need, response, result for each use, the readers' own organization first.
5. **Where to look.** Links the readers can open and what each answers.
6. **Thanks.** Once, specific, and before what's next.
7. **What's next.** Direction first, then two to four examples, from the north star and recorded decisions.
8. **How you can help.** Up to three general invitations that point at something that exists (open the dashboard and look at your own area; say what looks wrong or should not count). No asks aimed at named people and no requests for reviews, time or work on in-flight changes: those go to the people concerned directly. Leave the section out when the purpose is not adoption or feedback.

The Before | Now table is optional in this shape, because the first section's bullets carry the headline numbers. Other audiences keep the menu above.

An invented example of the finished shape, for a team email (about 1,100 words in full):

> Subject: Upload service: failures down 96% since March
> Hi all, since March the upload service has gone from losing 1 upload in 14 to 1 in 400, and it now runs a nightly check that tells us the same day if that slips. [an optional table, five rows: failed uploads, large-file failures, retry time, nightly check coverage, support tickets; each Before | Now | Change with its week or month in the row label.] Large files were the main cause: a failed upload restarted from zero, so a 2 GB file could fail the same way three times. Saving progress after each confirmed chunk removed that failure class, which was 3.2% of all uploads. [two more problems told the same way, then who it helps by reader type, where to look, the direction, and one line of thanks naming what each person did.]

### 6. Verify every claim before it goes out

A draft carries claims the sources do not support: a wrong cause, a plan stated as agreed, an ask credited to the wrong person, a figure from a different run, a piece of work described as something it is not. Reading the draft yourself does not find them, so a separate reader checks every claim against the original sources.

- **The brief.** Give the reader the finished draft, the sources and a claims table. The table lists every sentence of the draft that states a number, date, name, use, plan, cause or table-row label (an id and the sentence); sentences about the update itself (what follows, what is left out) are not claims. The reader also returns any such sentence the table left out. Standard brief: "Draft and claims table below. Read only <the allowed paths>. For each claim return its id and one verdict with the verbatim quote, file and line: SUPPORTED; PARTIAL (say which part is unsupported); NOT SUPPORTED (say what the source says instead); or UNSOURCED (a framing sentence about the author's own view, which needs a source or goes to the author). List any claim-bearing sentence missing from the table. End with exact counts, which you recount yourself. Write nothing else."
- **Where it may read.** The dated notes, `current/`, the named source files, the update's own file, the author's recorded statements, and plain-text copies of non-file sources (mail, query output) saved in the scratch directory. The skill files and the evidence file are not sources, and records of other projects can be skipped once their titles show that. A figure from a live query the notes never recorded is UNSOURCED: save the query output to the scratch directory, or cut the figure. Give every reader and verifier this same confinement and the same no-writing rule; record any breach in the evidence file, because the verdicts stand only if nothing from outside was used.
- **What to check beyond the quote.** For each table row: its label word by word against the source's own description of the figure (what it measures, the run type, the date, the scope), and that the before and the now measure the same quantity in the same units. For each claim about a person: word by word against what they said or what the record shows they did. For every absolute claim (every, never, always, only, first, all, "does not ... when"): a search for a counterexample. A single run or period stated as the current state is a dated observation. A projection or design estimate is not a measurement: label it or leave it out. Never state why a person acted or asked unless they said so. Describe what a piece of work does from its own record (its title and description), not from nearby entries; when you cannot, describe it at the level you can. When the record does not settle a target, state it as the author's stated direction, not as someone else's commitment.
- **Acting on the verdicts.** Correct each NOT SUPPORTED claim to what the source says, or delete it. When in doubt, leave it out: a PARTIAL claim is cut back to the part that is supported, not reworded around the gap. Re-open the original for every quote you rely on (or a stated sample on a large set) and confirm that its number and scope match the claim. Keep the quotes in the evidence file.
- **Rounds and stopping.** On a large claim set, split the table across several readers by section; a round is one pass over all changed claims. After the first full run a round re-checks only the claims that were added or reworded, including any new wording a weakening edit introduces; a pure deletion needs no round. Stop when a round returns no NOT SUPPORTED, PARTIAL or UNSOURCED claim, or after six rounds. A claim still unsupported at that point is deleted and the deletion is recorded in the evidence file; the writer may not set a finding aside as "structural" unless it names no claim.

Save the update to its own file and give the strict reader that file. Then a second separate reader, who has not seen the evidence file, reads the update as each type of reader and as a strict editor and marks it from 1 to 10 on: accuracy; fit to the audience, window and form; selling with substance; altitude; structure for the form; claims about people; credit and humility; and what each reader gets out of it, each judged against the matching core rules rather than its own taste. Give it the form, the audience profile and this skill's length, number and date guides so it marks against them instead of setting its own; tell it that for a team that works in the area the mechanism of a hard problem is wanted and is not an altitude fault, while blockers, today's problems, identifiers and sizes are. Word and number counts exclude the subject line and links, and follow the counting rule in the rules for the numbers. It sees only the update, so its accuracy and claims-about-people scores are impressions (the verifier's quotes are the proof). It returns each score and, for the two lowest, the sentences that cause them. Fix those sentences and read once more; any claim added or reworded after this reader goes back through the verifier. A recorded decision outranks this reader's altitude and people marks: list the conflict as a before-sending item. A claim stripped of an identifier stays checkable: keep the identifier in the evidence file. Where its altitude mark conflicts with "tell the mechanism", keep the mechanism to the one or two plain sentences that make the problem's difficulty clear. Scores mean: 6 needs edits, 7 is good, 8 is ready to send, 9 is strong. Stop after two fix cycles (read, fix, read, fix, read: three reads at most); the update is ready to show the author when the verifier's last round returned no unsupported claim, no dimension is below 7 and altitude is at least 8 (the accuracy mark is advisory; the verifier's quotes are the proof); otherwise it is shown with what remains as before-sending items. Either way state the before-sending items in the reply to the author, not only in the evidence file: the author decides and sends.

### 7. Fit the update to its form

A spoken update is about three minutes, which is 400 to 475 words at 150 words a minute: write short lines to speak from, not paragraphs. Give the headline, one or two stories with one number each and at most three numbers in all, rounded (counted as in the rules for the numbers). A usable shape is: one opening sentence with the headline and its number; story one in three short lines (the problem, what we did, the result); story two the same; one line per kind of listener on what it gives them; one line of direction; one line of thanks. A closed miss is one short line, not a story, and with no like-for-like before you state the result without a change figure; keep raw counts, identifiers, sizes and file or bug numbers for the evidence file; end with the direction. An email has its subject on the first line of the file, then a greeting and a sign-off in the author's voice; a post or a spoken update does not. Keep the first paragraph to the headline, the result and the direction, and move scope definitions and quotes lower. A direct message is a few lines: the headline, the one thing that matters to that person, and a link to a page they can open, or none. It keeps the whole-project read, the evidence file, the verifier and the strict reader: only its length is short, and a short message still states claims that need the project's context. An email or post follows the structure above. If there is a longer version, link it near the top. Length follows the reader. For a wide
audience that does not know the work, the wide-audience shape from the profile in step 0: about 150 to 300 words, at most five headlines, a table of at most three rows or none, one line of credit, one pointer. For a
team that works in the area, as long as the reader keeps gaining from it: the headline, a compact
before-and-after table and the direction on the first screen, and the hard problems told with their mechanism. As a guide, a written update to such a team runs about 1,000 to 1,500 words with at most about one number per 15 words (about 80 in 1,200 words) and about a dozen exact dates; a draft above that reads as a log, so keep the number that carries each story and move the rest to the evidence file. Give two or three hard problems the room they need, three or four sentences each: the symptom, why it was hard, what fixed it, the number. Keep the opening paragraph to three sentences (what it is, the headline result, where it is going) and put the reason for the change in the next paragraph; past that, cut detail, not stories: drop byte counts, version numbers and per-item tables the reader does not need to follow the argument, and keep a few dated milestones instead of a long timeline.
The first screen is the opening paragraph and the paragraph after it: what it was, why it changed (a sentence or two on what was wrong before), and what it is now. A mail that exists to inform carries no offers and no requests; being helpful is implied by the work. The one exception is the "How you can help" section of the default shape in step 5, limited to what that section allows. A length chosen in step 0 replaces the form's guide above, and the number and date budgets scale with it (about one number per 15 words and a dozen exact dates per 1,200 words). An update whose purpose includes decisions (a manager's update) lists the decisions needed, each with its options and the author's recommendation (when the author gave none, the options and the record's facts only), but still does not ask for work from others. Mechanism means what was found and how it was fixed, in the reader's terms, not file names or change numbers. Pointing readers at a dashboard or data is a pointer, not an offer. A path for readers to use the work (where to look, who to ask) is fine when it points at something that exists; an offer to do work for them, or a request for their time, is not. Where no how-to or link exists, say what exists today and do not imply an invitation: a use path counts only if it has a link or an owner the readers can open. When a long report exists, the update may carry a subset of its rows, with the same numbers, and nothing the long report lacks. If the asks are the point of the mail, put
them first as well.

### 8. Tailor per reader, without forking the facts

Use the audience profile from step 0 to set depth, vocabulary and the lead. Keep one set
of facts; reorder, shorten or add a short "for you" section rather than writing separate
reports that can drift apart. When one set of facts has to serve two audiences (a
detailed update for the manager and a five-line version for the wider list), write the
detailed one first and derive the short one from it, using only claims that survived the
soften list.

### 9. Where it goes

Before an update goes beyond the author's own team, the author clears the wording and the list with their manager, and with the manager's chain when the readers reach it. Name who to clear with in the evidence file's before-sending items. Reading the mailbox to find the list is as far as the mail tools go: never send, post or save a draft there (core rule 9).

Find the distribution the last report to this audience went to: search the mailbox for
that report and read its To, Cc and Bcc, and look for the page of record it links.
Propose that list and ask the author to confirm; the author's own statement of where it goes is enough, flagged for a check against reporting lines when no past report exists. If none is found, say so, then propose one
from the author's own organization (its reporting lines) plus the people the records show the
author discussed the work with, label it a proposal, and ask the author to confirm. Search results can be much larger than asked: read subjects first and cap how many messages you open. Note other groups the author receives related mail from, as
candidates, without claiming they are the right ones.

## Rules for the numbers

- **Counting.** Word and number counts exclude the subject line and links. A before-and-after pair counts as one number. Exact dates are counted separately (a dozen in a team email), including those in table cells; a month or a plain "since" is not an exact date. In a spoken update, dates, item counts and names do not count as numbers. Every guide that gives a count (core rule 5, steps 5 and 7, the strict reader) uses this rule.
- Before and after, with the change: `12,000 -> 18,000 items (+50%)`.
- A denominator whenever there is one: `412 of 1,000`, not `41.2%` alone. In a spoken update a ratio such as `1 in 14 to 1 in 400` stands in for it, and the raw counts stay in the evidence file.
- A date on every number, and the window it covers. In prose give the month or a plain "since" and keep exact dates for a table or the evidence file; dates orient the reader and must not turn the update into a log.
- Say where a number came from when it is not obvious: measured, queried,
  computed or estimated. An estimate labelled as one is useful; one that reads as
  measured is a liability.
- Ranges and floors beat invented precision: `20+`, `~3x`, `at least a day`.
- Never round in the direction that flatters.
- **A claim of absence needs a search.** "No figure was recorded" or "nobody outside has used it" is stated only after a search under more than one term finds nothing; a future event (a meeting, a release) is stated only if the record has it.
- **A comparative word needs both figures.** "Barely moved", "steady" and "up" are stated only with the before and the now on one basis; otherwise leave the word out.
- **One basis at both ends.** Read the before and the now from the same source and the same query or dashboard; a change computed across two bases (for example a dashboard figure against a stored total) is wrong even when each end is right.
- **No delta across definitions.** When the start of the window has no like-for-like figure because the definition changed, do not claim a change across the two: use the nearest like-for-like pair (same method, same day) and say so, or state the result without a before.
- **A figure from a dashboard you cannot open** is sourced by the dated note that records it.
- **Comparing an old system with a new one.** The "before" is the old system's last or best like-for-like reading, labelled with its date and what it ran. Use one run type for the headline and the table unless the row label states the difference.
- **A unit the source never states.** Use the source's own words, or drop the figure.
- **A figure given two ways.** When the notes give one figure two ways, state the better-sourced one and put the conflict in the evidence file.
- **One headline per measure.** Choose the figure the reader can open and check, or the one the notes record as decided, and give any second definition as a second figure with its definition in a clause. When a recorded decision and the latest data disagree, keep the decided figure as the headline, give a newer reading on the same definition only as a dated second figure, and list the difference as a before-sending item. If a decided figure cannot be reproduced, use it, label its source, and list the mismatch the same way.
- **Measure what the reader experiences, not what the system adds up.** For speed,
  that is how long until a recipe's text appears on screen, not the total server
  time of every request the page makes, which no person ever waits for.
- **ETAs, only where a dated decision records one, are a month, never a day** (`ETA March`, not `ETA 3/14`). A
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
- **Show each reader what is in it for them.** Readers act on what touches them. For every reader type, name the way the work makes their own work, their team's goals or the company's outcome better, in their terms. The aim is that each reader finishes thinking the work is useful to them and impressive. Benefits follow the same rule as numbers: state the reach you can point at, and label anything potential as potential. Do not skip a reader type because its benefit is not measured yet: say what is measured and what it enables.
- **Credit what has landed, within the window.** Work still in review is not credited as delivered, and in a windowed update credit goes for work done in the window unless the update covers the whole project. A later observation that contradicts a result (a regression, a lost job) goes in the same sentence as the result.
- **Credit an approach agreed in a conversation as agreed with that person,** not as their authorship, unless the record says they designed it.
- **Credit once, and by what the record shows.** Credit a person once, in the thanks, unless a chapter needs the name to make the story clear. Describe a person the record shows only as an asker as asking, not as a user, collaborator or partner.
- **Tell a hard problem to the depth that shows why it was hard,** naming the constraint, not the tool flag or the compiler detail.
- **Be humble, and credit others for their specific part.** Name the person and what
  they did ("designed the original approach", "suggested the change that unblocked
  the work"), once, in a sentence or two after the results, not a list of every name
  and not before the work. Thank people for design, unblocking and sustained help, not for
  routine duties, and do not credit anyone in a way that makes the author's own work look
  smaller. Take the credit that is due without superlatives, and say plainly when a miss
  was the project's own. Do not quote praise of the author. Someone whose only recorded contribution is praise or a routine review gets no credit line. If a contribution appears only in the author's own paraphrase, ask the author before crediting it. Collect who helped, and how, during the whole-project read so the
  thanks come from the record, not from memory.
- **Lead a short window with its strongest result.** When the headline measure moved little in the window, lead with the largest concrete result and give the headline as context.
- **Show one concrete case per reader type.** The strongest evidence of use is a case: a gap found, a test written, a decision made with the data. Look for one in the record for each reader type and say plainly when none is recorded ("no measured effect yet"); when the record holds only a request or a statement of use, say that and no more.
- **Describe earlier work without blame.** Say what a previous setup could not do, not that it failed or was quietly broken.
- **Pick the hard problems.** Readers who know the field respect problems that were hard: a design that had to satisfy several constraints at once, a scaling limit found and removed, data that would otherwise have been lost. They discount a one-line fix however much time it cost. For each highlight ask whether an expert in the area would call it hard, and drop the ones that would not.
- **Tell each use as a need, a response and a result.** Someone had a need, it was met quickly with a small change that also helped others, and the result is reusable. Do not say what someone could not do, and do not list their requests as requests (the label stays "asked"; the story is told as need, response, result). The reader should finish thinking "we could use that too" without being asked. The pattern: not "A group made two requests; both are answered", but "A group needed something, got it quickly in a form others can reuse, and the result is available to anyone with a similar need."
- **Direction, not status, for what is next.** Each next step is one sentence of direction followed by two to four concrete examples. Direction comes from the north star and recorded decisions, in their own words and labelled as the direction; an item beyond them is a before-sending question, not a sentence in the update. Say "the direction is" for what the record calls a direction, and use "we expect" only where the record shows an intention with an owner; where the record says a plan is unscheduled or undecided, say that or leave it out; an item the record shows as under way can be said to be under way. Give no schedule unless a decision with a date is recorded. A to-do in the author's notes is not a decision: a dated deliverable appears only if the record shows the readers' side agreed to it. Add no new baselines or numbers here, and name a target only for a measure whose target someone with authority has set, saying who set it. Use the target in the form the record states it; when people give different dates, say the recorded one. Avoid deficit wording ("not there yet"): lead with what exists and say where it goes.
- **Trace every claim about a person, a team or a plan to what they said or decided**, the way a number traces to its source. A recap is the author's paraphrase, so check it against the original before relying on it; the author's recorded statement outranks a recap, and a transcript outranks both for what the person said; prefer the transcript when both exist. The north star's own numbers are taken as given unless the record contradicts them. A fact the author states in the brief counts as the author's statement: record it in the notes (step 1) and list it in the evidence file. The author's own recorded statement is enough to name a team as a user, labelled as the author's statement in the evidence file. Nothing in this skill is evidence for a claim; every name, request or figure still needs a source in the record.
- **Quote and attribute exactly.** Do not state what someone chose or prefers unless those are their words; describe what they do with the work. Use a statement as it was made, without adding a clause the source does not carry. Quote a person only on the topic they spoke about. Attribute each ask or statement in a thread to the person who made it, checking the original message. When a record cannot say who spoke, attribute the point to the meeting, not to a person. A first-name speaker label in a transcript can be two different people: check the attendee list. Use a source pasted without a date only through the dated record that cites it, or label it undated.
- **Figures from recaps.** A figure taken from a recap counts as sourced only if the recap carries its source; a figure whose query is not recorded and cannot be re-run goes in the evidence file as unverified, and a traceable figure is preferred.
- **Maturity, verbs and tense.** State a capability at the maturity the record gives it (set up, tested, used) and never one step further. Use the weakest verb the record supports (discussed, planned, agreed, decided, done; work the record shows as done is stated as done) and the tense of the source: a plan is not a practice. Avoid "every", "all" and "always" unless the record shows it for the whole period.
- **Causes and inferences.** State the cause of an incident only from that incident's own record. An inference goes to the author as a question, not into the report.
- **State misses plainly, and scope them to the reader.** A report with no problems in it reads
  as incomplete, not as successful. Say in one sentence, folded into the story it belongs to, what the project itself broke and has closed; never give it a section of its own. Where a risk section is wanted (step 5, item 13), list the open risks a reader can act on; otherwise keep them in the evidence file. Open defects, unresolved blockers and problems that may be gone tomorrow stay out of a broad mail.
- **Understate rather than overstate.** An entry that reads smaller than the
  work costs a little; one that reads bigger costs the credibility of every other
  line.

## Formatting that survives mail clients, forwarding and wikis

- **Name what the reader gets, not how it was built.** No merge or pull requests,
  commits, branches, file paths or script names in a report that goes beyond the
  people working in the repo: say what the capability is and what changed. Link only
  what a reader must act on (a review to approve) or open (a dashboard, the page of
  record). A link into a private repo or personal notes is a dead link to them.
- **A link that does not exist yet is left out of the update itself** (never a guessed URL, a private link standing in for it, or a bare `<fill in>`). List it at the top of the evidence file as a before-sending item saying what will go there, so none is missed.
- Bold or capitalised section labels; a numbered list for the top items.
- Tables of five columns or fewer.
- Status as bracket tags (`[Done]`, `[In progress]`, `[At risk]`, `[Blocked]`),
  never colour alone.
- Refer to people by full name (when the record has only a login, use the login or leave the person out; do not guess a name), and avoid assuming pronouns; the same applies to the briefs you give readers and verifiers.
- Full raw URLs, never masked links -- forwarding mangles masked links, and the
  reader wants to see where a link goes.
- Nothing that exists only in a screenshot.
- Expand an acronym at first use unless every reader uses it daily (terms from neighbouring areas are expanded at first use; when no source gives an expansion, drop the term or describe it in one plain-words clause; a post for readers with no context defines each remaining insider term in a clause the first time it appears); a reader outside the
  team may not share its shorthand, and expanding the team's own terms reads as odd.

## Before it goes out

- [ ] The purpose, form, audience, window and north star were agreed (or recorded as assumptions), and the whole project (meetings,
      accomplishments, past reports) was read, with what was read recorded.
- [ ] Every number has a date and a source, and a denominator where one exists.
- [ ] The soften list was applied: no bundled, inflated or one-job number is stated as general.
- [ ] The opening paragraph alone answers: what it is, the headline result and where it is going.
- [ ] Any Before | Now table compares the same measure at both ends.
- [ ] Nothing unverified is stated as fact; the gaps are listed.
- [ ] Names, teams and their credit are right.
- [ ] Each type of reader can find a sentence saying how this helps them, and none of those claims goes beyond reach you can point at.
- [ ] A broad mail contains story only (core rule 4).
- [ ] A separate reader checked every claim against the original sources and returned none unsupported.
- [ ] Every claim about a person's use or a plan traces to what they said or decided, newest record first.
- [ ] An outline was agreed before drafting (or recorded as an assumption), and the draft was read once as each type of reader on the list: would anyone be misdescribed, or find nothing in it for them?
- [ ] The length fits the reader (about 300 words for a wide audience, more for a team that works in the area, with the headline and the table on the first screen).
- [ ] Nothing in what is sent points at something the readers cannot open (notes, internal paths, private links).
- [ ] The recipients were confirmed against a past report or the author's statement (not applicable to a spoken update).
- [ ] The length, reading mode, depth and leave-out settings from step 0 were applied, and a whole-project team update follows the "where it stands and how we got here" shape of step 5 with headings that name the move (any other team email, the step 5 team-email default).
- [ ] Who the author clears the wording and the list with (step 9) is named in the before-sending items.
- [ ] Nothing was sent, posted, scheduled or saved as a draft in any mail or chat tool, for any form. The author sends it.
