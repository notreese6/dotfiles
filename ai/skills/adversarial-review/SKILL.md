---
name: adversarial-review
description: >-
  Use when checking a finished piece of work by trying to break it, before it
  is called done or shown for review: a branch, a diff, a report
  with numbers in it, or a plan. Sends independent reviewers with fresh context
  to attack it from several angles, keeps only findings with a concrete way to
  fail, then tries to disprove each one before reporting it. Fires on:
  adversarial review, try to break this, review this before I look, red-team
  this, check this change, is this actually right.
---

# Adversarial review

The author of a change is the person least able to see what is wrong with it.
The same is true of an agent in the context that wrote it, which has already
convinced itself. This skill reviews from **outside** that context, and assumes
the work is wrong until a check fails to break it.

## Rules

- **Never review in the context that wrote the work.** Use subagents. Give
  them the change and the goal it was meant to meet. Do not give them the
  author's reasoning: they should judge what was written, not what was meant.
- **Every finding needs a failure scenario**: a specific input, state or
  sequence of steps, and the wrong result it produces. "This could be fragile"
  is not a finding.
- **Every finding is attacked before it is reported.** A second pass tries to
  disprove it by reading the code, running it, or checking the source. Only
  `CONFIRMED` (shown to fail) and `PLAUSIBLE` (not disproved, and the failure is
  realistic) survive.
- **Severity order**: wrong output, data loss, and silent failure come first.
  Style comes last, and only when it breaks one of the user's written rules.

## Lenses

Pick the lenses that fit what is being reviewed. One reviewer for a small
change; three or more in parallel for anything large or risky.

| Lens | The reviewer tries to show |
|---|---|
| **Correctness** | an input or state that gives a wrong result, a crash, or an edge case that is not handled |
| **Silent failure** | a path that does nothing and still reports success, an input that is missing but not checked, an empty result that cannot be told apart from a clean one |
| **Tests** | that the tests would still pass if the change were broken: mutate the key line and see whether any test fails |
| **Contract and rules** | a break with the user's code rules or the project's conventions: doc contracts, naming, layout, logging tags, no AI attribution, no internal names in public repositories |
| **Scope** | changes nobody asked for, things removed that were in use, or anything the plan said it would do that it did not |
| **Numbers** (reports) | a figure that does not match its source, a before or after with no date, a claim worded more strongly than the evidence supports |
| **Plan** (plans) | an item that needs a decision nobody has made, a "done when" that cannot be checked, or a step that would publish something |

## Procedure

1. **Frame it.** Collect the diff (or the document) and the goal: the plan
   item, the ticket, or the user's request. Note how to run the tests.
2. **Send the reviewers.** Run one subagent per lens, in parallel. Each one
   returns findings with a file and line, a one-line summary, and a failure
   scenario.
3. **Verify.** For each finding, run a separate check that tries to refute it.
   Drop anything that is refuted. Mark the rest `CONFIRMED` or `PLAUSIBLE`.
4. **Report.** If the `ReportFindings` tool is available, use it, ranked most
   severe first. Otherwise use one table:

   | # | Severity | Where | What fails | Scenario | Verdict |
   |---|---|---|---|---|---|

   If nothing survives, say so plainly and list the lenses that were run.
   Calling something clean without saying what was checked claims more than
   the review showed.
5. **Fix and review again** (in an unattended run, or when asked). Fix the
   confirmed findings, then run one more review pass on the fix only. Report
   whatever is still standing; do not loop until the reviewers give up.

## What this is not

It is not a style pass, and it does not replace the user's own review. A clean
result is a reason to show the work, not to merge it.
