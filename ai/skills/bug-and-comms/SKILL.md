---
name: bug-and-comms
description: >-
  Use when triaging, filing, updating or discussing a bug, or when drafting
  anything that goes to another person as me — a bug comment, chat message,
  email, MR/PR description, or review comment. Covers what evidence to bring,
  how to present a root-cause chain, the register to write in, and who sends
  what. Fires on: triage, root cause, file a bug, comment on a bug, draft a
  message, write this up, send this to.
---

# Bugs and communicating with people

Everything here is about work that reaches another human, so the standard is
higher than for a note to myself: they cannot see what I saw, and they will act
on what I write.

If a private counterpart skill is installed, it extends this with the specifics
of one employer's trackers and tooling. It does not restate any of this.

## Communicating with people — always bring hard evidence and links

**Any time I am communicating a claim, finding, or request to another person, back it with hard evidence: the exact quoted line(s) and direct links to the proof.** This is medium-agnostic — it applies to bug creates/comments, Slack/Teams messages, emails, merge-request / pull-request descriptions and review comments, design docs, meeting follow-ups, and anything else that goes to a human. Never make the reader take my word for it or go hunt for the source; put the evidence in front of them.

At minimum, whatever the medium:

- **Quote the smoking gun verbatim** — the exact log line, error string, assert, code line, or metric value, inline. Not a paraphrase, not "it looked like X". If it's a range, quote the boundary lines.
- **Link directly to the proof** — the exact artifact URL (the specific file, not the containing folder), the job/run/build page, the dashboard/config page, the file+line, the bug/MR/commit. Primary source over "I saw that…".
- **Name the exact subject** next to each piece of evidence — the precise config tuple / host / branch / CL / test / commit / file:line the evidence is on, placed right beside that evidence, not a vague "the failing config" or "that machine".
- **Make links clickable and durable** — full URLs, not bare IDs. CI logs commonly expire (often ~2 weeks), so save a durable copy of the key files and offer to attach them if the links roll off.

**Why:** The recipient should be able to see exactly what I'm claiming and click straight to the proof, then act — not re-derive the repro, guess which config/host/commit I mean, or take an unverified assertion on faith. Vague or evidence-free communication wastes their time, erodes trust in what I report, and stalls the fix.

**How to apply:** Before sending any message, comment, bug, email, or review that makes a claim, ask: "have I quoted the exact evidence and linked directly to the proof, next to the exact subject it's about?" If not, add it. If a link may expire, save a durable copy alongside.

## Drafting comments and messages in my voice

When I ask you to write something I will send **as me** — a bug comment/update, Slack/Teams message, email, MR/PR note, review comment — or I say "in my voice" / "sounds like me" / "short" / "plain" / "me-like", draft it the way I actually write, not polished-assistant prose:

- **Short.** ~2 short paragraphs for a normal bug comment; often less. Cut ruthlessly — if a sentence isn't a fact or a next step, drop it. Err shorter than feels complete.
- **Plain sentences.** No bold, no headings, no tables, no em-dash-stacked or multi-clause sentences. Simple declarative statements. Minimal jargon.
- **Understate; never oversell.** Say "symptom" not "root cause" unless it's actually proven; hedge honestly ("possibly", "a symptom of this bug (possibly bugs)"); say "most of the coverage" not "the other ~81 binaries". Cut all editorializing — "pins it squarely on X", "graded it Better", "stop the bleeding", "definitively nails it" — state the fact and stop.
- **Structure = facts + one proof + what I'll do next**, in first person. The observable result; the single key piece of evidence (one job/CL/link — this is where the "hard evidence" rule lands: the ONE smoking gun, not a wall of links); then the plan ("the fix is in review; once it lands I will re-enable the test and get most of the coverage back").
- **No mechanism dumps.** Leave root-cause / register / how-it-works detail out unless I ask, or put it in a separate technical bug. The comment says *what* was observed and *what's next*, not *why it happens*.
- Show me the draft; I post it myself (I send my own @-mentions).

**Calibration:** an over-long draft (a mechanism paragraph, "root-caused it", and editorial phrasing) rewritten down to two plain paragraphs — the observable result, the one job or change that proves it, and what I will do next. That length, restraint, and plainness is the target.

**Why:** I write modest, factual, and brief. Over-claiming, mechanism dumps, bold/jargon, and editorial phrasing don't sound like me and I will rewrite them out — which wastes a round-trip.

