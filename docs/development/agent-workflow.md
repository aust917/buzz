# Working with coding agents

This guide describes the fork's collaboration conventions. Read it when planning
multi-step work, handing a task to another agent, or changing agent instructions.
Routine fixes need only the applicable instructions and the relevant code.

## Load context as needed

[AGENTS.md](../../AGENTS.md) is the shared source of repository instructions.
Keep its entry point below 6 KB and scoped `AGENTS.md` files below 4 KB.
These are repository budgets, not model context limits. Add local instructions
only where a directory has different commands, constraints, or recurring traps.
Keep detailed architecture and procedures in linked reference documents.

Start with the task's paths, then open the relevant reference and implementation.
Search by symbol or directory before widening the search. Do not load the whole
documentation tree, lockfiles, translations, fixtures, or submodules for orientation.
Broaden the search when the initial path does not explain the behavior.

Instruction discovery depends on the client and its working directory. A Codex
session started at the repository root does not automatically load every nested
instruction file. Before editing a path, read the `AGENTS.md` files along its
directory chain; local instructions supplement the root's shared conventions.

## Keep client adapters thin

Each `CLAUDE.md` adapter contains exactly one line:

```text
@AGENTS.md
```

Put an adapter beside each shared instruction file that Claude needs. The import
resolves relative to the adapter. Do not import reference guides: imports load
their content immediately and defeat selective reading.

Keep `.github/copilot-instructions.md` as a small pointer to the root instructions
and applicable scoped files. Do not maintain another copy of project rules.
Support for pointers, imports, and nested instructions varies between Copilot
clients. Check the client's loaded instructions when onboarding or troubleshooting;
do not assume that the presence of an adapter proves the rules were loaded.

## Define bounded work

For a small fix, the request and a brief completion report are enough. For a task
that spans sessions or several components, save a concise task brief or plan with:

- Goal and observable acceptance criteria.
- Relevant paths and the boundaries affected by the change.
- A short sequence of steps and the checks that demonstrate completion.
- Material decisions, remaining work, and a handoff when work continues elsewhere.

Update the plan when evidence changes the approach. Record completed checks with
their actual outcome and distinguish unavailable checks from passing checks.
Avoid creating an invented product roadmap or mandatory planning files for every fix.

## Coordinate parallel work

Give each agent a bounded question or explicit file ownership. Read-only research
can run in parallel with implementation. Agents sharing a checkout must coordinate
edits to shared files; do not overwrite another agent's changes.
Use separate Git worktrees when implementation branches need independent changes
or checks. A worktree isolates files, not every external resource: coordinate ports,
model caches, native builds, and shared application settings as needed.
Before integration, review the combined diff and run the relevant checks against
the integrated result. Handoffs should name changed paths, decisions, check results,
and unresolved issues so the next agent does not repeat discovery.

## Preserve useful knowledge

Put stable directory rules in the nearest `AGENTS.md`; put detailed explanations
in the reference document that owns the topic. Update the same source when code
changes invalidate it. Add a durable note when it prevents repeated mistakes.
Keep temporary command output, transcripts, personal preferences, and session logs
out of shared instructions. Summarize only decisions and evidence needed to resume
unfinished work. Do not turn completed task history into required startup context.

## Verify the instructions

Run the lightweight [documentation check](../../scripts/check_agent_docs.py):

```sh
uv run --no-project --python 3.13 python scripts/check_agent_docs.py
```

The check catches structural drift such as broken local references, oversized
instructions, and adapter changes. It cannot prove that instructions are correct
or that a client loaded them. Check commands against their owning configuration
and code; verify application behavior with the appropriate tests.

## Sources

Official documentation reviewed on **2026-10-29**. Client behavior can change;
recheck these sources when changing integration or instruction discovery.

- [OpenAI: AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [OpenAI: keeping skills and prompts focused](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [Anthropic: instruction loading and imports](https://code.claude.com/docs/en/memory)
- [Anthropic: Claude Code best practices](https://code.claude.com/docs/en/best-practices)
- [GitHub: repository instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions)
- [GitHub: Copilot CLI discovery and imports](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)
