---
name: adversarial-review
description: >-
  Use for an outside, no-context review that tries to prove the work is broken,
  messy or off course. Two scopes: a whole project (is it on track for its
  north star, working, clean, readable, consistent and up to date?) or one
  change (a branch, a diff, a report, a plan). Sends fresh reviewers that know
  only the goal, keeps only findings with a concrete failure, and attacks each
  finding before reporting it. Fires on: adversarial review, review the whole
  project, is this project on track, try to break this, red-team this, review
  this before I look, style pass, is this actually right.
---

# Adversarial review

Whoever built something is the worst judge of it: they read what they meant,
not what is there. This review is done by **outsiders**. They know where the
project is meant to be going, they do not know why anything was done the way
it was, and their job is to find out what is wrong.

It is wholehearted: correctness, direction, cleanliness, readability, style
and freshness all at once. A review that only checks that the tests pass
cannot tell a clean project from one that passes its tests while drifting.

## Ground rules

- **Reviewers start with no context.** Each one is a fresh subagent. It gets
  the scope, the north star, the user's written code rules, and how to run the
  tests. It does not get the conversation, the author's reasoning, or earlier
  reviews. Knowing why something was done is how a reviewer starts excusing it.
- **Every finding needs a failure scenario**: an input, state, reader or
  future change, and the concrete bad result. "Could be cleaner" is not a
  finding. "A reader changing the timeout edits one of two copies and the
  other silently keeps the old value" is.
- **Every finding is attacked before it is reported.** A second subagent tries
  to disprove it by reading the code, running it, or checking the source. Only
  `CONFIRMED` (shown) and `PLAUSIBLE` (not disproved, and realistic) survive.
- **Run things; don't just read them.** Run the tests, the build, each entry
  point's `--help`, and a sample of the documented commands. A README command
  that fails is a finding.
- **Report the state that was reviewed.** Name the commit or the time. A clean
  result describes that state and nothing after it.
- **The review changes nothing.** Fixing is a separate step, decided by the user
  or by the run that asked for the review.

## Scope

| Scope | When | Reviewers |
|---|---|---|
| **Project** | on request, at a milestone, before a release or handover, or when the work feels off course | every lens below, in parallel |
| **Change** | a branch, a diff, a report or a plan, before it is called done | the lenses that apply; one reviewer for a small change |

For a change, the reviewers still read the code around it. A change that is
correct in itself can still duplicate something that already exists two files
away.

## Lenses

| Lens | The reviewer tries to show |
|---|---|
| **Direction** | work that serves no part of the north star; a part of the north star the project has quietly stopped serving; TODOs or plans that contradict the north star or each other; effort going into polish while a core measure is stuck |
| **Broken** | a test, build or documented command that fails; an input or state that gives a wrong answer or a crash; an edge case that is not handled |
| **Silent failure** | a path that does nothing and reports success; a missing input that is not checked; an empty result that looks the same as a clean one |
| **Duplication and rewriting** | the same logic in two places; a new helper that reimplements one that exists; two ways of doing one job (two config readers, two HTTP clients, two date formats); code copied instead of shared |
| **Dead and stale** | unused code, flags, files and dependencies; comments that describe code that has since changed; `XXX - TODO` markers for work that is done, and unfinished paths with no marker |
| **Readable** | a function a newcomer cannot follow in one pass; a name that says the wrong thing; a dense line with no comment; a file whose order makes the reader jump around; `main` doing work instead of calling it |
| **Style and rules** | breaks of the user's written code rules and the project's own conventions: contracts, layout, naming, logging tags, argument parsing, file placement |
| **Tests** | tests that would still pass if the code were broken: mutate a key line and see whether anything fails; behaviour with no test; tests that check the mock instead of the code |
| **Up to date** | a README, usage text, docs or notes that no longer match the code; examples that do not run; dependencies or pinned versions that are stale or vulnerable |
| **In one place** | configuration, constants or knowledge scattered across files, notes and scripts; a fact recorded in two places that already disagree |
| **Safe to publish** | secrets, internal names, personal paths or anything identifying in a repository others can read |
| **Numbers** (reports) | a figure that does not match its source, a before or after with no date, a claim stronger than its evidence |
| **Plan** (plans) | a decision nobody has made; a "done when" that cannot be checked; a step that writes over the network without approval |

## Procedure

1. **Frame it.** Write a one-page brief for the reviewers: the scope (repository
   and commit, or the diff), the north star from `current/<project>.md`, the
   current plan if one exists, where the user's code rules live, and how to
   build and test. Nothing else.
2. **Review.** Run one subagent per lens, in parallel. Each returns findings with
   `file:line`, a one-line summary and a failure scenario.
3. **Attack the findings.** For each finding, run a separate subagent that tries
   to refute it. Drop the refuted ones. Merge duplicates found by several lenses.
4. **Report.** Start with one verdict per lens: **on track**, **drifting** or
   **broken**, each with a one-line reason. Then list the findings, most severe
   first: wrong results and silent failures, then direction, then duplication
   and staleness, then readability and style. Use `ReportFindings` if it is
   available; otherwise one table:

   | # | Lens | Where | What fails | Scenario | Verdict |
   |---|---|---|---|---|---|

   When a lens finds nothing, say what it checked. "Clean" without the list of
   checks claims more than the review showed.
5. **Hand off.** For a project review, offer to turn the findings into TODOs in
   `current/<project>.md` (as a `daily-notes-hygiene` change the user approves),
   and to save the report under `<notes>/reports/<project>/<date>/`. In an
   unattended run, fix confirmed findings that are inside the item's scope;
   record the rest in the run report.
