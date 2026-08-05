---
name: daily-notes
module: daily-notes
description: >-
  Use whenever writing, reading, reconciling or syncing the daily notes — logging
  work that just landed, recapping a meeting, updating a project's current/
  rollup, backfilling past days, or working out what daily-notes-sync just told
  you. Carries the meeting-recap procedure, transcript saving, the sync output
  table and conflict handling, backfill/dating rules, and markdown safety. Fires
  on: log this, update daily notes, write up the meeting, recap, reconcile
  current/, daily-notes-sync said, backfill, what happened on.
---

# Daily notes — the full procedure

The always-on rules carry what makes a note *correct*: where the notes live,
which file, the section headings, the TODO markers, reconciling `current/`. This
carries what makes one *good*, and the parts only needed occasionally.

If you are just logging work that landed, the always-on rules are enough. Reach
here for a meeting, a backfill, or when the sync says something unexpected.

## Sourcing a meeting recap — the transcript is only half of it

When building a meeting recap, do NOT stop at the transcript — **always also read
the meeting/Teams chat thread** and capture anything important shared there:
links, papers, shared docs, file/code paths, repro commands, follow-ups, or
decisions. Chat-only resources (a paper or drive link pasted mid-call, a code
path someone dropped) never appear in the spoken transcript and are silently
lost if you only read the audio. Fold those links and resources into the recap,
and into TODOs where they imply follow-up ("read the paper they linked").

`## Meetings` is **always the last section in the page**, and **dated files
only** — the `current/` rollup has no Meetings section.

## When a fetch fails — retry, then flag what a retry would fix

A failed chat or transcript fetch is not the same as one that has nothing in it,
and the difference decides what the follow-up should say.

1. **Retry once, immediately.** Most of these are transient.
2. **If it still fails, classify it.** A rate limit (HTTP 429) or a timeout will
   clear on its own. A 403, a missing transcript, or a deleted thread will not.
3. **Write the follow-up as the cheapest action that would actually work:**

| What failed | The TODO says |
|---|---|
| 429, timeout, anything transient | **re-fetch the chat later** — name the meeting and date so the next session can just run it |
| 403, absent, deleted | ask a person, and say which person and what for |

**Never turn a transient failure into a question for a colleague.** That is the
mistake worth naming: on 2026-08-05 a meeting chat returned 429 twice, and the
recap correctly recorded the gap — but phrased both follow-ups as "get this from
Aditya directly" and "follow up with Kailash directly". The rate limit cleared
within hours and one re-fetch recovered everything, so two people were queued to
be interrupted for something a retry would have fixed. The guidance to read the
chat had been followed; what was missing was any route back to it.

So when a fetch fails, say so **in the recap** *and* leave a `[>]` in
`current/<project>.md` naming the fetch, not the person. Re-reading a note does
not re-run anything — only a TODO framed as an action gets performed.

## Also save the full transcript

In addition to the recap, save the meeting's full transcript **verbatim** to
`<notes>/<date>/transcripts/<meeting-slug>.md` — a short header (meeting,
date/time, attendees, recording link) followed by the raw transcript.

If the transcript is not retrievable — Teams keeps only the ~2 most recent
transcripts per recurring series, and org meetings you did not organize can
return a 403 — note that in the recap rather than leaving an empty file.

## Backfilling, and dating things you did not watch happen

An agent cannot perceive elapsed time, so never guess how long ago something
was or which day it happened on.

- Derive today from `date +%F` at the moment of writing.
- A day's file holds only that day's work. Never compress a multi-day arc into
  one file.
- When recapping or backfilling, treat `git log --date=short` commit dates and
  timestamps in tool output as the authoritative timeline. Record commit-anchored
  work under its commit date; mark diagnosis and other non-commit work, which has
  no timestamp, as approximate.

## Markdown safety

In note content, wrap any path, template, or placeholder containing angle
brackets in backticks — `<date>`, `<project>`, or a whole template like
`<notes>/<date>/<project>.md`. A raw `<word>` is parsed as an HTML tag by the
renderer and silently breaks the line.

## Reading daily-notes-sync

It reads the same config, so it needs no path argument — run it from anywhere.

| It says | Means |
|---|---|
| `[*] already current` | nobody else has written since your last sync |
| `[+] N file(s) changed on the remote` | re-read the listed files before writing them |
| `[+] pushed` | your notes are on the remote |
| `[*] nothing to push` | the remote already has everything; nothing was sent |
| `[-] could not push` | committed locally, delivery pending. **Not a failure** — carry on |
| `[-] conflicting edits…` | **stop and ask.** See below |

`daily-notes-sync status` answers "is this set up, and where?" in one place,
changes nothing, and exits 0 whatever it finds. Run it when a sync reports
something you did not expect, or before concluding that notes are unavailable —
it distinguishes "no notes path configured" from "the directory is not a
repository" from "local only, nothing syncs", which a failed sync does not.

## A conflict means stop and ask

Two machines edited the same note and the tool will not choose between them,
because both sides are prose someone wrote. It aborts cleanly and leaves the
working tree exactly as it was — nothing is half-merged and there are no conflict
markers in any file. Report which files it named and wait; do not attempt to
reconcile them yourself.

## Sync being unavailable never excuses not logging

The note is the point; the syncing is delivery. Write it exactly as usual when
`daily-notes-sync` reports that the directory is not a git repository, that no
remote is configured, or that it could not reach the remote. Mention the state
once so it can be fixed, then carry on — a machine whose notes are local-only is
a working machine, not a broken one.

**A failed push is not a failure.** The note is committed locally and goes out on
the next sync. Do not retry in a loop, and do not treat it as a reason to stop.

**If it says the directory is not a git repository**, say so and stop. Do not run
`git init` — whether these notes become a repository is not an agent's decision.

## Why the surfacing rule is session-scoped

`[!]` items and anything dated within 7 days are surfaced once per session per
project, not per prompt, and with no stored timestamp. A "last surfaced" stamp in
`current/<project>.md` would rewrite the file every time it is merely *read*,
manufacturing cross-machine sync conflicts for no benefit. A session is already
about a work block, so once per session lands near once or twice a day on its own.

## Why the markers exist at all

A deadline written into prose is invisible. One project's rollup carried a hard
external deadline for days as an ordinary sentence in an ordinary bullet,
indistinguishable from a note about something already finished — and it was two
days out before anyone noticed. The marker and the date exist so a time-sensitive
item announces itself instead of waiting to be re-read.
