# GitHub setup verification

Audit date: 2026-10-22. Base main has 10 historical commits / 8 Markdown files, no application tests, workflows or protection. All five accounts verified: caferkilinc Admin; ismail-cevik, cakarburkayy, tahaugurtoyran, Yaman-A-E Write. No permission elevation is required or performed.

| Operation | Status | Evidence / limitation |
|---|---|---|
| 6 work-package trackers + 31 technical tasks | COMPLETED AND VERIFIED | Existing issues #1–#37; owners assigned, acceptance and prerequisite links in bodies |
| Repository history | COMPLETED AND VERIFIED | New commit descends from audited main; original files/history preserved |
| Governance files and workflow definitions | PREPARED | Configuration PR; main unchanged until approved merge |
| Unit gate scenarios | COMPLETED AND VERIFIED locally | 27 positive/negative tests; see CI for hosted execution |
| Backend/frontend application checks | NOT STARTED | No app packages/lockfiles/test commands in audited base; #10 owns this |
| Trusted base dependency-gate | PREPARED | Becomes available after reviewed merge, then validate with real canary PR |
| Main branch protection | REQUIRES USER ACTION | Proposed JSON only; explicit owner approval and live checks needed |
| Actual product / scientific experiments | NOT STARTED | Governance task counts/tests do not establish product/research success |

## Activation after independent review

1. Inspect the configuration PR and its real CI results; Burkay/İsmail provide independent review.
2. Owner explicitly approves merge. This setup does not merge its own PR.
3. After merge, open a numbered canary PR for an existing legitimate task and verify trusted-base dependency gate success/failure, stale review, failed CI and reevaluation. Do not close fake prerequisites.
4. After successful live checks and explicit owner approval, apply `.github/branch-protection.proposed.json` through Settings → Branches → main, or `gh api --method PUT repos/caferkilinc/refactoring-ai-generated-code/branches/main/protection --input .github/branch-protection.proposed.json` from a locally authorized owner session. The setup does not execute this command.
5. Enable real app checks only when #10 provides reproducible packages and commands; add their proven check names to required checks through review.

No sensitive DOCX, API key, private upload, paid API call, direct main write, force push or automatic merge is part of this setup.

## Verified hosted evidence (bootstrap revision)

- Configuration PR: https://github.com/caferkilinc/refactoring-ai-generated-code/pull/38 ; independent review requested from @cakarburkayy. PR remains open/unmerged.
- Hosted governance CI: https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39774599017 — governance-tests, documentation-checks, security-checks succeeded on the first bootstrap revision.
- Native graph sync: https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39774558427 — succeeded; all 31 parent links and every declared dependency were subsequently checked through GitHub API. No task was closed.
- Project: https://github.com/users/caferkilinc/projects/1 ; reuses the existing project, no duplicate board.

The next revision adds a read-only live gate preview for PR #38 and pins checkout v6 to its verified immutable commit. This preview does not activate trusted-main merge enforcement.

Latest verified revision `ccf9673c97aa704cd88eb893f43a2d42fa2cf319`:
- https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39775623542 : all four jobs succeeded, including the read-only live `dependency-gate-preview` for real PR #38. The preview reported F01-GOV with zero mandatory prerequisites.
- 25 governance unit tests passed on the GitHub-hosted runner, including closed-only rejection, completed dependency reevaluation, API failure, stale/self review, failed/missing CI, cycles, P0/P1 separation, path scope, and restricted policy maintenance.
- https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39775630711 : pull-request CI succeeded. The preview job is intentionally skipped on PR events; the real trusted-base gate remains pending bootstrap merge.
- All 31 task-to-parent links and 53 prerequisite edges match the canonical registry.

## Project views and data

Task Table, Development Board, Roadmap and Bug Tracking are created; Status has Backlog, Ready, In Progress, Blocked, In Review, Testing and Done in that order. Estimated Effort (Number), Start Date (Date) and Target Date (Date) exist, and all 31 technical tasks were populated and verified by reading their actual cells. Roadmap was created and its date-field mapping prepared; persistence is checked separately below. #1 is In Review, #8 In Progress, #19/#25 Blocked for resources; other planned tasks remain Backlog. No task is Done.

Plan ID is in the task title, owner is the native Assignee, P0/P1/work package/phase/module are issue labels, prerequisites are native dependency links, and each issue body records supporting developer, independent reviewer, acceptance and contracts. These data are not duplicated into inconsistent standalone tasks.

Bug Tracking uses the same project issue set filtered by `label:type:bug`; no fake bug issue is created. The first iteration view uses the F00/F01/F02 task labels (Oct 21–Nov 1 planning block). Native date fields and issue bodies retain the exact task windows. Future weekly iterations can be added after the team declares capacity.
