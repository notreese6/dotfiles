---
name: status-report
description: >-
  Use when writing a "where things stand" report about a project for managers
  and other teams: a status update, an impact summary, a project review, or a
  monthly or quarterly update.
  Digs through notes and data for what the project was, what changed, the
  numbers before and after, who uses it, why it matters to the organization,
  and what comes next, then writes the update in the form the author chooses
  (talking points for a meeting, a message to one person, an email to a
  team, a company-wide post) from one set of facts, with an author-only
  evidence file beside it. Fires on: status report, status update, where things stand,
  impact report, monthly update, update for my manager, write up the project,
  how far we've come, update since our last one-on-one, a short list for a
  wide audience, full project update.
---

# Status and impact reports

A status report is read by people who were not in the work. Most of them read
the first screen: the goal, the objectives and the summary. So the report has two jobs, in this order: make the
change and its value obvious in the first screen, and back every claim with a
number and a source for the few who keep reading.

If a private counterpart skill is installed (`status-report-local`), it adds one
organization's house format, vocabulary, goals and audience. Load it too.

## Core rules (re-read before writing and again before sending)

1. **Accuracy first.** Every claim traces to the record, and a separate reader checks each one (step 6).
2. **Sell with evidence.** Before and after, the mechanism, the hard problems, who benefits; no adjectives doing the work of evidence.
3. **Every reader finds what is in it for them,** limited to reach you can point at.
4. **Level of detail.** Story and direction for a broad audience: no blockers, today's problems, identifiers (ticket and change numbers, test names, release numbers, product codenames), sizes, or asks for work or anyone's time.
5. **Fit the form, the length and the window.** The length the author chose (step 0) holds; failing that, the form sets it (talking points: two to four short bullets per section and only the headline figures; email: about 1,000 to 1,500 words, with at most about one number per 15 words and a dozen exact dates). Every "before" is at the window start, or is the nearest earlier figure, dated.
6. **People.** Their own words or a recorded decision; the weakest verb the record supports; specific, humble credit.
7. **Plans are directions, not promises.** Nothing unscheduled is stated as expected.
8. **Read what the window needs, and the recorded decisions, first;** keep an evidence file for every update; send nothing with a placeholder or a link readers cannot open. A whole-project update reads the whole project: no meeting and no accomplishment is skipped.
9. **The author sends; the agent never does, for any form.** Do not send, post, schedule or save a draft in any mail or chat tool, whatever the form or length (talking points and a one-line direct message included). The deliverable is a file shown to the author.
10. **When rules collide, this order wins:** accuracy and recorded decisions; then the chosen length (or the form's guide); then the required pieces (reader benefit, credit where it is meaningful, where to look), cut to a clause each if needed; then the strict reader's marks. A private skill's house format, for the audiences it lists, sets the sections and their order; these rules still govern what goes inside them. **The length and the readers decide which menu sections are on** (rule 4 and the length bucket first), and the author's corrections in the step 0 summary win: a correction that conflicts with rule 4 or the length is written and listed as a before-sending item.
11. **Step 0 is never skipped.** The author answers the step 0 questions in boxes, is shown the summary of every choice, default and assumption, and says "go" in plain words before any digging starts, whatever the deadline or form. A question is never answered by assumption; a default is shown in the summary for the author to correct. The one exception is an unattended run, where the assumptions are recorded at the top of the evidence file.

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

## Standard formats (the one place to edit)

Three formats are standard: the update file, the evidence file and the section menu with its plan check. Everything the skill requires about their shape is stated here and only here; the steps below point to this section. To change a format, change it here.

### The update file (full update and talking points)

Every update file, in every form, has this layout:

```
# <Audience> status update: <project>, <window>
- Written: <date and time, zone> from <what it was built from>
- Edited: <date and time, zone> <what changed and why>   (one entry per later edit, newest last)
- Status: draft, nothing sent; <anything else not done, e.g. a page not updated>
- Where to send: <the list>, after <who> has reviewed it

## The message
<subject line first, for an email; then the sections, as marked in the plan>

## Before you send (not part of the message)
<the before-sending items; deleted before it goes>
```

- *Written* is the first draft's time and sources and is never rewritten. *Edited* gets a new entry every time the file changes after that, with the reason (a reviewer's feedback, a figure refreshed, a verifier round).
- The title carries the window.
- Under `## The message` each section is a heading with the menu's section name exactly, then a bold headline sentence stating the outcome, then bullets (a short paragraph in read-through mode). Talking points use the same layout, with two to four bullets per section (step 7).
- The same before-sending list is kept in the evidence file (its section 2).

### The evidence file

```
# <Project>: evidence file, <date>
- Written: <date and time, zone> from <what it was built from>
- Edited: <date and time, zone> <what changed and why>   (one entry per later edit, newest last)
- Serves: <the update files this evidence supports>
- Status: <what is verified, what is not>

## 1. Step 0 answers
<table: readers, window, format, length, wins carried and bank size, derived depth, reading mode, reaction wanted, north star as confirmed, last update used, recorded steers, the section plan, the author's additions; or the assumptions in an unattended run. Then what differs from the last update's answers and what that means for this update (see reshaping).>
## 2. Before-sending items
## 3. Plan check
## 4. Context
<what was read (counts against what exists), what could not be read and what that leaves open, the per-person summary>
## 5. Accomplishment bank
<the top entries for these readers, up to 10, 20 or 35 by length, no cap for holistic (fewer when the record holds fewer that clear the bar), ranked, each with a one-line reason, its figure, source and date, and a pointer to the note it came from. The ones carried are marked; the rest are swap candidates with only the pointer and a one-line reason. Never a copy of the notes.>
## 6. Facts bank and number provenance
<step 3, and for every figure its definition, where it came from (a query, a note date, a document), whether it was checked against the original or carried from a note, its date, the safe wording, and the audiences it suits>
## 7. Work record
<the format study (step 2), the outline (step 4), claims with their supporting quotes, claims softened or left out, unverified items, verifier rounds, strict-reader scores (step 6)>
## 8. Change log
<each revision after the first, what changed and why, and every change to a step 0 answer, with the date and what it changes>
```

