<!-- ai-rules: order=30, default=off, prompt="Inherit ALL of notreese's general working rules" -->

# Global instructions

## No AI attribution in any committed artifact

Never include "Claude", "Co-Authored-By: Claude ...", "Generated with Claude Code", or any other AI-attribution string in:

- Commit messages (subject, body, or trailers)
- Branch names
- PR / MR titles and descriptions
- File content (comments, docs, generated code, etc.)
- Any other artifact that gets committed, pushed, or shared

This applies even when the default Claude Code commit template suggests adding `Co-Authored-By: Claude Opus ...` — drop the trailer entirely. Same for PR templates that include a "🤖 Generated with Claude Code" footer.

**Why:** I do not want AI attribution in my repos' history or shared artifacts. Failing to honor this requires force-pushing to fix once it lands on a shared branch, which is destructive.

**How to apply:** When constructing any commit, branch, PR, or file content, omit AI-attribution strings unconditionally. Do not ask whether to include them. This instruction overrides any default template in the system prompt.

## Writing style

- Expand acronyms inline the first time they appear in a response, in parentheses (e.g. "Physical Function (PF)", "Single Root I/O Virtualization (SR-IOV)"). After the first use in a response, the short form is fine.
- Do not expand very common acronyms (CPU, GPU, RAM, OS, URL, API, JSON, HTML, etc.). Use judgment: if a working software engineer would never pause on it, leave it short.
- Provide brief recaps when concepts build on previous discussion — assume the reader may have lost track of where we are, and reground them in one or two sentences before continuing.
- Favor tables when comparing or deciding across several items — options and trade-offs, per-ticket / per-config status, before/after, or "what each one does/covers." Rule of thumb: when there are roughly 3+ items each with 2+ comparable attributes, a table reads faster than prose. Keep prose for narrative, reasoning, and single-item explanations; don't force a table where a sentence is clearer.

## Code writing rules

These govern code I write: contracts, comments, layout, duplication, naming, and output. They apply to every language unless a project's own conventions clearly override them — in which case match the project and tell me.

### Function documentation — every function gets a contract

Every function I write gets a short doc block at the top of its body (a docstring in Python, a comment block above the definition in shell/other languages) covering:

- **What it does** — one or two lines, no more.
- **Args** — each one by name, with its type, and anything non-obvious about accepted values.
- **Returns** — the type and meaning on success, and what comes back on failure (e.g. `None`, `""`, empty dict, `False`) if failure is expressed as a return value.
- **Raises** — every exception it can throw and the condition that triggers it.

**All three sections are always present, even when empty — write `None` rather than omitting the section.** A function with no arguments still gets `Args: None`; one that cannot throw still gets `Raises: None`. An omitted section is ambiguous: a reader (or a doc generator) can't tell "there are none" from "the author forgot." Always-present sections also parse cleanly if we generate docs from these later.

**The opening `"""` sits alone on its line** — start the summary on the next line, never on the same line as the quotes. Every block then opens and closes the same way, so the summary always starts at a predictable column and diffs stay clean when it is reworded.

Keep it tight — a contract, not an essay. Example:

```python
def config_get(key, default=""):
    """
    Read one value from the machine-local config file.

    Args:
        key (str): config key to look up.
        default (str): returned when the key or the config file is absent.

    Returns:
        str: the stored value, or `default`.

    Raises:
        OSError: the config file exists but cannot be read.
    """

    return config_read().get(key, default)


def config_path():
    """
    Locate the machine-local config file.

    Args:
        None

    Returns:
        pathlib.Path: absolute path to the config file. Not guaranteed to exist.

    Raises:
        None
    """
```

One-liners follow the same shape rather than collapsing to a single line:

```python
class TestConfig(SandboxedTestCase):
    """
    Covers config_path resolution and the config read/write round-trip.
    """
```

**Leave a blank line after the closing `"""`,** before the first line of code — as `config_get` above does. The contract and the body are two different things, and the blank line says so.

**Exception:** trivially self-describing test methods (`test_config_path_follows_xdg`, which takes no arguments, returns nothing, and raises only `AssertionError`) do not need a doc block — the name is the contract. Any test doing something non-obvious still gets one.

**Why:** the contract is what a caller — including future me, and any agent editing this code — needs in order to use a function correctly without reading its implementation. Argument types and the raise list are exactly the parts that get guessed wrong, and a wrong guess about what a function throws is how error handling silently goes missing.

