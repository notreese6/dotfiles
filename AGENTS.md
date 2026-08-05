# Working in this repository

How the rules system works. This file is project-scoped on purpose: none of it is
actionable anywhere else, so carrying it in the assembled rules meant every
session on every machine paid for instructions about editing one repo.

The always-on rules keep only a pointer — where the rules live, and that the live
file is generated. Everything below is the detail behind that pointer.

`CLAUDE.md` beside this file is a symlink to it. `AGENTS.md` is the open standard
that Codex, Cursor and most other agents read natively; Claude Code does not read
it and insists on its own name, so the symlink is Anthropic's own documented
workaround. One file, two names — not two files to keep in step.

## Adding or changing a rule — edit the repo, never the live file

The rules file each agent reads is **generated output**, usually a symlink to it.
Editing it edits the assembly, and the next `ai-rules apply` overwrites the
change. The edit is gone and nothing says so.

`ai-rules where` prints every path involved on this machine. Use it rather than
assuming any of them — the repo can be cloned anywhere, the private layer has its
own setting, and the config honours `$XDG_CONFIG_HOME`, so a literal path written
into a rule is wrong on the next machine and gives no sign that it is.

So when I ask for a rule to be added, changed, or removed, edit the **source** and
re-assemble. Which source depends on what the rule is *and* on which modules this
machine actually has switched on — a module that is off is not assembled, so a
rule written into it is saved and then never reaches any agent:

| The rule is | Goes in | Only reaches an agent when |
|---|---|---|
| Private — an employer, an internal host, a codename | the private layer (`local_rules_dir`; `ai-rules where` prints it) | Always. This layer has no switch |
| About how this rules system itself works | this file | Always — it is read when working in this repo |
| About keeping notes | `ai/rules/daily-notes.md` | `modules."daily-notes"` is true |
| General, shareable, and notreese's opinion | `ai/rules/misc.md` | `modules.misc` is true |
| A subject none of those covers | a **new** `ai/rules/<name>.md` | `modules.<name>` is true |

**Check before writing, not after.** `ai-setup --dry-run` prints every module's
setting and changes nothing. If the natural home for the rule is a module that is
switched off, say so and offer the choice — turn the module on, or put the rule in the
private layer instead — rather than writing into a file nothing reads.

**Why:** an edit to the live file looks like it worked and survives until the next
apply, which may be days later and will not mention what it discarded. Editing the
source is the only change that lasts.

**How to apply:** before editing any rules file, check whether it is a symlink
(`ls -l` on it). If it is, you are looking at generated output — find the source in
the repo and edit that instead. Adding a rule is not done until `ai-rules apply`
has run.

## Before adding a rule, find out whether it already exists

The rules are one document by the time an agent reads them, so a second rule on a subject that already has one is not an addition — it is a fork. Two near-identical rules drift, and nothing reconciles them.

**Search first, against the file the agents actually read:**

```bash
grep -in "<topic>" "$(ai-rules where | awk '/assembled:/{print $3}')"
```

Then:

- **Something related exists → edit it in place.** Sharpen the existing wording rather than adding a second rule beside it. If the new point genuinely does not fit under it, say so and add a sibling deliberately, not by default.
- **What exists is in the wrong module → move it in the same change.** Do not leave a right-place copy next to a wrong-place one; that is the fork again, with extra steps. Moving means cut, paste into the right module, `ai-rules apply`, and confirm the text is in the assembled file exactly once.
- **Two rules that contradict each other is a bug, not two opinions.** Resolve it — decide which is right, delete or reword the other, and say which one changed. Leaving both makes every later reader pick one at random.
- **A private rule that would be true at a different employer belongs in the shareable module.** The private layer extends the general rule and says so ("Extends the shareable … rule"); it does not restate it. Specifics that name an internal system stay private, the principle behind them does not.

**Why:** the point of these modules is that each subject has one home. A rule in the wrong one still reaches an agent, so nothing fails visibly — it just means the next person to change that subject changes one of two copies.

**How to apply:** grep before writing, and when you find the subject already covered, prefer editing over appending. A rules file that grows only by addition stops being read.

## Adding a whole new module

`ai/rules/` is globbed, so **a new file is the entire change** — no constant, no
config key, no prompt to write. Give it a declaration on line 1:

```markdown
<!-- ai-rules: order=40, default=off, prompt="Include the review-checklist rules" -->

# Review checklist
```

| Entry | Means | Default |
|---|---|---|
| `order=N` | sort position, for assembly *and* for the order `ai-setup` asks | 50 |
| `default=on` / `off` | the answer used before anyone has been asked | `off` |
| `required` | never asked about, never off | absent |
| `prompt="..."` | the question asked; quote it if it contains a comma | built from the `# ` heading |

Declaring nothing is valid: the file is then asked about and off until you say
yes. The next `ai-setup` asks about it in `order` position and records the answer
under `modules` in the config; `ai-rules apply` wraps it in markers naming the
file, so the assembled document says where each section came from.

**The private layer works the same way** — same glob, same README skip, same
declaration line, same ordering, same markers. One difference: nothing there is
ever asked about, because a private file is machine-local and was put there
deliberately. So it applies unless it declares `default=off`, which is how a
private rule is shelved without deleting it. `required` and `prompt` have
nothing to act on there and are unused.

**Your agent files are replaced whatever you answer.** Configuring an agent is
what points its rules file at the assembled one; the module questions decide what
goes *into* that file, not whether it replaces yours. Saying no to every module
still leaves a symlink where your file was — just with less in it. `ai-setup`
says so before it asks anything, and the original goes to the backup directory.

**Two things are hard errors rather than skips**, because a rule silently missing
looks exactly like a rule being followed:

- A module the config switched on whose file has gone away. `ai-rules apply`
  refuses and writes nothing.
- Every layer empty. The live rules are left alone rather than replaced with a
  document holding none.

Then run `ai-rules apply`, which rebuilds the assembled file and leaves every
agent's symlink pointing at it. Confirm the new text is actually in the assembled
file afterwards — `ai-rules where` names it — because that is what agents read.

## Testing

```bash
python3 -m unittest discover -s ai/tests -t ai/tests
```

`install.sh` is prompt-driven and the suite drives it non-interactively, so any
new prompt needs a `[ -t 0 ]` guard or it blocks on a `read` nobody can answer —
and under `set -euo pipefail` a failed `read` aborts the whole script. Three bugs
of exactly that shape have already shipped. Tests that feed answers do so **by
position**, so adding a prompt silently shifts every later answer and surfaces as
an unrelated assertion.

Before pushing anything public, the pre-commit hook runs `leak-check`. Install it
once per clone — it lives in `.git/hooks/`, which git never tracks:

```bash
leak-check install-hook
```
