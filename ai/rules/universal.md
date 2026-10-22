<!-- ai-rules: order=10, required -->

# Using these rules

Where these rules come from, and the one thing that goes wrong if you do not know
it. Included on every assembly, whatever else is switched on.

Deliberately short. It declares `required`, so it lands on every machine whatever
else was turned down — which makes it the one file where adding a paragraph is a
decision made on someone else's behalf.

## Never edit the rules file you are reading

The file each agent reads is **generated output**, usually a symlink to it.
Editing it edits the assembly, and the next `ai-rules apply` overwrites the
change. The edit is gone and nothing says so.

## Resolve the paths, never assume them

Every path in this system is configurable, and none of them are the same on two
machines. The repo can be cloned anywhere, the private layer has its own setting,
and the config file itself honours `$XDG_CONFIG_HOME`. Ask:

```bash
ai-rules where
```

That prints the config, the rules source, the private layer, the assembled file,
and the file each configured agent reads. Use what it says.

If that command is unavailable, the config file is the fallback source of truth —
`ai_dir` names the rules source and `local_rules_dir` the private layer. **Do not
write a literal path into a rule**; it will be wrong on the next machine and give
no sign that it is.

## Which source a rule belongs in

| The rule is | Goes in |
|---|---|
| Private — an employer, an internal host, a codename | the private layer (`local_rules_dir`) |
| About keeping notes | `ai/rules/daily-notes.md` under the rules source |
| General, shareable, and notreese's opinion | `ai/rules/misc.md` under the rules source |
| About the rules system itself | the rules source repo's own `AGENTS.md` |

Then run `ai-rules apply` and confirm the text is in the assembled file. Adding a
rule is not done until that has run.

**Read that repo's `AGENTS.md` before changing anything in it.** It carries the
rest — how to add a module, the front-matter spec, how to check the subject is
not already covered, and what the hard errors are. Those instructions are only
actionable inside that repo, so they live there rather than in every session on
every machine.

**How to apply:** before editing any rules file, check whether it is a symlink
(`ls -l` on it). If it is, you are looking at generated output — run
`ai-rules where` to find the source.