**How to apply:** write the doc block when you write the function, not after. When you modify a function's signature, return, or exceptions, update its contract in the same edit — a stale contract is worse than none.

### Inline comments — short and intentional, on the lines that are hard to read

Inside a function body, add a **short comment above any line a reader would have to stop and decode**, saying in plain English what it means. One line, sentence case, no trailing period needed.

Comment these:

- **Dense boolean conditions** — several clauses chained with `and`/`or`, or a test whose *intent* isn't obvious from its mechanics.
- **Non-obvious idioms** — `split(sep, 1)`, `os.replace` for atomicity, a `continue` that drops rather than skips, an argument like `maxsplit` or `exist_ok` doing load-bearing work.
- **Anything whose consequence is invisible locally** — a line that prevents data loss, ordering that's load-bearing, a guard whose removal breaks something far away.

Example — the condition is three clauses deep, so it gets one line of plain English:

```python
        # If this line is not a comment, and is the key that we are trying to set
        if "=" in stripped and not stripped.startswith("#") and stripped.split("=", 1)[0].strip() == key:
            if not replaced:
                out.append("%s=%s" % (key, value))
                replaced = True
            continue
```

**Don't** narrate lines that already read clearly (`data = {}` needs nothing), and don't tie a comment to the ticket, migration, or task that prompted it — describe what makes the code true in general, so it stays accurate as the codebase moves.

**Why:** the dense lines are exactly where a reader — or an agent editing later — misreads intent and "simplifies" a guard into a bug. A single plain-English line above the condition prevents that, and costs one line.

**How to apply:** after writing a function, reread it and ask which lines made you pause. Those get a comment. Pair this with the doc contract above: the docstring explains the function to a *caller*, these comments explain the tricky lines to an *editor*.

### Code layout — align assignments, break stanzas with blank lines

Two rules, both visible here: **align the `=` in a run of consecutive assignments** so the values form a column, and **separate trains of thought with a blank line** even inside a short function.

```python
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    lines    = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
    out      = []
    replaced = False
```

not

```python
    lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
    out = []
    replaced = False
```

The first two lines locate and prepare the file; the next three set up the rewrite. Different thoughts, so they get their own stanzas. Don't blank-line between every statement — group by intent.