### The section menu and the plan check

**Marks.** Each of the seventeen sections is marked in the step 0 summary:
- `[+]` the section is written.
- `[-]` the section is left out.
- `[?]` undecided until the record has been read (allowed when what the section holds depends on the read, mainly in talking points). Every `[?]` becomes `[+]` or `[-]` right after the read, is shown to the author and recorded in the evidence file; none is left when writing starts.

Sections 1 and 2 are always `[+]`. The marked set is the plan and it is kept: every `[+]` section is written, under its menu name and in menu order, in the full update and in the talking points alike. A section is never renamed, merged or dropped on the way. It comes up short only when the record holds nothing to say: a change-tracking section (3, 4, 9 to 12) then carries the single line "No update since <the last update, or the window start>" and the author is told in the before-sending items; a static section (14, 15, 17) with nothing to say is `[-]` from the start.

**Plan check.** After each file is written, list its section headings in order and compare them with the plan:
- every `[+]` section appears once, under its menu name, in menu order;
- no `[-]` section appears;
- no `[?]` is left.

Record the result in the evidence file's Plan check as a table (section, planned mark, delivered, for each file) and state it in the reply to the author ("plan matched: 14 of 14 `[+]`, 0 unplanned"). A mismatch is fixed, or told to the author with the reason; it is never left silent. A section added or dropped after the plan was shown is recorded in the file's Edited line.

**The seventeen sections.** Each is written to the rules below; a section that is on but has nothing new is never padded (see above).

*Opening*
1. **Goal and objectives** -- the problem being solved, in a sentence; the goal with its measure, target and date, from the confirmed north star; and three to five numbered concrete objectives, each with a one-line status that the record supports. Never an objective the record does not back. Where a last update exists, each status says what it was and what it is now.
2. **Summary (thirty seconds)** -- about six bullets (five at the up-to-300-words length), each a bold headline stating the outcome and opening with what is different now, not what was done ("failed uploads no longer need a person to restart them", not "worked on the retry job"), covering where it stands, what is new, what it took, who uses it, what is next and how to help, and keeping only those whose sections are `[+]`. The first bullet carries the decision, ask or strongest result when there is one. It adds no figure that the details do not carry. A one-line note after it says the sections above are enough for a reader short of time.
3. **Where it stands** -- the snapshot: what it is, the headline result with its number and date, the north star with its target, and a Before | Now | Change table of four to six rows where like-for-like figures exist (units and dates on every number; a "before" with no like-for-like start is a short phrase, never "n/a"; two runs that ran different things say what each ran; a row measured on one job or test is labelled as such; a list of what produced a gain includes only changes that landed between the two measurements).
4. **Accomplishments in the window** -- the strongest, each opening with what changed (never "worked on"), then its before and after, the mechanism, the scope (who and what it reached) and, where the name makes the story clear, who did it; each carries the link to its page (a review, ticket, dashboard or document) when one exists that the readers can open, and none is needed when it does not. A long list means it has not been prioritised yet.

*Story*
5. **How we got the gain** -- three to six hard problems (the length setting decides), each a bold headline naming the problem, then the constraint, why it was hard, what fixed it and the number; chosen by the hard-problem test. For a whole-project update it includes where it started and why it changed, with the dated timeline folded in.
6. **Who is using it** -- the readers' own organization first, then partner teams, then others, each told as a need, a response and a result, and the next adopters. Only reach that can be pointed at.
7. **People and teams I am helping** -- who was worked with in the window and what each got, from the record; where credit is due it is given here, in line, and not repeated in Thanks.
8. **Time and capacity** -- hours or days logged against what was committed, only from the tracker's own figures, with each original estimate stated as it was.

*Forward*
9. **In progress** -- what is under way now and how far along, from the record.
10. **Next** -- direction first, then two to four examples, from the north star and recorded decisions; a month only where a dated decision records one; nothing unscheduled stated as expected.
11. **Blockers and risks** -- each with an owner and what would unblock it, and only for a reader who can act on it.
12. **Decisions and asks** -- the decisions needed, each with its options and the author's recommendation (when the author gave none, the options and the record's facts only), and the asks with an owner, what and by when, limited to decisions, approvals and resources the readers control, never work for them to do; decisions made are listed as made.
13. **Lessons and what is not working** (on by default only when a manager is among the readers; sits in the Forward group) -- what is working and what is not, in one or two honest lines each, and one lesson the work taught that changes what happens next; from the record, never a mood. A reader who can act on it gets a specific, scoped item, not a general complaint.

