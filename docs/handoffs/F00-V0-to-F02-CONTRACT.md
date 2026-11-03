# Cafer → Alperen: F00-V0 accepted handoff / F02-CONTRACT preparation

Date: 2026-11-04 (Europe/Istanbul). This is preparation context, not permission
to implement the next task. Cafer selected Alperen / F02-CONTRACT #11 in this
chat after accepting the merged and verified F00-V0 result.

## Published predecessor evidence

- Source: `d923134da4f9f5a2ab55a5f51fbf9415ff717262`.
- [PR #45](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/45),
  merged at `fdd573286834fe15c1ac1c0d51db4ed9b0015db7`.
- [Source report](https://github.com/caferkilinc/refactoring-ai-generated-code/blob/d923134da4f9f5a2ab55a5f51fbf9415ff717262/report.md).
- [Actual delegated approval](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/45#issuecomment-6617013699),
  recognized only for that PR/revision through ADR 0006 / PR #46.
- [Dependency/readiness success](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41688380131/attempts/3).
- Main [pilot CI](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41731529368):
  ten real JUnit tests passed; original/test integrity preserved.
- Main [governance CI](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41731529429):
  111 tests and documentation/security checks passed; preview SKIPPED, not PASS.

Acceptance key: `F00-V0:d923134da4f9f5a2ab55a5f51fbf9415ff717262`.
Consume this key once only. New active owner/task: Yaman-A-E / F02-CONTRACT #11,
rotation index 2; conditional successor İsmail (@ismail-cevik). The current
Alperen task has not been executed or handed off, so handoff_confirmed=false.

V0 manifest SHA-256: `1650a915ea6516e52ac27c1a4c98a11d0ddd62155f41ec6a21835b0195311376`.
Test manifest SHA-256: `d5f17c053d0e9d6f0e7e6a7b2a51c8039edbb42d8a0b025a46a9193740b63028`.
Exact serving model ID/revision/settings remain UNKNOWN as disclosed in the
generation record. Dataset NOT_FROZEN, research NOT_RUN and release NOT_READY.
The Java pilot is not the whole application or a complete twelve-task study.

## Next task boundary

F02-CONTRACT / #11 supplies versioned CIR/LanguageAdapter/API schemas and
fixtures: Finding, Evidence, SourceLocation, capability/test contracts,
IssueSelection, ContextPackage and PatchCandidate; behavior_status and
quality_outcome remain distinct. Hard prerequisite is **only F00-PLAN #8**.
F00-V0 #9 is the predecessor handoff continuity record, not a new hard edge.
No environment/GPU/API dependency or scope promotion is introduced here.

Approved task areas: backend/core/schemas/, docs/contracts/, tests/contracts/,
.github/workflows/contract-checks.yml, and applicable continuity files under
trusted policy. Required declared checks: governance-tests, documentation-checks,
security-checks, contract-checks; evaluate additional checks from actual paths.
No schema/app code or contract-checks workflow is supplied by this handoff.

## Copyable startup prompt — preparation only

```text
PROJECT GENESIS v2.0 — CONTEXT RECOVERY / PREPARATION ONLY

Developer: Alperen Enes Yaman (@Yaman-A-E)
Assigned task: F02-CONTRACT / Issue #11
Canonical repository:
https://github.com/caferkilinc/refactoring-ai-generated-code.git
Integration branch: main

Determine the current canonical main SHA live. The pilot merge is
fdd573286834fe15c1ac1c0d51db4ed9b0015db7; the later accepted-handoff record
must be present on current main. Do not force main to an older SHA.

Inspect the actual OS, Git root, branch/HEAD, remotes/upstream, tracked and
untracked work, in-progress Git operations and linked worktrees. Prefer a
verified existing canonical repository. Use a full-history clone only when
needed into a safe empty location. Preserve all existing work. Fetch canonical
refs/tags; synchronize main by fast-forward only when safe, and preserve the
starting feature branch. No reset --hard, clean, force push, automatic stash,
feature-branch merge/rebase, dependency installation, tests or project scripts.

Read current AGENTS.md and the development-handoff procedure; task-plan.json,
acceptance.json, latest PROJECT_STATUS/report, approved TR/EN SRS v0.4,
architecture and task-relevant contracts/decisions. Inspect the actual #11
issue, its native #8 prerequisite, and #8 acceptance. Separately verify #9's
completed state, merged #45, exact d923134... source and accepted-handoff key
as continuity evidence. Do not add #9 as a dependency of #11.

Confirm active_owner=Yaman-A-E, active_task_plan_id=F02-CONTRACT,
rotation_index=2 and conditional next owner ismail-cevik on trusted main.
Verify canonical source identity; do not expose credentials or impersonate
another developer. Old fixed issue roles do not grant implementation authority.
If records differ, report the actual difference without rewriting them.

Preserve original Java V0/tests/manifests. All seven languages and real local
Falcon-Mamba remain mandatory P0; approved requirements are not implemented
features. Report unavailable private architecture PDFs honestly. Inspect
existing contracts and equivalent open PRs rather than assuming they exist.

Return a Turkish synchronization/context report with actual SHAs, paths,
branch/worktree state, current ownership/prerequisite evidence, inspected files,
real CI, limitations and READY_FOR_TASK_CONTRACT or BLOCKED. Then STOP.
Do not write code, create a development branch, commit/push, invoke models,
install tools, accept another task or advance rotation. Await the separate
bounded F02-CONTRACT execution contract.
```

The containing handoff publication SHA is supplied after publication in the
final receipt. This file does not contain its own fabricated commit SHA.