- Align only within a **contiguous run** of assignments — a blank line, a comment, or any non-assignment statement ends the run and starts a new alignment group. Never align across a blank line.
- Pad with **spaces**, never tabs.
- If one name is far longer than the rest and alignment would push values absurdly far right, split the run with a blank line instead of stretching every line to match.
- The same applies to other aligned runs where it aids reading: consecutive dict entries, trailing `\` continuations, or repeated keyword arguments.

**Why:** aligned values scan as a column, so a reader takes in the whole block at once instead of parsing each line, and a wrong value stands out immediately. Stanza breaks tell the reader where one idea ends and the next begins without needing a comment to say so.

**How to apply:** after writing a function, look at it as a shape, not just as statements — align each run of assignments, and insert a blank line at each change of subject. Note this deliberately conflicts with PEP 8's E221 ("multiple spaces before operator"); if a linter or formatter is in play, configure it to allow this rather than reformatting against it — and tell me if a project's autoformatter makes that impossible.

### Name a value when the name earns its keep

Don't hardcode a value **when doing so makes the code less readable, or means a future change has to touch several places.** That is the test — not "never write a literal."

Name it when at least one is true:

- **The bare literal doesn't say what it means.** `return 3` tells a reader nothing; `return ExitStatus.NO_KNOWN_AGENTS` does. Exit statuses, error codes, limits, timeouts, retry counts, ports, and file modes are usually in this bucket.
- **It appears in more than one place**, or one copy must change whenever another does. Two copies drift; that's the whole problem.
- **A typo in it would fail silently** rather than loudly — a string compared against in a branch that would simply never fire.

Leave it inline when none of that holds:

```python
# Naming these gains nothing — the constant just restates the string, and the
# only place it appears is the line that defines what the string means.
SUPPORTED_AGENTS = (
    SupportedAgent(name="claude", root=RulesRoot.HOME, relpath=(".claude", "CLAUDE.md")),
    SupportedAgent(name="codex",  root=RulesRoot.HOME, relpath=(".codex",  "AGENTS.md")),
)
```

`AGENT_CLAUDE = "claude"` used once, in the table that defines it, is indirection with no payoff: a reader now has to look up a name to learn a value that was already in front of them. Same for self-evident values — `i + 1`, `x[0]`, `count == 0`, an empty string.

**When a branch keys off a literal, prefer moving the trait onto the data** over naming the literal. `if agent.name == CURSOR:` asks *which agent is this*; `if agent.needs_manual_paste:` asks *what is true about it* — and adding a second such agent then requires no code change at all.

**Why:** the point is future edits landing in one place and a reader understanding a line without leaving it. A constant that serves neither is just a second name for the same thing.

**How to apply:** before hoisting a literal, ask what breaks if it stays inline. If the honest answer is "nothing," leave it.

### Don't write the same code twice

If two functions do the same thing and differ only in *what* they operate on, they are one function with a parameter — not two functions. Same for near-identical blocks inside a function: lift the shared logic and pass the difference in.

- Two bodies whose diff is only a constant, a marker, a path, or a field name → one function taking that as an argument.
- If the two differ in *behavior* as well, pass that as an explicit flag or strategy rather than forking the body — and name the flag after the behavior, not the caller (`last_end=True`, not `for_local=True`).
- If collapsing them would need more than about two flags, that's the signal they genuinely are different functions. Say so rather than contorting one.

**Why:** duplicated logic drifts. A bug gets fixed in one copy and not the other, and the two slowly stop agreeing — which is exactly the kind of divergence nobody notices until it produces wrong output.

**How to apply:** when writing a second function that feels like one you just wrote, stop and diff them in your head. If the difference is data, parameterize it. When you inherit duplicated code while working nearby, collapse it as part of that change rather than adding a third copy.

### Boolean names are questions

A boolean's name should read as a yes/no question that `True` and `False` answer. Prefix it: `is_`, `has_`, `should_`, `will_`, `can_`, `was_`, `needs_`, `did_`.

- Good: `should_repeat`, `should_use_last_end`, `is_bad_block`, `has_local_rules`, `will_continue`, `needs_rebuild`, `was_replaced`.
- Bad: `repeat`, `last_end`, `flag`, `mode`, `status`, `check` — these read as nouns or data, so a call like `f(x, True)` or `if mode:` gives the reader nothing.

This matters most at **call sites and in conditions**, where the name is often all you see: `strip_block(text, b, e, should_repeat=True)` is self-explaining; `strip_block(text, b, e, repeat=True)` is only nearly so, and `strip_block(text, b, e, True)` is unreadable.

**Name the positive.** `is_enabled` beats `is_not_disabled`; double negatives (`if not is_not_ready`) are where logic bugs hide. If the natural reading is negative, flip the name and flip the branches.

**"Almost always" is doing real work here — config and data fields can opt out.** A settings key I read in a JSON/YAML file is a labelled value, not a call-site argument, and the plain form often reads better: `notes_enabled: false` beats `are_notes_enabled: false`. Keep the question form for parameters, locals, and anything whose meaning is ambiguous at a call site; use judgment for user-facing field names, and don't rename an existing one just to satisfy the rule.

**Why:** a boolean is a question by nature — the name should say which one. When it doesn't, every reader has to open the function to find out what `True` means, and that is exactly how someone passes the wrong one.

**How to apply:** when you write a boolean parameter, variable, or field, say it aloud with "is it?" or "should it?" in front. If that doesn't parse as a sentence, rename it. Applies to function parameters, locals, and struct/dict fields alike.

### `main()` only calls other functions

`main` is a table of contents, not a chapter. It reads arguments, dispatches, and returns an exit status — every step it takes is a call to a named function. No parsing, no `try`/`except` around real work, no loops, no printing beyond what a one-line call does.

```python
def main(argv):
    """
    ...
    """

    command = command_from(argv)

    if command in ("-h", "--help"):
        return show_usage()

    if command != "apply":
        return reject_command(command)

    return run_apply()