*Support*
14. **Where to look** -- the links the author gave or the newest record shows as current (an older note's link may have been replaced; when a title is unconfirmed, describe the link neutrally), what each answers, how to drill in and how long each kind of detail is kept. A link the readers cannot open becomes a before-sending item.
15. **Thanks** -- written only when there is meaningful credit (design, unblocking, sustained help) that the update has not already given in line, and not for small or routine things; specific and humble, placed after Next; otherwise `[-]`.
16. **How you can help** -- up to three general invitations that point at something that exists (open the dashboard and look at your own area; say what looks wrong or should not count). No asks aimed at named people and no requests for reviews, time or work on in-flight changes: those go to the people concerned directly.
17. **Definitions** -- a term defined inline where it first appears, kept only when readers outside the area would not know it; where to check a figure belongs in Where to look. Provenance only the author can open (notes, internal paths) and what could not be verified go in the evidence file, never in the update: a link the readers cannot follow is worse than none.

### Update body shape

The default shape, any audience and any window: Goal and objectives (1), Summary (2), then the remaining `[+]` sections in menu order. The structure came from a reader's feedback on a long update: keep the detail, because the detail matters, but open with the goal and concrete objectives and then a thirty-second summary.

## Procedure

### 0. Ask the step 0 questions, summarise every choice, and wait for "go"

**Never skipped, never answered by assumption.** Not for a deadline, not for talking points, not for a small edit that changes the readers, the window or the format. An update already written keeps its recorded answers, and the questions are asked again only for what changed. In an unattended run, where nobody can answer, record each answer as an assumption at the top of the evidence file and continue.

**How to ask.** Use the pick-a-box prompt tool (in Claude Code, `AskUserQuestion`: one to four questions per call, **two to four options per question**, multi-select allowed, a free-text "Other" always added, so a named list or an unusual choice goes there). Put the recommended option first, mark it "(Recommended)", and give the reason in its description. Without such a tool, ask the same questions as a numbered list with the recommendation and reason on each line. Option wording uses the author's earlier answers (the real dates of a window, the chosen readers), never the wording of the request, which is why the questions go in three calls: each call's options use only answers from earlier calls.

**Reads allowed before "go".** Only these, to ground the recommendations and the summary: the project's live summary and its North Star section; the last sent update to these readers and its evidence file (see below); the date of the last meeting with a reader (calendar or notes); and the recorded steers in notes back to the last update, or the last 14 days (`Decided` lines and the readers' own feedback on earlier updates). Nothing else is read, queried or drafted until the author says "go".

**Finding the last update.** Updates are named `<project>_<readers>_status_update.md` and the evidence file `<project>_evidence.md`, in the project's reports folder for the day they were written. The last update is the newest `_status_update` file for these readers that the notes record as sent (the author says it went out; record "sent <date> to <list>" in the dated note for the day it went out, and never edit an older date folder to do so). `<readers>` is a short slug for the list or group; a multi-select answer matches an earlier update whose slug covers any of these readers, and the closest match is shown in the summary for the author to confirm or replace. An unsent draft informs structure only. When none is found, say so in the summary and ask the author to confirm that, or to name one, before "go".

**Call 1 -- the readers (one question).** Multi-select: a manager; the author's team; adjacent teams and partners; a wide organization. A named list or person goes in "Other". The author picks them; the format never implies them. Nothing is looked up in this call. What the readers already know, what they decide or do with it, where it goes and the last report that went to a named list are found after "go" (steps 1 and 9); until then the summary shows the depth and the reader types as defaults for the author to correct.

**Call 2 -- window and format (two questions).**

1. **The window.** Options show their real dates: since the last update or meeting with these readers (give the date and say which), the last week, the last month (a quarter or any other span goes in "Other"), the whole project. Every "before" number sits at the start of the window; when no figure exists there, describe the starting state in a sentence and date any later "before" figure, never implying it is the start. Prefer the nearest recorded figure before the start, dated, over one from the middle of the window. The window decides how much is read (step 1). When the request names a window and the author picks another, use the pick and say so once in the summary.
2. **The format.** How it is delivered, which sets the structure conventions only: an email, a page of record, meeting prep as talking points, or a monthly publication format if a private skill defines one. The default structure is goal and objectives, then a summary, then details, whatever the readers or window. Talking points are not a different shape: they follow the same sections as the plan (step 7), a few high-level bullets each, written beside the full update so the author can go through them breadth first and dig into any one.

**Call 3 -- length and what it is for (three questions).**

3. **The length.** Up to 300 words; 300 to 1,000; 1,000 to 2,000; holistic (as long as the whole picture needs, the hard problems at full length). Recommend from the window, format and readers chosen and from how the last report to these readers was read. Talking points are measured by their sections, not by a word cap: two to four bullets each.
4. **The reaction wanted.** Multi-select, worded against the chosen window and readers: what should the readers think or do afterwards? Options are reactions, not labels: know where it stands and what moved in the window (inform); see that the work achieved something and is useful to them (show what a body of work achieved); open the dashboard or tool and look at their own area (build adoption); decide something named (ask for a decision). Recommend one or two and say why. Each reaction turns on sections: inform, where it stands, in progress and next (3, 9, 10); show what was achieved, accomplishments, how we got the gain and who is using it (4, 5, 6); build adoption, who is using it, where to look and how to help (6, 14, 16); ask for a decision, blockers and decisions (11, 12). Name the reader types (the people doing the work, their team, managers, the wider organization, the company) and, for each, how the work helps them, so every reader can see what is in it for them. An update meant to show what the work achieved is a story of change and who benefits, not a neutral status.
5. **The north star.** The outcome the project exists to deliver and the target it is measured against, from the live summary's North Star section as the recommended text, with its target, measure and date (the last update's north star is the fallback, and any named ticket or page is only a check). Two options: confirm the recommended text, or change it (the change typed in). An unanswered question is asked again, never assumed. If none is recorded, do not start another process inside step 0: recommend the last update's north star or the target the request states, ask the author to confirm or type one, and offer to agree one properly after the update (the realign step of `plan-iteration`). The goal and objectives, the headline numbers and every "next" step come from it and from recorded decisions (open TODOs are candidates; one they do not back goes to the author as a question).

