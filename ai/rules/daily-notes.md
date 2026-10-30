<!-- ai-rules: order=20, default=on, prompt="Include the daily-notes rules, skill and reminder hook" -->

# Daily notes

An opt-in module. `ai-rules apply` includes this when `modules."daily-notes"`
is true in the config, which it is by default — the module declares `default=on`,
since including it only appends a section.

Take this repo and you inherit the notes discipline on its own: nothing here
depends on `misc.md`, which is notreese's general opinions and is off unless
you ask for it.

## Where the notes live — read this before anything else

**The notes directory is a per-machine setting. Read it from the config. Do not
assume `~/daily-notes`, and do not assume it is under your home directory at
all** — on at least one machine it is `/weird/path/home/<user>/daily-notes`.

```bash
python3 -c "import json,os;print(json.load(open(os.path.expanduser('~/.config/ai-notes/config.json')))['notes_path'])"
```

That path is `<notes>` everywhere below. If the file or the key is missing, fall
back to `~/daily-notes`. **Never go searching for a notes folder** — a machine
with a configured path elsewhere looks empty, and you will report "no daily notes
exist" about notes that do. That has already happened once: the config was right,
the rule said to read it, and the first lookup went to the default anyway.

`daily-notes-sync status` prints the resolved path along with everything else
about the setup, and changes nothing, if you would rather ask the tool.

## Reading the notes (answering "where are we on X?")

These notes exist to be read, not only written. When asked what happened on a
project, what is in flight, or to pick up where something left off, **read them
before answering from the codebase or from memory** — they hold decisions and
blockers that no file in the repo records.

Where to look, in order:

1. **`<notes>/current/<project>.md`** — the live "what is open right now" view.
   One file, usually the whole answer. Start here.
2. **The most recent `<notes>/<date>/<project>.md` files** — what actually landed
   and when. Read a few days back, not just today.
3. **`<notes>/current/` as a listing** — when the project name is uncertain, this
   is the list of every project with open work.
4. **`<notes>/reports/<project>/<YYYY-MM-DD>/`** — the standing multi-file deliverables.
   Reached from the pointer in `current/<project>.md`, not by browsing;
   `reports/README.md` indexes them. Open one only when a rollup points you at it,
   and read the **newest** date folder that holds it — that is the current version.

**Run `daily-notes-sync pull` first.** Another machine may have written since
this one last synced, and answering from stale notes is worse than answering
from none — it is confidently wrong. If the notes directory turns out not to be
a repository, read it anyway; it is still the notes.

**If you find nothing, say which paths you checked.** "No notes exist" and "no
notes for that project" and "the configured path is empty" are three different
answers, and only the first is ever surprising.

## Prioritizing TODOs — markers, dates, and when to surface them

Every item under `## TODOs`, `## Blockers` and `## In Progress` carries one of four
markers. They sort in this order, and each of those lists is **always** written sorted:

| Marker | Means | Date |
|---|---|---|
| `[!]` | **URGENT** — a hard deadline inside 7 days, or blocked/blocking someone right now | **required** |
| `[>]` | **NEXT** — the thing to pick up next. Important, no hard date | optional |
| `[ ]` | **OPEN** — real work, will happen, not next | optional |
| `[~]` | **LATER** — worth keeping, no commitment | none |

```markdown
## TODOs
- [!] by 2030-01-15 — finish the auth migration on both services (ticket 1234)
- [!] blocked — post the unblock note on the review that has been stuck a week
- [>] commit + MR the retry-loop timeout fix
- [ ] pull the unclaimed triage queue
- [~] prune the backup directory
```

**Sort order within a tier:** dated items first, by date ascending, then undated
items by priority, the one that matters most first. A new item goes at its rank,
never at the end because that is the easy edit, and an item whose priority changed
moves to its new rank. Items that tie keep the order they were already in, so
re-sorting never churns a line that did not need to move.

**Dates are the mechanism, not decoration.** Write `by YYYY-MM-DD` immediately
after the marker — that is what makes a deadline greppable and sortable. Convert
"end of June" or "next Friday" to a real date as you write it; a relative date in
a note read three weeks later is worse than no date at all.