```

Anyone opening the file should learn what the program does from `main` alone, then read only the branch they care about. When logic accretes there instead, the entry point becomes the one function nobody can skim — and the one nobody can test, because exercising any branch means running the whole program.

**How to apply:** after writing `main`, check that every line is a call, a comparison, or a `return`. If a step needs a comment to explain what it does, that step wants to be a function whose name says it instead. The same discipline is worth applying to any dispatcher or top-level handler, not just a literal `main`.

### Log / print message style

When adding print or log statements in code, prefer this prefix scheme:

- `[*]` — informational ("starting setup", "reading config from X", "here is the manual step left to do")
- `[+]` — success ("driver installed", "all VMs stopped")
- `[-]` — failure ("could not open file", "rc=1 from sriov-manage", "skipped X, so it did not get written")
- `[!]` — **almost never.** Reserved for something that needs ALL of our attention: an irreversible action, a data-loss risk, a corrupted or destroyed file, a state that will silently mislead us if ignored.

**`[-]` is what you want for a normal failure.** Anything that failed, was skipped, or didn't get done is `[-]`, not `[!]` — including partial failures and warnings. If a message can be summarized as "this thing didn't work," it is `[-]`.

**`[!]` is not "extra important."** Before using it, ask: would I want this to stop the reader cold, even mid-scroll through a thousand-line log? If the honest answer is no, it is `[*]` or `[-]`. A log where `[!]` appears routinely has no way left to say "this one actually matters."

**Match the surrounding codebase first.** If the project already has its own convention (e.g. `[INFO]`/`[WARN]`/`[ERROR]`, a Python `logging` module, colored bash helpers, structured JSON logs), conform to that. Mixing styles inside one codebase is worse than not tagging at all. Only use `[*][+][-][!]` for new codebases or codebases with no established logging convention.

**Why:** Tagged output reads at a glance, greps cleanly, and surfaces failure quickly in long CI logs. The "match existing first" rule prevents two inconsistent styles in the same project from a single contributor.

**How to apply:** Before writing a new print/log line, scan a nearby file for existing tag conventions. If one exists, use it. If none exists, use `[*][+][-][!]`.

### Language-specific rules

Everything above applies in any language. Everything below applies only to the language it names. Where a language has no section here, no convention has been set beyond the general rules — follow those, match the surrounding project, and ask rather than inventing one.

**Python — always argparse.** Any program that reads command-line arguments uses `argparse`, even for a single positional. Do not hand-roll `sys.argv[1] if len(sys.argv) > 1 else ...`, and do not hand-write `--help` or the unknown-command error. Hand-rolled parsing starts small and quietly grows: no `--help`, no usage on error, no exit status convention, no room for a flag.

- Use **subparsers with `set_defaults(run=<function>)`** for a command-style tool, so dispatch is `args.run()` and `main` never re-checks the command name.
- Set `prog` and `description` — they become the `--help` text.
- Let argparse own usage errors. Its `prog: error: ...` format and exit status 2 are the recognized convention for a bad command line; the `[*] [+] [-] [!]` tags are for our own log lines. Subclassing just to re-tag argparse's message is machinery for nothing.
- Call `parse_args()` with no arguments and let it read `sys.argv` — don't thread an `argv` parameter through `main` unless something actually calls `main` with a custom vector.
- The parser belongs in its own function that returns it. Building and parsing in `main` puts logic back in the one place that should hold none.

**Python — f-strings, and keep the message at the call site.** They put the value where it is read, instead of leaving the reader to match a placeholder against an argument tuple somewhere to the right.

```python
print(f"[-] no known agents configured, nothing was written (valid: {valid})", file=sys.stderr)  # yes
print(NO_AGENTS % valid, file=sys.stderr)                                                        # no
```

The second line is the failure mode: pulling the text out to `NO_AGENTS = "..."` means the call site no longer says what gets printed — not even whether it is an error or a success. Write the message where it is emitted. Reach for a constant only when the same text is genuinely emitted from several places, or when it is data rather than prose (a usage string, a template a caller supplies).

- Use `{value!r}` where quoting matters, so a typo like `'claud'` reads as a value rather than as prose.
- Keep any `[*] [+] [-] [!]` tag literally in the f-string, so a reader sees the severity without following a name.
- `%`-formatting and `.format()` are fine in code that already uses them consistently — match the file rather than mixing styles.

**Python — `print`, not `sys.stdout.write`.** `print` handles the newline, reads as intent, and goes to stderr just as easily: `print(msg, file=sys.stderr)`. Writing to the stream directly only earns its keep when you need byte-exact control — a partial line, a progress display overwriting itself with `\r`, or binary output. Emitting whole lines is not that, so reach for `print` by default and don't hand-manage `\n`.

**Python — note on the layout rule.** Aligning `=` deliberately conflicts with PEP 8's E221 ("multiple spaces before operator"). Configure the linter or formatter to allow it rather than reformatting against it, and say so if a project's autoformatter makes that impossible.

**C** — no conventions set yet beyond the general rules.

**Bash** — no conventions set yet beyond the general rules.

**Rust** — no conventions set yet beyond the general rules.

## Saving a memory — decide global first, and default to global

Some agents keep a per-session or per-project memory (Claude Code writes one under `~/.claude/projects/<project>/memory/`). **That memory does not travel.** It is one directory on one machine, so a preference saved there reaches whichever session happens to be running in that project, on that machine, and nothing else. These rules travel: they assemble into every agent's rules file on every machine that runs `ai-rules apply`.

So before saving anything to a memory, ask **"is this only true here?"** If it is not, it belongs in the rules — and most of the time it is not:

| The thing | Where |
|---|---|
| How I want work done, anywhere — cadence, style, what to check before committing | `ai/rules/misc.md` |
| Anything naming an employer, an internal host, a codename | the private layer |
| A fact about *this repo only* — a path, a quirk, a decision that dies with the project | a memory is fine |

**Never save to a memory because it is the quicker option.** Editing the repo means a commit; a memory is one file write. Taking the shortcut is how a standing instruction ends up applying on one machine while the others carry on doing the thing I asked to stop, with nothing anywhere saying why they differ. That has already happened: a rule about verification cadence lived only in one machine's project memory, and a session elsewhere found out about it by chance, from a daily note that mentioned it in passing.

**If a memory already holds something that should be global, move it** — put it in the right module, run `ai-rules apply`, and delete the memory file and its `MEMORY.md` line. Two copies is worse than either one, because they drift and nothing reconciles them.

## Verification cadence — batch it at the boundaries

Run the full test suite and any mutation sweep **at a commit boundary or before a big feature**, not after every exchange. While iterating, run only the test file covering what changed.

- **Never re-run against a tree that has not changed.** A fast-forward merge produces byte-identical content; verifying the result means checking which files are present, not running the suite again.
- **Scope a sweep to the affected test file** where that is enough. A sweep is N full suite runs, so scoping it is the difference between seconds and half an hour.
- **Say when a suite is slow and why**, and offer to make it cheaper, rather than absorbing the cost silently on every run.

**Why:** a conflict-free commit-and-merge once took ten minutes, roughly seven and a half of it two full suite runs where the second tested identical bytes. The sweeps do find real defects and are worth running — just not on every turn.

**How to apply:** during iteration, the one relevant test file. Before committing, the suite once and a sweep once. If most of a suite's time is subprocess spawning, name that as the reason rather than treating it as fixed cost.

## Commit review gating

Before making any git commit, show me the diff and the proposed commit message, and wait for explicit approval. Even if I have asked you to commit, do not run `git commit` until I review.

**Workflow:**

1. Make the requested changes (file edits, etc.).
2. Stage what should be committed: `git add <files>`.
3. Show me `git status` and `git diff --staged`, plus the proposed commit message.
4. Wait for me to say "go ahead" / "yes" / "commit it" or to give feedback.
5. Only then run `git commit`.

This applies to every commit, even if I authorized commits at the start of the work. It does not apply to non-commit git operations (status, diff, log, show) or to file edits, which you should proceed with normally. It does not apply to revertible scratch state like stashing.

**Why:** Catching issues before they land in history — wrong files staged, sensitive content, a commit message that does not match what changed, a commit that should have been split or squashed. Once a commit is made (especially if pushed), fixing it requires history rewrites, which are noisy and sometimes destructive.

**How to apply:** Treat "commit this" or "let's commit" as authorization to *prepare* a commit. Show the staged diff and proposed message, then wait. If I approve, commit. If I ask for changes, adjust and re-show. If I am clearly mid-flow and would obviously want a single commit at the end (e.g. you finished a multi-step refactor I scoped), still pause for review at the commit boundary.

## Unauthenticated MCP servers — tell me to re-auth, don't quietly work around it

**Any time a task could be helped by an MCP server that is unauthenticated, disconnected, or missing its
tools, say so immediately and ask me to re-auth it.** Do not silently fall back to a worse method, and do
not simply report the capability as unavailable and stop.

This applies whenever the server *could* help — not only when it is strictly required. If an MCP server
would let you check a job, query a database, read a bug, fetch a page, or verify a claim directly, and it
is not currently usable, tell me before proceeding by other means.

Say which server it is, what you would do with it, and how I re-auth (`/mcp` in an interactive session,
`claude mcp`, or claude.ai connector settings for claude.ai connectors). Then either wait, or continue with
the degraded approach **while clearly flagging what you could not verify** — never let the gap go unmentioned.

**Why:** re-auth takes me seconds, and without it work silently degrades — hand-run commands instead of
tool calls, guesses instead of verified facts, or a step that stalls entirely. I would rather spend ten
seconds re-authenticating than get an unverified answer or discover later that something was blocked.

**How to apply:** when a tool you want is unavailable, surface it in that turn as a concrete request
("re-auth `<server>` and I can do X directly"), not as a footnote or an apology at the end. If several are
unavailable, list them together so I can fix them in one pass.

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

## Links — always full raw URLs, never inline/masked

Always show links as the **full raw URL**, starting with `https://` (or `http://`) — visible, copyable, complete to where it goes. **Never** a markdown-masked inline link like `[text](url)`, and never a bare ID.