**Not asked, derived and shown.** Depth is set by the least-informed reader ticked (no context: plain words, no internal names; an adjacent team: their own terms, the mechanism in a clause; works in the area: the constraint and mechanism of each hard problem, numbers with denominators; a peer expert: the constraint, the alternatives rejected and why); it sets vocabulary and how much mechanism each story gets and never changes which facts are true. Reading mode defaults to skim-first (every item opens with a bold headline that states the outcome, bullets under it, a table or bulleted measures for numbers); the author can ask for read-through (a short paragraph under each headline) in the summary. A peer-expert depth is used only when the author says so. What to leave out of the story comes from the recorded steers (what the project replaced, its own infrastructure history, fixes to its own earlier mistakes, experiments that did not become the product, a reviewer's earlier feedback); a part left out is replaced by at most a clause where the reader still needs it, wording that implies it is cut, and leaving something out never licenses a false statement.

**The summary, then "go" (plain text, not a box).** After the three calls, show one summary and nothing else:

- **A table of the choices:** readers, window (with dates), format, length, the number of wins carried and the bank size (targets from the length, so the author can change them; the actual count is known after reading and reported with the finished update), derived depth, reading mode, reaction wanted, the north star in full, the last update (its path and whether it is recorded as sent, or "none found, please confirm"), the recorded steers that apply, and, when a last update exists, what changed from its answers (a longer window, new readers, a revised north star, a new format).
- **Defaults and assumptions:** every one made without asking, so the author can correct it.
- **The sections, all seventeen from the Standard formats section menu, each marked `[+]`, `[-]` or `[?]`, with a few words of reason.** The marks are the plan; the plan check in Standard formats confirms the file came back as marked. Goal and objectives and Summary are always `[+]`. The rest are decided from the length and the readers (rule 10): for example a broad audience or an up-to-300-word length turns off blockers, asks and time and capacity, and a manager among the readers turns on lessons. Start from the last update's section set when there is one. When the author turns on a section that rule 4 or the length rules out for these readers, write it and list the conflict as a before-sending item.

Then ask in plain text for corrections, additions (a section not in the menu, something to include, a person to credit, a figure or wording to avoid) or "go", and **stop.** Any clear go-ahead counts as "go". A correction changes the summary: show the changed rows and ask again. An answer that contradicts another, or free text that fits no option, is restated in the summary as your reading of it for the author to confirm. After "go": steps 1 to 6 (reading step 7 before step 5, and step 9 when it goes out), then show the update with the runners-up and ask what to change (step 6, last paragraph).

**Audience presets (recommendations only; the author's corrections in the summary win).** The facts are the same for every audience; the depth, the vocabulary, the lead and the sections left out are not.

- **A manager, since the last one-on-one** (technical). Recommend the sections that show what the author is doing: where it stands, in progress, next, blockers and risks, decisions and asks, what was accomplished since the last meeting, and lessons, with mechanism and numbers with denominators. A recommendation is the author's: label it as such, and when the author gave none, list the decision with its options and the record's facts and offer no recommendation. The decision that matters most to the manager's goals is the first bullet of the Summary.
- **A team that works in the area, whole project.** Recommend all sections except 13 (managers only), with the hard problems at full length and mechanism wanted; for a whole-project window section 4 is folded into section 5, and blockers and asks (11, 12) are on only where the team can act on them.
- **A wide audience that knows nothing about it.** Recommend the up-to-300-words length: at most five plain-word headlines, each with what changed, why it matters to the reader and one before-and-after number; no internal names, tools or acronyms the reader has not met; blockers, asks and anything undecided left out. At this length the goal is one sentence, the summary is the five headlines, and the details are `[-]`.
- **A known team or list** (a regular status mail). Recommend what changed and who it helps, two or three examples, who uses it, what is next and where to look; medium length, light jargon. A wide list gets direction, not status.

### 1. Read what the window needs, then keep it in the evidence file

Starts only after the author says "go". **How much is read depends on the window:**

- **A window (since a date, a month, a quarter):** every dated note, every meeting and one-on-one record (recaps and transcripts) and every accomplishment **inside the window**, read in full, none skipped. From before the window read only what a figure or a decision needs: the "before" figures at the window start, the history behind anything that landed in the window, and the items below that apply to every update.
- **The whole project:** everything, outside the window too. No meeting and no accomplishment is skipped; the starting point, the chain of causes behind each gain and the things that went wrong are found in the early record.

**Applies to every update, whatever the window:**

- **The audience's own record:** the last few meetings and one-on-ones with this audience (back to the last update at most), plus any earlier statement a claim or a priority relies on, in the original words where they exist. What the readers say they care about, in their words, is the most important input: it tells you which items to lead with and why. Collect, per person, what they care about, what they asked for, what they would count as a win, and what they pushed back on, with dated quotes; about five lines per person. Recaps are someone's paraphrase: read the primary record for the strongest claims (who uses the work and why, what someone asked for, what was decided). The newest record wins; an earlier note is history.
- **The last update sent to these readers, its evidence file, and the replies**, to see what landed and to continue it: its goal and objectives, its section set and structure, its north star and its recorded steers set the defaults, and each objective's status is carried forward so this update can say what moved since. An unsent draft or a report to a different audience shows what the author has said; use it to check, never as a source.
- **The decisions already recorded** and the author's recorded statements (the `Decided` entries and any other lead-in the notes use; read the whole Notes section of each recent day, not only the lines that start with `Decided`): the headline measure, what to leave out, wording the author has ruled out. They override your defaults. When the author states a decision, or a fact about who uses the work and what it is for, record it in the notes with the date, marked as the author's statement, so the next session can use it; write it only when the author actually said it (an inference is a question, not a statement). A use or plan with no source in the record and no statement from the author goes to the author as a question. A recorded decision on what to include or omit, or on the headline measure, binds the update on what it decides, even when the figure is hard to re-derive: use the decided one and list the conflicting reading as a before-sending item, in the note's own wording.
- **The north star and any targets with their reasons.**

**Reading accomplishments at scale, ranking as you go.** Each accomplishment is read in full, by you or by a reader, never judged from its first line: the best ones are found in the detail (the number, the cause, what was fixed and how). Do not copy them out: the notes already hold them. Rank each one against **these readers only**, as you read, on: value to the readers (it changes what they can do or decide); size of the change, as a before and after with a denominator; strength of the evidence (measured against a query, or carried from a note); newness (in the window, and not already told to these readers in the last update); and whether an expert would call it a hard problem. Keep a running top list and a runners-up tail. The number carried comes from the length chosen, where a win is one accomplishment with a figure, however the update groups it into chapters: up to 300 words, 3; 300 to 1,000, 6; 1,000 to 2,000, 12; holistic, everything that clears the bar above. The **bank** (the carried wins plus the runners-up kept as swap candidates) holds up to 10, 20 or 35 wins for those three lengths, and has no cap for holistic. These are targets, never quotas: when the record holds fewer wins that clear the bar, carry and bank fewer, say so in the summary, and never pad or invent. On a long record, extract the entries with a script (writing to the session's scratch directory) into files of about 100 entries each (split on entry boundaries outside code blocks; a sub-bullet belongs to its entry) and give each file to a parallel reader with the same brief: rank as above and return its strongest entries (up to a third of what it read, capped at the bank size) with a verbatim quote, the date and file, the figure with its denominator, whether it was later corrected, retracted or superseded (with the later date), who is credited, and a count of entries read. Read the returns yourself, re-check each quote you use against the original, and record the count read against the count that exist, explaining any difference from a count the author gave. An entry is one dated bullet under Accomplishments; its sub-bullets belong to it.

**The evidence file is always created**, for every update (talking points included), as `<project>_evidence.md` next to the update `<project>_<readers>_status_update.md`. One evidence file per project per day serves every update written that day, with a section of step 0 answers for each; a second audience adds an update file, not another evidence file. It is the author's record, never sent, and it exists so a change of audience, window, sections or headline later is a pick from it instead of another read of the record. Its format is in Standard formats. Fill the step 0 answers, the before-sending items and the context before the outline, and add the rest as the work produces it. Do not write the update before it exists.

**Reshaping uses it.** When the author asks for another audience, window, section set or headline, start from the evidence file and the update, read only the part of the record the new choice adds (the new part of the window, a new audience's own record), add each new fact to the file with its source before it reaches the update, and record the change. **A changed step 0 answer can force more than a rewrite** (the same applies when this update's answers differ from the last one's): a longer or shifted window means reading the added days in full, and any before-and-after comparison with the last update is valid only if the objectives and definitions it used are unchanged; new readers mean reading their own record and re-deriving depth, the steers to apply and the credit; a revised north star means re-deriving the goal and objectives and saying plainly that the target changed; a different format or length means refitting, not trimming; a changed section set needs nothing further. Record the answer, what it changed and what was done about it.

### 2. Learn the house format before writing a word

Read a few reports this audience already likes and match their shape; readers
parse a familiar shape faster. Note what the good ones share and what the weak
ones do wrong. Save what you learn as a study (a section of the evidence file is enough),
so the next report starts from it. If this audience has no earlier report, say so, and use
the closest one you can find. If the author names a draft they like, use its shape, never its facts. The format and length the author chose in step 0 win over a liked report's shape; take only its conventions.

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
current code and configuration, then memory. Recaps and drafts are leads, not sources, until checked against a dated note or the original. Read what the window needs (step 1): for a whole-project update the notes for the whole project, not the last few days -- the starting point is the part most often lost.

**The facts file is a bank of options, not the outline.** Hold the facts the update uses and, for the swap candidates, a pointer to where each is recorded (date and file) instead of a copy, because feedback, a different audience or a change of headline later means picking from it or re-reading only those pointers. For each fact used keep: the claim with its definition, the source and date, whether it was checked against the original or carried from a note, the safe wording (and wording to avoid), which audiences or forms it suits, and whether the current update uses it. Group the facts by theme, so a pivot is a quick pick, and give the history and the open tracking items their own groups marked as not for a broad audience, so they are findable but never leak into one. Record the open definition questions (for example, a figure whose denominator differs between two sources) beside the facts they affect. Keep it after the update is sent: a revision starts from it, changes the update's wording from it, and records what changed and why in the evidence file. New facts (a meeting, a data pull) are added to it with their source before they reach the update, so a figure never enters the update without a row in the file.

### 4. Sort the facts, then record the outline

Mark every fact as **story** (what changed, how it was done, who benefits, where it is going) or **tracking** (current status, blockers, who is waiting on whom, requests to named people, problems of the last day or two). A report for a broad list is built from story only. Per-item counts, incident detail and operational mechanics are tracking unless they explain something the reader will see. Test each sentence: if the reader's belief or decision would not change were it deleted, cut it. Definitions and reconciliations between two figures go in the evidence file; the update gives the headline's definition in one clause. Tracking belongs in the one-on-one, the notes or a direct message; in a broad mail it makes the work look smaller. The exception is a section marked `[+]` that is itself tracking (in progress, blockers, decisions). The outline names the headline, the stories and the direction; the goal, objectives and summary are written from it after the body.

Then apply the recorded steers from step 0: delete each part of the story they say these readers should not carry (a closed miss of the project's own keeps a clause, see the impact rules), keep at most a clause where the reader still needs it, and cut any wording that implies it.

Record the outline in the evidence file: the headline, the stories that carry it (each with its sources), the direction in a few lines, and the readers' own use. It is not sent to the author for approval: the sections and the audience were settled in step 0, and the author reviews the finished update (step 6, last paragraph). Treat the recorded `Decided` entries as the agreed outline where they decide something.

### 5. Write the update

The deliverable is the update in the form the author chose, saved in the project's reports folder, by date (`reports/<project>/<date>/` unless the notes rules say otherwise). Before drafting, read step 7 (the form's length and shape) and the impact rules below; the delete test is in step 4. Write a separate long report only when a page of record will be published or the audience asks for depth; otherwise the evidence lives in the author-only file and the update stands alone. The structure below is the same for the full update and for talking points; talking points keep every section and cut each to a few bullets. A whole-project update tells the work once, as the hard problems of menu section 5 with the dated timeline folded in, not as separate highlight and timeline blocks. The required pieces (reader benefit, where to look, credit) are a line or two each: fold them into the sections they belong to instead of adding blocks, so the update stays inside its length guide. **The default shape for a general status update, any audience and any window: goal and objectives, summary, details.** It holds for a whole-project update and for a short windowed one, in every form; talking points use the same sections at a higher level (step 7). The structure came from a reader's feedback on a long update: keep the detail, because the detail matters, but open with the goal and concrete objectives and then a thirty-second summary, so a reader short of time stops after the first screen and a reader who wants more continues.

The update follows the Standard formats above: the file layout, the section plan and the plan check. The default shape for any audience and any window is goal and objectives, summary, then the details, so a reader short of time stops after the first screen and a reader who wants more continues.

The Before | Now table in "Where it stands" is optional: its first bullets can carry the headline numbers. Talking points follow step 7, and the up-to-300-words length for a wide audience keeps to the preset in step 0.

An invented example of the finished shape, for a team email (about 1,100 words in full):

> Subject: Upload service: failures down 96% since March
> **Goal and objectives.** The problem: one upload in 14 was being lost. The goal is under one in 300 by June. Objectives: (1) save progress after each confirmed chunk [done]; (2) a nightly check that tells us the same day if failures climb [in progress]; (3) the same fix for the mobile client [next].
> **Summary.** Failed uploads fell from 1 in 14 to 1 in 400 since March; large files, the main cause, no longer restart from zero; a nightly check now runs; mobile is next. [six bullets in all, each opening with what changed.]
> **Details.** [the kept sections, in order: where it stands with an optional Before | Now table; the hard problems told as symptom, why it was hard, what fixed it, the number; who it helps by reader type; where to look; what is next.]

### 6. Verify every claim before it goes out

A draft carries claims the sources do not support: a wrong cause, a plan stated as agreed, an ask credited to the wrong person, a figure from a different run, a piece of work described as something it is not. Reading the draft yourself does not find them, so a separate reader checks every claim against the original sources.

- **The brief.** Give the reader the finished draft, the sources and a claims table. The table lists every sentence of the draft that states a number, date, name, use, plan, cause or table-row label (an id and the sentence); sentences about the update itself (what follows, what is left out) are not claims. The reader also returns any such sentence the table left out. Standard brief: "Draft and claims table below. Read only <the allowed paths>. For each claim return its id and one verdict with the verbatim quote, file and line: SUPPORTED; PARTIAL (say which part is unsupported); NOT SUPPORTED (say what the source says instead); or UNSOURCED (a framing sentence about the author's own view, which needs a source or goes to the author). List any claim-bearing sentence missing from the table. End with exact counts, which you recount yourself. Write nothing else."
- **Where it may read.** The dated notes, the project's live summary, the named source files, the update's own file, the author's recorded statements, and plain-text copies of non-file sources (mail, query output) saved in the scratch directory. The skill files and the evidence file are not sources, and records of other projects can be skipped once their titles show that. A figure from a live query the notes never recorded is UNSOURCED: save the query output to the scratch directory, or cut the figure. Give every reader and verifier this same confinement and the same no-writing rule; record any breach in the evidence file, because the verdicts stand only if nothing from outside was used.
- **What to check beyond the quote.** For each table row: its label word by word against the source's own description of the figure (what it measures, the run type, the date, the scope), and that the before and the now measure the same quantity in the same units. For each claim about a person: word by word against what they said or what the record shows they did. For every absolute claim (every, never, always, only, first, all, "does not ... when"): a search for a counterexample. A single run or period stated as the current state is a dated observation. A projection or design estimate is not a measurement: label it or leave it out. Never state why a person acted or asked unless they said so. Describe what a piece of work does from its own record (its title and description), not from nearby entries; when you cannot, describe it at the level you can. When the record does not settle a target, state it as the author's stated direction, not as someone else's commitment.
- **Acting on the verdicts.** Correct each NOT SUPPORTED claim to what the source says, or delete it. When in doubt, leave it out: a PARTIAL claim is cut back to the part that is supported, not reworded around the gap. Re-open the original for every quote you rely on (or a stated sample on a large set) and confirm that its number and scope match the claim. Keep the quotes in the evidence file.
- **Rounds and stopping.** On a large claim set, split the table across several readers by section; a round is one pass over all changed claims. After the first full run a round re-checks only the claims that were added or reworded, including any new wording a weakening edit introduces; a pure deletion needs no round. Stop when a round returns no NOT SUPPORTED, PARTIAL or UNSOURCED claim, or after six rounds. A claim still unsupported at that point is deleted and the deletion is recorded in the evidence file; the writer may not set a finding aside as "structural" unless it names no claim.

Save the update to its own file and give the strict reader that file. Then a second separate reader, who has not seen the evidence file, reads the update as each type of reader and as a strict editor and marks it from 1 to 10 on: accuracy; fit to the audience, window and form; selling with substance; level of detail; structure for the form; claims about people; credit and humility; and what each reader gets out of it, each judged against the matching core rules rather than its own taste. Give it the form, the audience, the depth and this skill's length, number and date guides so it marks against them instead of setting its own; tell it that for a team that works in the area the mechanism of a hard problem is wanted and is not a level-of-detail fault, while blockers, today's problems, identifiers and sizes are. Word and number counts exclude the subject line and links, and follow the counting rule in the rules for the numbers. It sees only the update, so its accuracy and claims-about-people scores are impressions (the verifier's quotes are the proof). It returns each score and, for the two lowest, the sentences that cause them. Fix those sentences and read once more; any claim added or reworded after this reader goes back through the verifier. A recorded decision outranks this reader's level-of-detail and people marks: list the conflict as a before-sending item. A claim stripped of an identifier stays checkable: keep the identifier in the evidence file. Where its level-of-detail mark conflicts with "tell the mechanism", keep the mechanism to the one or two plain sentences that make the problem's difficulty clear. Scores mean: 6 needs edits, 7 is good, 8 is ready to send, 9 is strong. Stop after two fix cycles (read, fix, read, fix, read: three reads at most); the update is ready to show the author when the verifier's last round returned no unsupported claim, no dimension other than accuracy is below 7 and level of detail is at least 8 (the accuracy mark is advisory; the verifier's quotes are the proof); otherwise it is shown with what remains as before-sending items. Either way state the before-sending items in the reply to the author, not only in the evidence file: the author decides and sends. **Then ask what to change,** in a box of at most four options: the content (a section, a figure, a line of wording, or swapping in one of the runners-up); the readers or depth; the window or length; or nothing more to change. Apply the answers from the evidence file as step 1 describes, and ask again until the author picks "nothing more to change".

### 7. Fit the update to its form

**Talking points** are for a meeting where the author goes through the work breadth first and the reader picks what to dig into. They are the same sections as the plan, in the menu's order, each as two to four short bullets at a high level: the headline of the section, the one figure that carries it (headline figures only; raw counts, identifiers, sizes and file or bug numbers stay in the full update and the evidence file), and where it matters a line to say out loud. Goal and objectives and the summary come first, because they are what lets the reader choose where to dive. Talking points follow the Standard formats (layout, section plan and plan check). They are written beside the full update, not instead of it, and use only claims the full update carries. An email has a greeting and a sign-off in the author's voice, under its subject line in the file layout; a post or talking points do not. The first screen is the goal and objectives and the summary (step 5); move scope definitions and quotes lower. A direct message is a few lines: the headline, the one thing that matters to that person, and a link to a page they can open, or none. It keeps the evidence file, the window-based read of step 1, the verifier and the strict reader: only its length is short, and a short message still states claims that need the project's context. An email or post follows the structure above. If there is a longer version, link it near the top. Length follows the reader. For a wide
audience that does not know the work, the up-to-300-words preset in step 0: at most five headlines, a table of at most three rows or none, one line of credit if there is any that is meaningful, one pointer. For a
team that works in the area, as long as the reader keeps gaining from it: the goal, objectives and summary on the first screen, and the hard problems told with their mechanism. As a guide, a written update to such a team runs about 1,000 to 1,500 words with at most about one number per 15 words (about 80 in 1,200 words) and about a dozen exact dates; a draft above that reads as a log, so keep the number that carries each story and move the rest to the evidence file. Give each hard problem the room it needs (the length chosen sets how many), three or four sentences each: the symptom, why it was hard, what fixed it, the number. Keep the goal to a sentence or two before the numbered objectives; past that, cut detail, not stories: drop byte counts, version numbers and per-item tables the reader does not need to follow the argument, and keep a few dated milestones instead of a long timeline.
The first screen is the goal and objectives and the summary: what the problem was, where it stands, and where it is going. A mail that exists to inform carries no offers and no requests; being helpful is implied by the work. The one exception is the "How you can help" section of the default shape in step 5, limited to what that section allows. A length chosen in step 0 replaces the form's guide above, and the number and date budgets scale with it (about one number per 15 words and a dozen exact dates per 1,200 words). An update whose purpose includes decisions (a manager's update) lists the decisions needed, each with its options and the author's recommendation (when the author gave none, the options and the record's facts only), but still does not ask for work from others. Mechanism means what was found and how it was fixed, in the reader's terms, not file names or change numbers. Pointing readers at a dashboard or data is a pointer, not an offer. A path for readers to use the work (where to look, who to ask) is fine when it points at something that exists; an offer to do work for them, or a request for their time, is not. Where no how-to or link exists, say what exists today and do not imply an invitation: a use path counts only if it has a link or an owner the readers can open. When a long report exists, the update may carry a subset of its rows, with the same numbers, and nothing the long report lacks. If the asks are the point of the mail, make them the Summary's first bullet.

### 8. Tailor per reader, without forking the facts

Use the audience, depth and sections chosen in step 0 to set vocabulary, the lead and what is cut. Keep one set
of facts; reorder or shorten rather than writing separate
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

- **Counting.** Word and number counts exclude the subject line and links. A before-and-after pair counts as one number. Exact dates are counted separately (a dozen in a team email), including those in table cells; a month or a plain "since" is not an exact date. In talking points, dates, item counts and names do not count as numbers. Every guide that gives a count (core rule 5, steps 5 and 7, the strict reader) uses this rule.
- Before and after, with the change: `12,000 -> 18,000 items (+50%)`.
- A denominator whenever there is one: `412 of 1,000`, not `41.2%` alone. In talking points a ratio such as `1 in 14 to 1 in 400` stands in for it, and the raw counts stay in the evidence file.
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
- **Credit by what the record shows, never the same credit twice.** Credit a person in line where the story needs the name, or in Thanks, not in both. Describe a person the record shows only as an asker as asking, not as a user, collaborator or partner.
- **Tell a hard problem to the depth that shows why it was hard,** naming the constraint, not the tool flag or the compiler detail.
- **Be humble, and credit others for their specific part.** Name the person and what they did ("designed the original approach", "suggested the change that unblocked the work"), in a sentence or two, where it fits the story. Thank people for design, unblocking and sustained help, not for routine duties or small things, and do not credit anyone in a way that makes the author's own work look smaller. Take the credit that is due without superlatives, and say plainly when a miss was the project's own. Do not quote praise of the author. Someone whose only recorded contribution is praise or a routine review gets no credit line. If a contribution appears only in the author's own paraphrase, ask the author before crediting it. Collect who helped, and how, during the read so the credit comes from the record, not from memory.
- **Lead a short window with its strongest result.** When the headline measure moved little in the window, make the largest concrete result the Summary's first bullet and give the headline as context.
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
  as incomplete, not as successful. Say in one sentence, folded into the story it belongs to, what the project itself broke and has closed; never give it a section of its own. Where a risk section is wanted (step 5, menu item 11), list the open risks a reader can act on; otherwise keep them in the evidence file. Open defects, unresolved blockers and problems that may be gone tomorrow stay out of a broad mail.
- **Understate rather than overstate.** An entry that reads smaller than the
  work costs a little; one that reads bigger costs the credibility of every other
  line.

## Formatting that survives mail clients, forwarding and wikis

- **Name what the reader gets, not how it was built.** No merge or pull requests,
  commits, branches, file paths or script names in a report that goes beyond the
  people working in the repo: say what the capability is and what changed. Link only
  what a reader must act on (a review to approve) or open (a dashboard, the page of
  record). A link into a private repo or personal notes is a dead link to them.
- **Supply a link wherever one exists and the readers can open it** (a review, ticket, dashboard, document); a claim does not need a link, and a missing link is not a gap to fill with a guess.
- **A link that does not exist yet is left out of the update itself** (never a guessed URL, a private link standing in for it, or a bare `<fill in>`). List it in the before-sending items as a note saying what will go there, so none is missed.
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

- [ ] The readers, window, format, length, reaction wanted and north star were agreed (or recorded as assumptions), and what the window needs (the whole project for a whole-project update) was read, with what was read recorded.
- [ ] Every number has a date and a source, and a denominator where one exists.
- [ ] The soften list was applied: no bundled, inflated or one-job number is stated as general.
- [ ] The goal and objectives and the summary alone answer: what the problem is, where it stands and where it is going.
- [ ] Any Before | Now table compares the same measure at both ends.
- [ ] Nothing unverified is stated as fact; the gaps are listed.
- [ ] Names, teams and their credit are right.
- [ ] Each type of reader can find a sentence saying how this helps them, and none of those claims goes beyond reach you can point at.
- [ ] A broad mail contains story only (core rule 4).
- [ ] A separate reader checked every claim against the original sources and returned none unsupported.
- [ ] Every claim about a person's use or a plan traces to what they said or decided, newest record first.
- [ ] The step 0 questions were asked in boxes, the summary (choices, north star, defaults and assumptions, sections marked `[+]`/`[-]`/`[?]`) was shown, the author said "go" before any reading beyond the allowed grounding, and the draft was read once as each type of reader on the list: would anyone be misdescribed, or find nothing in it for them?
- [ ] The length fits the reader (about 300 words for a wide audience, more for a team that works in the area, with the goal, objectives and summary on the first screen).
- [ ] Nothing in what is sent points at something the readers cannot open (notes, internal paths, private links).
- [ ] The recipients were confirmed against a past report or the author's statement (not applicable to talking points).
- [ ] The length, reading mode, depth and recorded steers from step 0 were applied, and the update follows the goal, summary and details shape of step 5 with only the sections marked `[+]` in the summary, and headings that name the move.
- [ ] The evidence file exists with the step 0 answers, the ranked accomplishment bank (sized by length) and the number provenance table.
- [ ] Who the author clears the wording and the list with (step 9) is named in the before-sending items.
- [ ] The update file and the evidence file match the Standard formats, and the plan check shows every planned section delivered and nothing unplanned.
- [ ] Nothing was sent, posted, scheduled or saved as a draft in any mail or chat tool, for any form. The author sends it.