- A dated item **promotes to `[!]` on its own** once it is within 7 days.
- Past its date it becomes `[!] OVERDUE since YYYY-MM-DD`. Never leave a stale
  `by` date sitting there looking like it is still ahead.

**`[!]` is almost never** — the same discipline as the `[!]` log tag. If six
things are urgent then none of them are, and the surfacing below becomes
wallpaper that gets scrolled past. `[>]` is where "important" normally lives.
Before marking something `[!]`, ask whether it should stop me mid-scroll.

**Surfacing — once per session per project, not once per prompt.** The first time
a session touches a project (reading its notes, writing them, or doing work that
belongs to it), surface that project's `[!]` items and anything dated within 7
days. Nothing else, and not again in that session unless something changes or I
ask for it.

**`## Blockers` and `## In Progress` use the same markers and the same sort**, so
one scan finds everything and the most urgent entry is always first. How the work
went is told in the dated notes, not by the order of the list. Mark an in-progress
item `[!]` when it is blocked or has a date bearing down on it.

**How to apply:** assign a marker whenever you add or touch a TODO, blocker or
in-progress item — never write a bare `- ` bullet under those headings. When you
touch any item in one of those lists, re-sort that whole list before saving. When a date comes up in conversation ("the
migration is the 15th"), convert it to `by YYYY-MM-DD` and attach it right then.

**Dated files are history — never re-prioritize them.** These markers apply to
`current/<project>.md` and to newly written entries. A past `<date>/<project>.md`
records what was true that day; if something was a TODO then, it stays a TODO
there even though it has since been done. Reconcile `current/`, never the archive.

## Daily notes upkeep (nudge after a big task)

After finishing a **substantial task** — a feature/fix that lands, a non-trivial investigation or root-cause, a commit/MR/merge, a meaningful decision — record it in my daily notes. This is for milestones, not every turn: skip small/trivial steps and pure Q&A.

**Log it the moment it lands — same response, no batching.** The instant a piece of substantial work completes (the fix works, the image/commit/MR is pushed, the root cause is nailed, the call is made), write the daily-note entry *in that same turn*, before moving on to the next thing or ending the response. Do NOT save it for "later" or "at the end" — deferring is exactly when it silently drops, because in a long multi-turn task the live work always wins and the log never happens. If one effort lands in pieces across several turns, log each piece as it lands.

**End-of-turn self-check (whenever work landed this turn):** before finishing the response, ask: *did substantial work complete this turn, and is it already in today's `<date>/<project>.md` Accomplishments (with `current/` reconciled)?* If not, add it now — don't end the turn until it's recorded. If the user ever has to ask "did you log that?", that's a miss this check exists to prevent.

**Layout:** `<notes>/<YYYY-MM-DD>/<project>.md` (not under `~/Documents` — that folder is macOS TCC-protected, which blocks agents/tools that lack a per-app grant, silently so in non-interactive runs) — `<YYYY-MM-DD>` is today's local date (compute it, e.g. `date +%F`); `<project>` is the project being worked on (git repo / working-dir name, e.g. `recipe-app`). One file per project per day. For work **not tied to a single project** — general tooling, automation, workflow/settings changes, the notes system itself — use `general` as the `<project>` (i.e. `<notes>/<YYYY-MM-DD>/general.md`). That kind of meta-work is an accomplishment in its own right and gets recorded there, not crammed into a project's file.

**Reports:** a large multi-file deliverable is not a daily note. It lives at
`<notes>/reports/<project>/<YYYY-MM-DD>/` — `<project>` exactly as in
`current/<project>.md`, and the date the version was written. Reports are **not**
transcripts; `transcripts/` stays meeting-only.

Grouped by project so a project's reports sit together, and by date so each version
stays whole. Before this layout, one report ended up spread across two date folders
citing its own sibling by two paths, and another filled with `-v2` / `-v3` copies of
the same document because there was nowhere else for the next version to go.

- **A multi-file report keeps all its files in one date folder**, so they cite each
  other by bare filename and keep resolving.
- **Name files for the report** (`<report>-00-index.md`, `<report>-findings.md`), since
  several reports can land in one project on one day.
- **Updating a report: copy its files from the newest date folder that holds them into
  today's folder and edit the copies.** A second update the same day edits today's copy
  in place.
- **One file per report per day, edited in place.** No `-v2`, no "kept unchanged" side
  copy, no second file for a revision, unless the user says to keep one: git carries the
  history. A new file is for a different report (another audience, window or kind), never
  for another version of this one.
- **Never edit an older date folder unless explicitly asked.** It records what the
  report said on that day — history, like a dated note.
- Do not rename files when copying forward or moving a report in — the
  cross-references depend on those names.
- `current/<project>.md` points at the report's newest file path, and is updated when a
  new version lands. `reports/README.md` indexes every report.

**Reports that end in decisions or fixes use the checklist format.** A digest of
things to decide, a review's findings, a plan: each is worked through over a day with
an agent, so it is a list to tick off, not prose to read once. Wall-of-text preambles
and wide tables with a cramped last column are how these became unreadable.

- **Title says what it is.** No weekday, no "tomorrow", no "weekend run"; the date and
  the time, with the zone, go in the header table. Run type (attended or not) is not
  part of the title.
- **Header as plain `Label: value` lines, not a table, then a summary of at most three
  sentences.** The lines are *Written*, *Last updated*, *Covers* (what was reviewed,
  and its commit or version) and *Progress* (`N of M done`). Sources go in a *Sources*
  list at the end. The checklist is read top to bottom, so there is no separate "start
  here" list.
- **Every item is a checkbox with a stable ID** (`A1`, `B3`), an imperative title, and
  the same lines under it: **Context** (what it is and why it came up, in two or three
  sentences, so it makes sense without opening another file), **Recommend**, **Why**,
  **Evidence** (a path or full URL) and **Done when**. A finding adds **Where** and
  **What goes wrong**. Each group heading gets one sentence saying what the group is.
- **Prefer lists to tables.** A table is for short, comparable values only: at most
  four columns, no `#` column (the ID lives in the item), no cell longer than a short
  phrase. A name with a link, or anything longer, is a list item.
- **Reviews come first, then work.** Put what waits on the user (decisions, drafts, reviews) in the first group, and work after it. Every item of new work says which north star measure or guardrail it serves; work that serves none goes under a *Parked* group and is not added to the list.
- **Group items by what you do next** (short decisions, fixes, drafts to send), then
  *Settled*, *Not checked* and *Log*. Leave a place for what the template did not
  expect, such as an *Added later* group.
- **Working through it is the point.** When an item is finished, in the same turn:
  tick it, add one line to the *Log* (time, what changed, a link), and update
  *Last updated* and *Progress*. Do not reorder, merge or drop items the user has not
  dropped, so the day stays on the list; new work goes under *Added later* with its
  time. A skipped item is ticked with the reason beside it.

**Pick the right project (every update):** before writing any of these files, decide which project the work actually belongs to — do NOT assume it's the session's origin project. A session that started on one project (e.g. recipe-app) may turn to a different project, or touch several at once. File under the matching `<project>.md` (or `general.md`); if the work spans a group of projects, update each one's files. That is *which* project; step 2 of the procedure below is what it is *called*, and both have to be right.

**`current/` live rollup:** `<notes>/current/<project>.md` is the single "what's open right now" view for each project. It holds no Accomplishments (those are the dated history), and these sections, in this order:
- `## North Star` (optional) — the end state every TODO works toward. Agreed with the user at the start of each `plan-iteration` and changed nowhere else.
- `## State` — at most five lines, stamped with date and time, **rewritten in place** (never appended to): how the project stands, where to look next, and the newest report. A copy goes into that day's dated file, so states can be compared over time.
- `## Blockers` — one entry per thing waiting on a person, sorted by marker like the TODOs, in this format (bullets, never a table, so it stays readable):
  ```markdown
  - [!] **Waiting on:** <person, team or group>
    - **What:** <what is waiting, in a sentence or two; the history lives in the dated note>
    - **Link:** <full URL>
    - **Since:** <YYYY-MM-DD>
  ```
  Every review, merge request, bug or ticket waiting on someone sits here with its **full URL**. **When it merges, closes or is abandoned, its entry leaves** — the dated Accomplishment that records the outcome keeps the link. A blocker with no live link is either not a blocker or is missing its link.
- `## In Progress` and `## TODOs` — one short entry each, with a pointer to the dated note or report that holds the history. The history itself does not live here. An In Progress item that something will be built for carries its **shape** indented under it — purpose, what gets built, what it reuses, what is not built, the decisions, and how we will know it is done — so working on it together and an unattended run build the same thing. When a plan is active, State names it: `Active plan: <YYYY-MM-DD>/<project>.md, Plans, HH:MM`.

**Capturing TODOs (any session, any project — this is global):** Whenever you raise, change, or finish a TODO in conversation — *not only* when a big task completes — immediately reflect it in BOTH that project's `current/<project>.md` and today's `<date>/<project>.md` TODOs, filed under the right project. This whole notes system is global across all sessions and projects: a TODO about a different project (even one raised mid-session here) is captured under *that* project, not the session's origin project.

**Procedure, every time:**
1. **Run `daily-notes-sync pull`.** These notes are shared between machines, so the file on this one can be stale before you open it. It commits nothing, so it is safe at any point. If it names a file you are about to write, re-read that file and reconcile — do not overwrite it with what you had in mind before you knew.
2. **Resolve the project name against the names already in use — never invent one without looking.** List `<notes>/current/` and the recent dated folders first, and check `<notes>/PROJECT-RENAMES.md`: a name listed there as **old** is never used again, even when a working directory, ticket or earlier transcript still carries it — file the work under its new name. If the work belongs to a project already logged, use *that* name exactly, even when another spelling reads better. Only create a new `<project>.md` when nothing there is this project.
3. Ensure today's date folder exists (create it if missing). Open the project file if it exists; otherwise create it with the headings below.
4. **Read the whole file first** to get the full picture before writing.
5. **Reconcile to keep it accurate:** move any item whose state changed into the right section — a TODO we've started → In Progress; a TODO or In-Progress item we've finished → Accomplishments.
6. Add or update the new work in the right section (update an existing entry in place, don't duplicate), then save.
7. **Run `daily-notes-sync`.** It pulls, commits and pushes. A note that never leaves this machine is not a note the other machines have.

**Links:** every merge request, review, bug and ticket gets its full URL the first time each entry mentions it — `https://tracker.example.org/issues/4821`, not a bare `4821`. A bare ID cannot be clicked, and an entry that needs a search before it can be acted on is an entry that waits.

**Why step 2 comes before everything else:** one project logged under two names (`dotfiles` and `dotfiles-ai`, `recipe-app` and `recipe_app`) splits its history in two, and neither half ever says so. The reconcile in step 5 then reconciles the *other* file — the new name's file has no open TODOs to contradict, so it reads as a clean project while the real one silently stops being updated. It is the one mistake here that looks more correct the longer it goes on.

**Sections (use these exact headings):**
- `## State` (first) — that day's copy of the `current/` State paragraph, replaced through the day as it changes, so the last version is the day's closing state. Lets any two days be compared.
- `## Plans` (when a plan was written that day) — one `### HH:MM — <together | unattended | together, then unattended> — active` entry per plan, written by `plan-iteration`. A plan names the In Progress items it covers, in order, and adds only what belongs to the plan: the window, the stretch items, and for an unattended stretch the approved writes over the network, what each item stops before, the limits, where alerts go, and how results leave the machine. It never restates an item's shape — that lives in `current/`. When the plan is finished or replaced, its status changes to `complete` or `replaced by HH:MM`. That status line is the one thing a past day's file may have changed, so a plan that ran past midnight is closed where it was written.
- `## Accomplishments` — short: what was achieved, how, and the workflow/approach, a sentence or two each. **Carry a metric and the scope wherever they exist** — see the section below.
- `## In Progress` — what we're actively working on and how we've approached it (path taken, findings, blockers); may be longer.
- `## TODOs` — identified work not yet started.
- `## Notes` — anything worth keeping that is not one of the above, written out in full. Two fixed lead-ins make the important kinds greppable across every day:
  - `**Decided (<who>, YYYY-MM-DD):**` — a decision and the reason for it. `grep -h -A4 '\*\*Decided (' <notes>/*/<project>.md` lists every decision for export.
  - `**Learned:**` — something that cost time or surprised us, and what to do about it next time.
  Anything else is a plain note, with no lead-in. Decisions and lessons go here even when the day's Accomplishments mention the work, because an Accomplishment's text is about what landed, not about what was decided or learned along the way.
- `## Meetings` (**always the last section in the page**) — recap of any meetings that day: attendees, what was decided, action items. **Dated files only — the `current/` rollup has no Meetings section.**

## Put a number on it — Accomplishments carry metrics and scope

**Every Accomplishment that moved something measurable states the measurement, as
before → after with the delta.** "Made it faster" records nothing. "Cut the run
from 12h to 2h, −83%" records something still quotable a year later.

Shapes that work:

| Kind | Write it as |
|---|---|
| Time or duration | `12h -> 2h (-83%)` |
| Rate or percentage | `62% -> 97% uptime` |
| Breadth | `20+ components`, `2 regions -> 9` |
| Volume or size | `1.2 TB -> 150 GB (-88%)` |
| Defects | `7 found, 4 of them in paths that had been reporting success` |
| Throughput | `~40 runs/day -> ~400` |

Rules for the numbers themselves:

- **Give before AND after.** A lone "now at 97%" cannot be turned into a
  contribution later; `62% -> 97%` can.
- **Say where the number came from** whenever it is not obvious — measured,
  computed, or estimated. An estimate labelled as one is useful; an estimate that
  reads as measured is a claim that will get quoted back.
- **A range, a floor, or an order of magnitude beats a fabricated point value.**
  `20+`, `~3x`, `at least a day` are all honest. Inventing `23.4%` is not.
- **Round honestly.** Three significant figures is nearly always more than
  enough, and false precision reads as padding.
- **If nothing was measurable, say what changed in kind instead** — a capability
  that did not exist before, a failure mode that can no longer happen, a manual
  step that is now automatic. Never manufacture a metric to satisfy this rule.

**Why:** these notes are the raw material for status updates, handovers, reviews
and promotion packets, and by the time any of those gets written the numbers are
gone. "How much faster did that actually get?" is usually unanswerable six months
on, and the honest answer becomes a shrug — so the work reads as smaller than it
was. The number costs one clause at the time and cannot be recovered afterwards.

**How to apply:** when writing an Accomplishment, ask "what was it before?" If
there is an answer, it belongs in the line. And whenever a measurement surfaces
during the work at all — a timing, a row count, a pass rate, a size — capture it
in the note even when the entry is about something else. That is the moment it is
cheapest to record, and the last moment it is free.

### Scope — how far it reached, and the guardrails that keep it honest

**Say who and what a change affected, not only what changed.** A measurement says
how much moved; scope says how far it went. `2 regions -> 9`, `every caller of
the shared config`, `unblocked two people who had been stuck a week`. Without it,
a change touching one script and a change touching everything read identically.

The guardrails matter more than the field does, because scope is the part that
rots into self-promotion first:

- **State the reach you can point at, not the reach you can imagine.** "Everyone
  who uses it" is a claim; "the four callers that import it" is a fact. When the
  real number is unknown, write that it is unknown.
- **Count what was affected, not what could be.** Potential reach is a forecast.
  Label it as one or leave it out.
- **Second-order effects belong to whoever produced them.** That a fix later
  unblocked a launch is not your scope unless you did that part too.
- **Understate rather than overstate.** An entry that reads smaller than the work
  costs a little when it is read back. One that reads bigger costs the
  credibility of every other entry in the file.
- **"One file, one caller" is a legitimate entry.** Most work is small, and a
  notes file where everything is far-reaching is a file nobody believes.

**Why the guardrails and not just the rule:** the whole value of these notes is
that they are true. The moment an entry is written to impress rather than to
record, the archive stops working as evidence — including the accurate parts,
because nothing afterwards distinguishes them. An accurate small number survives
being checked; an inflated one loses the argument the first time somebody does.

**When to reach for the skill:** a meeting recap, a backfill, or anything
`daily-notes-sync` said that you did not expect — **invoke the `daily-notes`
skill**. It carries the recap procedure, transcript saving, the sync output
table, conflict handling, and the dating rules for work you did not watch
happen. Logging work that just landed needs nothing beyond what is above.
