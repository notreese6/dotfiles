<!-- ai-rules: order=20, default=on, prompt="Include the daily-notes rules" -->

# Daily notes

An opt-in module. `ai-rules apply` includes this when `modules."daily-notes"`
is true in the config, which it is by default — the module declares `default=on`,
since including it only appends a section.

Take this repo and you inherit the notes discipline on its own: nothing here
depends on `misc.md`, which is notreese's general opinions and is off unless
you ask for it.

## Daily notes upkeep (nudge after a big task)

After finishing a **substantial task** — a feature/fix that lands, a non-trivial investigation or root-cause, a commit/MR/merge, a meaningful decision — record it in my daily notes. This is for milestones, not every turn: skip small/trivial steps and pure Q&A.

**Log it the moment it lands — same response, no batching.** The instant a piece of substantial work completes (the fix works, the image/commit/MR is pushed, the root cause is nailed, the call is made), write the daily-note entry *in that same turn*, before moving on to the next thing or ending the response. Do NOT save it for "later" or "at the end" — deferring is exactly when it silently drops, because in a long multi-turn task the live work always wins and the log never happens. If one effort lands in pieces across several turns, log each piece as it lands.

**End-of-turn self-check (whenever work landed this turn):** before finishing the response, ask: *did substantial work complete this turn, and is it already in today's `<date>/<project>.md` Accomplishments (with `current/` reconciled)?* If not, add it now — don't end the turn until it's recorded. If the user ever has to ask "did you log that?", that's a miss this check exists to prevent.

**Location:** `~/daily-notes/<YYYY-MM-DD>/<project>.md` (moved out of `~/Documents` on 2026-07-27 — that folder is macOS TCC-protected, which blocks agents/tools that lack a per-app grant, silently so in non-interactive runs) — `<YYYY-MM-DD>` is today's local date (compute it, e.g. `date +%F`); `<project>` is the project being worked on (git repo / working-dir name, e.g. `coverage-automation`). One file per project per day. For work **not tied to a single project** — general tooling, automation, workflow/settings changes, the notes system itself — use `general` as the `<project>` (i.e. `daily-notes/<YYYY-MM-DD>/general.md`). That kind of meta-work is an accomplishment in its own right and gets recorded there, not crammed into a project's file.

**Pick the right project (every update):** before writing any of these files, decide which project the work actually belongs to — do NOT assume it's the session's origin project. A session that started on one project (e.g. coverage-automation) may turn to a different project, or touch several at once. File under the matching `<project>.md` (or `general.md`); if the work spans a group of projects, update each one's files.

**`current/` live rollup:** `daily-notes/current/<project>.md` holds the live **In Progress + TODOs** for each project (no Accomplishments — those are the dated history). It is the single "what's open right now" view. On every update, re-read and reconcile the relevant `current/` file(s): promote a TODO to In Progress when it's started; when an item finishes, remove it from `current/` and record it as an Accomplishment in that day's dated file; add newly-surfaced TODOs. Keep `current/` matching reality.

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

**Also save the full transcript:** in addition to the recap, save the meeting's full transcript **verbatim** to `daily-notes/<date>/transcripts/<meeting-slug>.md` — a short header (meeting, date/time, attendees, recording link) followed by the raw transcript. If the transcript isn't retrievable — Teams keeps only the ~2 most recent transcripts per recurring series, and org meetings you didn't organize can return a 403 — note that in the recap instead of leaving an empty file.

**Markdown safety:** in note content, wrap any path, template, or placeholder that contains angle brackets in backticks (e.g. `<date>`, `<project>`, or a whole template like `daily-notes/<date>/<project>.md`). A raw `<word>` is parsed as an HTML tag by the renderer and silently breaks the line.

**Syncing across machines — `daily-notes-sync`.** These notes are shared between several machines, so a note written here can be stale before it is saved. Two commands, in this order:

1. **Before editing any note, run `daily-notes-sync pull`.** It reports what changed on the other machines and commits nothing, so it is safe to run at any point. If it names the file you are about to write, **re-read that file and reconcile** — do not overwrite it with what you had in mind before you knew.
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

**A failed push is not a failure.** The note is committed locally and goes out on the next sync. Do not retry in a loop, and do not treat it as a reason to stop working.

**If it says the directory is not a git repository**, say so and stop. Do not run `git init` — whether these notes become a repository is not an agent's decision.

**Why / how to apply:** this is a *nudge I follow*, not a `settings.json` hook — the summary and the section reconciliation need judgment a deterministic hook can't do, so it's best-effort. If I miss it, say "update daily notes."

**Accuracy / dating (I can't perceive elapsed time):** Always derive the date from `date +%F` at the moment of writing — never guess how much time has passed or which day past work happened on. A day's file holds only that day's work; never compress a multi-day arc into one file. When recapping or backfilling, treat `git log --date=short` commit dates (and timestamps in tool output) as the authoritative timeline — record commit-anchored work under its commit date, and mark diagnosis / non-commit work (which has no timestamp) as approximate. The rolling cross-session state lives in project memory (e.g. `jira-ticket-progress.md`); `daily-notes/` is the per-day record — maintain both.
