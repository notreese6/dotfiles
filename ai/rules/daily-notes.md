<!-- ai-rules: order=20, default=on, prompt="Include the daily-notes rules" -->

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
all** — on at least one machine it is `/disk01/home/reesew/daily-notes`.

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

**Run `daily-notes-sync pull` first.** Another machine may have written since
this one last synced, and answering from stale notes is worse than answering
from none — it is confidently wrong. If the notes directory turns out not to be
a repository, read it anyway; it is still the notes.

**If you find nothing, say which paths you checked.** "No notes exist" and "no
notes for that project" and "the configured path is empty" are three different
answers, and only the first is ever surprising.

## Prioritizing TODOs — markers, dates, and when to surface them

Every item under `## TODOs` carries one of four markers. They sort in this order,
and a TODO list is **always** written sorted:

| Marker | Means | Date |
|---|---|---|
| `[!]` | **URGENT** — a hard deadline inside 7 days, or blocked/blocking someone right now | **required** |
| `[>]` | **NEXT** — the thing to pick up next. Important, no hard date | optional |
| `[ ]` | **OPEN** — real work, will happen, not next | optional |
| `[~]` | **LATER** — worth keeping, no commitment | none |

```markdown
## TODOs
- [!] by 2026-08-14 — finish the auth migration on both controllers (bug 1234567)
- [!] blocked — post the unblock note on the review that has been stuck a week
- [>] commit + MR the poller phantom-trigger fix
- [ ] pull the unclaimed triage queue
- [~] prune the backup directory
```

**Sort order within a tier:** dated items first, by date ascending, then undated
items in the order they were already in. Re-sorting must never churn a line that
did not need to move.

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

This is deliberately session-scoped with no stored timestamp. A "last surfaced"
stamp in `current/<project>.md` would rewrite the file every time it is merely
*read*, manufacturing cross-machine sync conflicts for no benefit. A session is
already about a work block, so once per session lands near once or twice a day
on its own.

**`## In Progress` uses the same markers** so one scan finds everything, but it is
**not** force-sorted — its order carries the narrative of how the work went. Mark
an in-progress item `[!]` when it is blocked or has a date bearing down on it.

**Why:** a deadline written into prose is invisible. One project's rollup carried
a hard external deadline for days as an ordinary sentence in an ordinary bullet,
indistinguishable from a note about something already finished — and it was two
days out before anyone noticed. The marker and the date exist so a time-sensitive
item announces itself instead of waiting to be re-read.

