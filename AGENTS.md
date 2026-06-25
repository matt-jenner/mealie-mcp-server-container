# Agent Workflow

This project uses feature specs in `spec/` and project-local OpenCode subagents in `.opencode/agent/`.

## Roles

- The primary assistant acts as orchestrator.
- `story-implementer` implements one assigned story at a time.
- `story-reviewer` reviews one completed story against its acceptance criteria.
- `feature-reviewer` reviews a full feature after all stories are implemented.
- `spec-maintainer` updates spec status sections only after the orchestrator decides what changed.
- `test-runner` runs requested validation commands and reports results without editing files.

## Spec Structure

Each feature spec lives at `spec/<order>-<feature>.md`.

Each spec should include:

- `Goal`: what the feature achieves.
- `Status`: current implementation and review state.
- `Context`: relevant design background.
- `Stories`: independently deliverable slices with acceptance criteria.
- `Implementation Notes`: constraints and preferred approach.
- `Test Strategy`: expected validation.

## Status Rules

Use these states in `## Status`:

- `Not Started`: no implementation work has begun.
- `In Progress`: at least one story is being implemented or reviewed.
- `Implemented`: all stories are implemented but feature review is not complete.
- `Complete`: implementation, review, and required verification are complete.
- `Blocked`: work cannot continue without a decision or external dependency.

Story checkboxes mean:

- Unchecked: story is not completed.
- Checked: story implementation passed review or the orchestrator explicitly accepted it.

Review checkboxes mean:

- `Implementation reviewed against acceptance criteria`: review agent or orchestrator completed acceptance review.
- `Tests verified`: required tests/checks were run or a documented reason exists for not running them.

Do not mark stories or reviews complete based only on intent.

## Orchestration Process

For each feature:

1. The orchestrator reads the feature spec and identifies stories that can be worked safely.
2. The orchestrator assigns scoped work to one `story-implementer` per story when parallel work is safe.
3. Shared-file or high-conflict work is serialized.
4. Each implementation agent reports files changed, criteria satisfied, tests run, and blockers.
5. The orchestrator inspects the combined changes.
6. A separate `story-reviewer` checks each completed story against the spec.
7. After all stories pass, `feature-reviewer` checks the whole feature.
8. The orchestrator asks `spec-maintainer` to update status sections.
9. The orchestrator reports completion and residual risks to the user.

## Scope Rules

- Do not edit reference files in `../../3rdParty/mealie-mcp-server` unless the user explicitly asks.
- Do not commit, amend, or push unless the user explicitly asks.
- Do not add secrets to committed files.
- Keep changes minimal and focused on the current spec story.
- Preserve unrelated user or agent changes.

## Review Standard

Review findings should prioritize:

- Missing acceptance criteria.
- Bugs or behavioral regressions.
- Security risks.
- Missing or weak tests.
- Documentation inaccuracies.
- Scope creep.

If no findings are discovered, say so and list residual risks or unverified behavior.

## Typical Orchestrator Prompt

Use this shape when starting a feature:

```text
Start Feature 02 using the orchestrated agent workflow. Use separate implementation agents where safe, then use separate review agents against the spec. Update the spec status when complete, but do not commit.
```

Use this shape when starting a single story:

```text
Implement Story 04.1 using story-implementer, then review it with story-reviewer. Update the spec status only if review passes. Do not commit.
```