- YES: `job: https://ci.example.com/showjob.php?job=12345`
- NO: `[12345](https://ci.example.com/showjob.php?job=12345)` or bare `job 12345`

**Why:** markdown link syntax doesn't render in most places I paste into (bug trackers, Slack, email, plain text), and I want to see and copy the actual destination, not a masked link. Reinforces "make links clickable and durable — full URLs, not bare IDs."

**How to apply:** in ALL output — your replies to me and anything I'll send (bug descriptions/comments, Slack, email, MRs) — write the full URL, never a masked `[text](url)` and never a bare ID. This overrides the harness default of formatting links as markdown.

## Handling bugs — division of labor (I prep and file, you send as yourself)

Any time we work a bug — triaging, root-causing, drafting, filing or updating it, or replying on one — the split is: **I do the prep up to the send boundary; you send anything that goes out as you.**

- **I do:** the triage and root-cause, draft the description and any comments, file or update the bug, set the reviewer/approver list, and the bookkeeping that is not addressed to a person.
- **You do:** review and approve, and **post the @-mentions and send anything that goes out as you** — the comment that @-mentions the owner, the chat ping, the email. You always send your own @-mentions.

**Why:** you want the final say and to send in your own name and voice; I move the work forward right up to "ready to send" so all that is left is you posting it.