**How to apply:** assign a marker whenever you add or touch a TODO — never write
a bare `- ` bullet under `## TODOs`. When you touch any TODO in a file, re-sort
that whole list before saving. When a date comes up in conversation ("the
migration is the 15th"), convert it to `by YYYY-MM-DD` and attach it right then.

**Dated files are history — never re-prioritize them.** These markers apply to
`current/<project>.md` and to newly written entries. A past `<date>/<project>.md`
records what was true that day; if something was a TODO then, it stays a TODO
there even though it has since been done. Reconcile `current/`, never the archive.

## Daily notes upkeep (nudge after a big task)

After finishing a **substantial task** — a feature/fix that lands, a non-trivial investigation or root-cause, a commit/MR/merge, a meaningful decision — record it in my daily notes. This is for milestones, not every turn: skip small/trivial steps and pure Q&A.

**Log it the moment it lands — same response, no batching.** The instant a piece of substantial work completes (the fix works, the image/commit/MR is pushed, the root cause is nailed, the call is made), write the daily-note entry *in that same turn*, before moving on to the next thing or ending the response. Do NOT save it for "later" or "at the end" — deferring is exactly when it silently drops, because in a long multi-turn task the live work always wins and the log never happens. If one effort lands in pieces across several turns, log each piece as it lands.

**End-of-turn self-check (whenever work landed this turn):** before finishing the response, ask: *did substantial work complete this turn, and is it already in today's `<date>/<project>.md` Accomplishments (with `current/` reconciled)?* If not, add it now — don't end the turn until it's recorded. If the user ever has to ask "did you log that?", that's a miss this check exists to prevent.

**Layout:** `<notes>/<YYYY-MM-DD>/<project>.md` (moved out of `~/Documents` on 2026-07-27 — that folder is macOS TCC-protected, which blocks agents/tools that lack a per-app grant, silently so in non-interactive runs) — `<YYYY-MM-DD>` is today's local date (compute it, e.g. `date +%F`); `<project>` is the project being worked on (git repo / working-dir name, e.g. `coverage-automation`). One file per project per day. For work **not tied to a single project** — general tooling, automation, workflow/settings changes, the notes system itself — use `general` as the `<project>` (i.e. `<notes>/<YYYY-MM-DD>/general.md`). That kind of meta-work is an accomplishment in its own right and gets recorded there, not crammed into a project's file.

**Pick the right project (every update):** before writing any of these files, decide which project the work actually belongs to — do NOT assume it's the session's origin project. A session that started on one project (e.g. coverage-automation) may turn to a different project, or touch several at once. File under the matching `<project>.md` (or `general.md`); if the work spans a group of projects, update each one's files.

**`current/` live rollup:** `<notes>/current/<project>.md` holds the live **In Progress + TODOs** for each project (no Accomplishments — those are the dated history). It is the single "what's open right now" view. On every update, re-read and reconcile the relevant `current/` file(s): promote a TODO to In Progress when it's started; when an item finishes, remove it from `current/` and record it as an Accomplishment in that day's dated file; add newly-surfaced TODOs. Keep `current/` matching reality.

**Capturing TODOs (any session, any project — this is global):** Whenever you raise, change, or finish a TODO in conversation — *not only* when a big task completes — immediately reflect it in BOTH that project's `current/<project>.md` and today's `<date>/<project>.md` TODOs, filed under the right project. This whole notes system is global across all sessions and projects: a TODO about a different project (even one raised mid-session here) is captured under *that* project, not the session's origin project.

**Procedure, every time:**
1. Ensure today's date folder exists (create it if missing). Open the project file if it exists; otherwise create it with the three headings below.
2. **Read the whole file first** to get the full picture before writing.
3. **Reconcile to keep it accurate:** move any item whose state changed into the right section — a TODO we've started → In Progress; a TODO or In-Progress item we've finished → Accomplishments.
4. Add or update the new work in the right section (update an existing entry in place, don't duplicate), then save.

**Sections (use these exact headings):**
- `## Accomplishments` — short: what was achieved, how, and the workflow/approach, a sentence or two each.
- `## In Progress` — what we're actively working on and how we've approached it (path taken, findings, blockers); may be longer.
- `## TODOs` — identified work not yet started.
- `## Meetings` (**always the last section in the page**) — recap of any meetings that day: attendees, what was decided, action items. **Dated files only — the `current/` rollup has no Meetings section.**

**Sourcing a meeting recap (transcript AND chat):** when building a meeting recap, do NOT stop at the transcript — **always also read the meeting/Teams chat thread** and capture anything important shared there: links, papers, shared docs, file/code paths, repro commands, follow-ups, or decisions. Chat-only resources (e.g. a paper or drive link pasted mid-call, a code path someone dropped) never appear in the spoken transcript and are silently lost if you only read the audio. Fold those links/resources into the recap, and into TODOs where they imply follow-up (e.g. "read the paper they linked").

**Also save the full transcript:** in addition to the recap, save the meeting's full transcript **verbatim** to `<notes>/<date>/transcripts/<meeting-slug>.md` — a short header (meeting, date/time, attendees, recording link) followed by the raw transcript. If the transcript isn't retrievable — Teams keeps only the ~2 most recent transcripts per recurring series, and org meetings you didn't organize can return a 403 — note that in the recap instead of leaving an empty file.

**Markdown safety:** in note content, wrap any path, template, or placeholder that contains angle brackets in backticks (e.g. `<date>`, `<project>`, or a whole template like `<notes>/<date>/<project>.md`). A raw `<word>` is parsed as an HTML tag by the renderer and silently breaks the line.

**`daily-notes-sync` reads the same config**, so it needs no path argument — run it from anywhere.

**`daily-notes-sync status` answers "is this set up, and where?" in one place**, changes
nothing, and exits 0 whatever it finds. Run it when a sync reports something you did not
expect, or before concluding that notes are unavailable — it distinguishes "no notes path
configured" from "the directory is not a repository" from "local only, nothing syncs", which
a failed sync does not.

**Syncing across machines — `daily-notes-sync`.** These notes are shared between several machines, so a note written here can be stale before it is saved. Two commands, in this order:

1. **Before reading or editing any note, run `daily-notes-sync pull`.** It reports what changed on the other machines and commits nothing, so it is safe to run at any point. If it names the file you are about to write, **re-read that file and reconcile** — do not overwrite it with what you had in mind before you knew.
2. **After logging, run `daily-notes-sync`.** It pulls, commits everything, and pushes.

What its output means:

| It says | Means |
|---|---|
| `[*] already current` | nobody else has written since your last sync |
| `[+] N file(s) changed on the remote` | re-read the listed files before writing them |
| `[+] pushed` | your notes are on the remote |
| `[*] nothing to push` | the remote already has everything; nothing was sent |
| `[-] could not push` | committed locally, delivery pending. **Not a failure** — carry on |
| `[-] conflicting edits…` | **stop and ask.** See below |

**A conflict means stop and ask.** Two machines edited the same note and the tool will not choose between them, because both sides are prose someone wrote. It aborts cleanly and leaves your working tree exactly as it was — nothing is half-merged and there are no conflict markers in your files. Report which files it named and wait; do not attempt to reconcile them yourself.

**Sync being unavailable never excuses not logging.** The note is the point; the
syncing is delivery. Write it exactly as usual when `daily-notes-sync` reports
that the directory is not a git repository, that no remote is configured, or
that it could not reach the remote. Mention the state once so it can be fixed,
then carry on — a machine whose notes are local-only is a working machine, not a
broken one.

**A failed push is not a failure.** The note is committed locally and goes out on the next sync. Do not retry in a loop, and do not treat it as a reason to stop working.

**If it says the directory is not a git repository**, say so and stop. Do not run `git init` — whether these notes become a repository is not an agent's decision.

**Why / how to apply:** this is a *nudge I follow*, not a `settings.json` hook — the summary and the section reconciliation need judgment a deterministic hook can't do, so it's best-effort. If I miss it, say "update daily notes."

**Accuracy / dating (I can't perceive elapsed time):** Always derive the date from `date +%F` at the moment of writing — never guess how much time has passed or which day past work happened on. A day's file holds only that day's work; never compress a multi-day arc into one file. When recapping or backfilling, treat `git log --date=short` commit dates (and timestamps in tool output) as the authoritative timeline — record commit-anchored work under its commit date, and mark diagnosis / non-commit work (which has no timestamp) as approximate. The rolling cross-session state lives in project memory (e.g. `jira-ticket-progress.md`); the notes directory is the per-day record — maintain both.