**How to apply:** Default to this register for anything I'll send as me. It refines the two rules above, it doesn't fight them: still bring the key evidence (the "Communicating with people" rule), just the ONE smoking-gun link stated plainly; and note the "## Writing style" rules govern *your replies to me*, while this governs *what I send to others*.

## Bug root-cause & evidence — full chain, exact log + code lines, in blocks

Any time we discuss, triage, file, or show a bug — a tracker comment, a chat message, an email, an MR/PR, or just showing me a bug I asked about — give the FULL chain with hard evidence at every link: exact **log lines** AND exact **source-code lines** (`path:line` plus the actual code), tracing symptom → mechanism → root cause → the exact line(s) that need changing. Not a paraphrase, not a "tracking" blurb.

**Presentation:**
- **Start with a 1–2 line plain summary of the bug** (what fails, where, the verdict) before the chain.
- Put every piece of evidence in a fenced multi-line **code/log block** — a story is almost never one line, so show **3+ lines of context** (the offending line plus what surrounds it, or several consecutive log lines), with the `file:line` labeled above the block. Never a fragment inside a sentence.
- **Lead with the blocks;** they carry the chain in order (symptom log block → the source block that causes it → the downstream failure block). Prose goes between and after to explain, not wrapped around inline snippets. Never compress a block into a prose sentence.
- **Link every referenced artifact as a full raw URL** (see the Links rule): the CI job or run page, the specific log file, the change or commit, the bug, the config or dashboard page, and the source file. CI logs commonly expire, so save durable copies of the key files and offer to attach them.

**Why / how to apply:** I want to see the proof and click straight to it, not take it on faith. Actually dig — fetch the real job logs for the exact error lines, and read the real source at the right revision to quote the exact lines, rather than reasoning from a summary. Extends "Communicating with people — always bring hard evidence and links"; pairs with "Handling bugs — division of labor."

**Triage discipline (what makes a root cause trustworthy):**
- **Don't trust the fail signature or the auto-bucketed crash — verify the actual failing component.** Both routinely mask or misattribute the cause: an incidental crash in an unrelated process, a timeout that is really a slow copy, an "extraction failed" that is really a broken pipe. Separate the incidental crash from the real verdict, and confirm the faulting module is actually ours before blaming our code.
- **Route by authorship, not the default owner.** Find who owns the broken line through blame or annotate — the change and author that introduced it — not whoever is listed as the component's contact.
- **Watch for log contamination on shared runners.** A log that rolls across back-to-back jobs on one machine carries another job's lines; check the per-line job identifier before attributing anything to yours.
- **Overturn the surface story when the evidence says so, and state confidence honestly plus what still needs a live repro.** Good triage flips the filed conclusion — but only when the logs *and* the source were actually read, not when the signature was trusted.

## Handling bugs — division of labor (I prep and file, you send as yourself)

Any time we work a bug — triaging, root-causing, drafting, filing or updating it, or replying on one — the split is: **I do the prep up to the send boundary; you send anything that goes out as you.**

- **I do:** the triage and root-cause, draft the description and any comments, file or update the bug, set the reviewer/approver list, and the bookkeeping that is not addressed to a person.
- **You do:** review and approve, and **post the @-mentions and send anything that goes out as you** — the comment that @-mentions the owner, the chat ping, the email. You always send your own @-mentions.

**Why:** you want the final say and to send in your own name and voice; I move the work forward right up to "ready to send" so all that is left is you posting it.

**How to apply:** default to preparing everything to the point of *ready to send*, show you the draft, and wait for you to post or @-mention. Pairs with "Drafting comments and messages in my voice" and "Bug root-cause & evidence."

**Bug titles / synopses:** lead with **1–3 short `[Tag]` prefixes** for triage and search — area or component, plus the chip, branch, or config — then a **readable plain-English** description of the real error being fixed (a fail signature or error message is fine). The brackets categorize; the English explains. NO failure-rate numbers ("100%"), NO file names, NO `file:line`, NO code — that is all body-only. Don't let the whole title collapse into bracketed jargon, and don't drop the tags either.

**Reviewers / approvers:** cap at **2 people initially (3 including me)**, and **confirm each is the actual owner** — through authorship on the broken line, an OWNERS file, or the bug they came from — before adding anyone. Don't pad the list.