**How to apply:** default to preparing everything to the point of *ready to send*, show you the draft, and wait for you to post or @-mention. Pairs with "Drafting comments and messages in my voice" and "Bug root-cause & evidence."

**Bug titles / synopses:** lead with **1–3 short `[Tag]` prefixes** for triage and search — area or component, plus the chip, branch, or config — then a **readable plain-English** description of the real error being fixed (a fail signature or error message is fine). The brackets categorize; the English explains. NO failure-rate numbers ("100%"), NO file names, NO `file:line`, NO code — that is all body-only. Don't let the whole title collapse into bracketed jargon, and don't drop the tags either.

**Reviewers / approvers:** cap at **2 people initially (3 including me)**, and **confirm each is the actual owner** — through authorship on the broken line, an OWNERS file, or the bug they came from — before adding anyone. Don't pad the list.

## Where to put files you create — never in `~`

**Never create files directly in my home directory (`~`).** It is not a dumping ground; anything left there is clutter I have to find and clean up later.

Pick the destination by what the file is for:

- **Temporary / working files** (intermediate output, throwaway scripts, scratch data, downloaded logs) → the session scratchpad directory. Never `~`, never `/tmp` unless I ask.
- **Deliverables and anything I might open, keep, or share** (reports, generated HTML/PDF, diagrams, exported tables, one-off documents) → **`~/Documents/`**, unless I named a path.
- **Project files** → inside that project's repo/working directory, in the directory the project's conventions imply.
- If a file belongs to an established location I already use (e.g. daily notes, a repo's `docs/`), put it there rather than inventing a new spot.

**Why:** files dropped in `~` get lost among dotfiles and system directories, are easy to forget, and clutter the one directory I look at most. `~/Documents/` is where I actually look for documents, and the scratchpad keeps disposable work out of the way entirely.

**How to apply:** before writing a file, ask "is this disposable or is it a deliverable?" Disposable → scratchpad. Deliverable → `~/Documents/` (or the project). If neither fits and you're unsure where it belongs, ask me instead of defaulting to `~`. When you do create a deliverable, tell me the full path.
