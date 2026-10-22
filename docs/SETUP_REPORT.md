# GitHub setup verification

Audit date: 2026-10-22. Base main has 10 historical commits / 8 Markdown files, no application tests, workflows or protection. All five accounts verified: caferkilinc Admin; ismail-cevik, cakarburkayy, tahaugurtoyran, Yaman-A-E Write. No permission elevation is required or performed.

| Operation | Status | Evidence / limitation |
|---|---|---|
| 6 work-package trackers + 31 technical tasks | COMPLETED AND VERIFIED | Existing issues #1–#37; owners assigned, acceptance and prerequisite links in bodies |
| Repository history | COMPLETED AND VERIFIED | New commit descends from audited main; original files/history preserved |
| Governance files and workflow definitions | PREPARED | Configuration PR; main unchanged until approved merge |
| Unit gate scenarios | COMPLETED AND VERIFIED locally | 22 positive/negative tests; see CI for hosted execution |
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
