<!-- ai-rules: order=10, required -->

# Using these rules

How this rules system works. Included on every assembly, whatever else is
switched on, because ignoring it is how someone edits a generated file and loses
the edit on the next run.

## Adding or changing a rule — edit the repo, never the live file

The rules file each agent reads is a **symlink to generated output**. Editing
`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, or `~/.config/ai-notes/rules.md`
edits the assembly, and the next `ai-rules apply` overwrites it. The edit is gone
and nothing says so.

So when I ask for a rule to be added, changed, or removed, edit the **source** and
re-assemble. Which source depends on what the rule is *and* on which modules this
machine actually has switched on — a module that is off is not assembled, so a
rule written into it is saved and then never reaches any agent:

| The rule is | Goes in | Only reaches an agent when |
|---|---|---|
| Private — an employer, an internal host, a codename | the private layer, `~/.config/ai-notes/local_rules/*.md` by default (`local_rules_dir` in the config says where) | Always. This layer has no switch |
| About how this rules system itself works | `ai/rules/universal.md` | Always — it declares `required` |
| About keeping notes | `ai/rules/daily-notes.md` | `modules."daily-notes"` is true |
| General, shareable, and notreese's opinion | `ai/rules/misc.md` | `modules.misc` is true |
| A subject none of those covers | a **new** `ai/rules/<name>.md` | `modules.<name>` is true |

**Check before writing, not after.** `ai-setup --dry-run` prints every module's
setting and changes nothing. If the natural home for the rule is a module that is
switched off, say so and offer the choice — turn the module on, or put the rule in the
private layer instead — rather than writing into a file nothing reads.

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
| `clobbers` | `ai-setup` names the files it will replace before asking | absent |
| `prompt="..."` | the question asked; quote it if it contains a comma | built from the `# ` heading |

Declaring nothing is valid: the file is then asked about and off until you say
yes. The next `ai-setup` asks about it in `order` position and records the answer
under `modules` in the config; `ai-rules apply` wraps it in markers naming the
file, so the assembled document says where each section came from.

**The private layer works the same way** — same glob, same README skip, same
declaration line, same ordering, same markers. One difference: nothing there is
ever asked about, because a private file is machine-local and was put there
deliberately. So it applies unless it declares `default=off`, which is how a
private rule is shelved without deleting it. `required`, `clobbers` and `prompt`
have nothing to act on there and are unused.

**Two things are hard errors rather than skips**, because a rule silently missing
looks exactly like a rule being followed:

- A module the config switched on whose file has gone away. `ai-rules apply`
  refuses and writes nothing.
- Every layer empty. The live rules are left alone rather than replaced with a
  document holding none.

Then run `ai-rules apply`, which rebuilds the assembled file and leaves every
agent's symlink pointing at it. Confirm the new text is actually in
`~/.config/ai-notes/rules.md` afterwards; that is the file the agents read.

**Why:** an edit to the live file looks like it worked and survives until the next
apply, which may be days later and will not mention what it discarded. Editing the
source is the only change that lasts.

**How to apply:** before editing any rules file, check whether it is a symlink
(`ls -l` on it). If it is, you are looking at generated output — find the source in
the repo and edit that instead. Adding a rule is not done until `ai-rules apply`
has run.
