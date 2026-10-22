# GitHub ekip altyapısı teslim ve doğrulama raporu / Setup verification

22 Ekim 2026 / 22 October 2026. Repository: [caferkilinc/refactoring-ai-generated-code](https://github.com/caferkilinc/refactoring-ai-generated-code). [Project](https://github.com/users/caferkilinc/projects/1). [Configuration PR #38](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/38).

Kurulum dosyaları inceleme branch’inde hazırlanmıştır; PR açık ve merge edilmemiştir. Yönetim altyapısı testleri çalışan bir ürün veya tamamlanmış araştırma deneyi anlamına gelmez. (Configuration is prepared on the review branch; the PR remains open and unmerged. Governance tests do not establish product or research success.)

## 1. Repository audit

`main` audit baseline: `7e068040c3a4fb1a2f32783a4c592dc974324f36`, ten September commits and eight Markdown files. Existing history is preserved. No executable application packages/tests or measured refactoring experiments exist in that base. Live repository visibility remains public and auto-merge is disabled. No direct main write, force push, history rewrite, paid service, private DOCX publication or permission change was performed in this completion pass.

| Operation | Status | Verified result / limitation |
|---|---|---|
| Repository access | COMPLETED AND VERIFIED | Cafer Admin; four collaborators Write, rechecked on 22 October |
| Six work-package trackers and 31 technical tasks | COMPLETED AND VERIFIED | All 37 issues fetched live; all open and assigned; no duplicate issue created |
| Task owner/support/reviewer/priority/date consistency | COMPLETED AND VERIFIED | All 31 live task bodies and assignees match `.github/task-plan.json`; six tracker assignees match |
| Native issue hierarchy and prerequisites | COMPLETED AND VERIFIED | Earlier hosted sync and API verification established 31 parent links / 53 edges; registry preserved in this pass |
| Five Project views and schedule | COMPLETED AND VERIFIED | Table, Board, Roadmap, Bug Tracking, Iteration / Sprint; saved shared defaults |
| Board acceptance automation | COMPLETED AND VERIFIED | Closure and merge → Testing; Auto-close issue is Off; Done requires reviewed acceptance |
| Private Project team access | REQUIRES USER ACTION | Only caferkilinc has Project Admin; four Project Write invitations require explicit owner approval |
| Governance tests and hosted CI | COMPLETED AND VERIFIED | 27 unit tests; documentation and hygiene checks pass; actual hosted evidence below |
| Configuration files | PREPARED | 32 changed files in PR #38; main unchanged pending independent review and explicit merge approval |
| Independent PR approval | REQUIRES USER ACTION | Burkay requested; zero submitted reviews when checked |
| Trusted-main dependency gate | PREPARED | Read-only live preview passed; real base-triggered enforcement awaits bootstrap merge and canary checks |
| Main branch protection / rulesets | REQUIRES USER ACTION | No classic branch protection or ruleset currently exists; explicit owner approval and live gate checks required |
| Application backend/frontend checks | NOT STARTED | Task #10 must supply real packages, lockfiles and commands first |
| Product implementation / scientific experiments | NOT STARTED | No implementation or numerical research success is claimed |

## 2. Project views, fields and automation

[Open Project](https://github.com/users/caferkilinc/projects/1). The same issue set feeds all views; trackers remain native parents rather than duplicated development work. Status order: Backlog → Ready → In Progress → Blocked → In Review → Testing → Done.

| View | Saved configuration |
|---|---|
| Task Table | `-label:type:epic`, 31 tasks; Assignee, Status, Linked PR, Estimated Effort, Start Date, Target Date, Labels |
| Development Board | `-label:type:epic`, same 31 tasks grouped by seven Status values |
| Roadmap | Start = Start Date; end = Target Date; technical-task filter; both fields verified selected after reload |
| Bug Tracking | `label:type:bug`; currently zero bugs, no fake issue created |
| Iteration / Sprint | `label:phase:F00,phase:F01,phase:F02`, six tasks for the initial 21 October–1 November planning block |

Estimated Effort is a Number; Start Date and Target Date are Date fields. All 31 task values were populated and checked earlier. Plan ID is in the title; owner is native Assignee; work package, phase, module and P0/P1 are labels; support/reviewer/contracts/acceptance are in the issue body; prerequisites are native issue dependencies. PR #38 is linked in issue #1’s body, without an automatic closing directive. No separate Reviewer/Plan ID/Dependency custom-field duplication or native recurring Iteration field is claimed.

Final verification corrected two inherited Done shortcuts: Item closed and Pull request merged now set Testing. Auto-close issue from Done is disabled. The built-in automations route work; they do not semantically verify acceptance. A maintainer must review the acceptance record and live evidence before setting Done. Six Project workflows remain enabled. Project description/README links the plan, workload, guide, PR and final deadline.

Project is private and currently lists only caferkilinc (Admin). Repository Write does not grant Project access. After explicit owner approval, invite `ismail-cevik`, `cakarburkayy`, `tahaugurtoyran`, `Yaman-A-E` with Project Write via Project → Settings → Manage access. No invitation or visibility change has been made.

## 3. Research work packages

| Package | Owner | Tracker | Phases |
|---|---|---|---|
| İP1 — Deney temeli ve platform sözleşmeleri | @caferkilinc | [#2](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/2) | F00–F03 |
| İP2 — Dil çekirdeği ve başlangıç kalite/davranış ölçümü | @cakarburkayy | [#3](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/3) | F04–F06 |
| İP3 — Güvenlik inceleme hattı ve Local AI | @Yaman-A-E | [#4](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/4) | F07A/F07B |
| İP4 — İlk onay ve bağımlılığa duyarlı paralel refactoring | @Yaman-A-E | [#5](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/5) | F08–F10 |
| İP5 — Kanıta dayalı doğrulama ve nihai sürüm | @ismail-cevik | [#6](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/6) | F11–F13 |
| İP6 — Çok dilli genişleme ve deneysel değerlendirme | @tahaugurtoyran | [#7](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/7) | F14–F15 |

## 4. All technical tasks and dependency graph

The following is the exact mandatory integration graph. Independent topic-branch work may proceed with approved contracts/fixtures; dependencies gate integration. F07B / Local AI is P1 and never blocks Java P0. Contract Ready and Integration Ready tasks are distinct. Full technical deliverables, normal/error cases, allowed paths and applicable checks remain in the canonical registry and live issue bodies.

| Issue / Plan ID | Primary; support; independent reviewer | Priority | Start → target | Effort range | Prerequisites |
|---|---|---|---|---|---|
| [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) `F00-PLAN` | @caferkilinc; @cakarburkayy; @ismail-cevik | P0 | 2026-10-21 → 2026-10-25 | 6–10 h | None |
| [#9](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/9) `F00-V0` | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-10-26 → 2026-11-01 | 12–18 h | [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) |
| [#1](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/1) `F01-GOV` | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-10-21 → 2026-10-25 | 8–12 h | None |
| [#10](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/10) `F01-ENV` | @ismail-cevik; @caferkilinc; @cakarburkayy | P0 | 2026-10-26 → 2026-11-01 | 12–18 h | [#1](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/1) |
| [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) `F02-CONTRACT` | @caferkilinc; @cakarburkayy; @ismail-cevik | P0 | 2026-10-21 → 2026-10-25 | 10–16 h | [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) |
| [#12](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/12) `F02-STATE` | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-10-26 → 2026-11-01 | 12–18 h | [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11), [#10](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/10) |
| [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13) `F03-INPUT` | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-11-02 → 2026-11-08 | 14–22 h | [#12](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/12) |
| [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) `F04-JAVA` | @cakarburkayy; @Yaman-A-E; @ismail-cevik | P0 | 2026-11-02 → 2026-11-08 | 16–24 h | [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11), [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13) |
| [#15](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/15) `F05-QUALITY` | @cakarburkayy; @caferkilinc; @ismail-cevik | P0 | 2026-11-09 → 2026-11-15 | 16–24 h | [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) |
| [#16](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/16) `F06-SANDBOX` | @ismail-cevik; @caferkilinc; @cakarburkayy | P0 | 2026-11-02 → 2026-11-08 | 18–26 h | [#10](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/10), [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13) |
| [#17](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/17) `F06-TESTS` | @ismail-cevik; @caferkilinc; @cakarburkayy | P0 | 2026-11-09 → 2026-11-15 | 12–18 h | [#9](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/9), [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14), [#16](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/16) |
| [#18](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/18) `F07A-SCAN` | @cakarburkayy; @ismail-cevik; @caferkilinc | P0 | 2026-11-16 → 2026-11-22 | 14–22 h | [#15](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/15), [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13) |
| [#19](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/19) `F07B-PILOT` | @Yaman-A-E; @ismail-cevik; @cakarburkayy | P1 | 2026-10-26 → 2026-11-01 | 6–10 h | [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) |
| [#20](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/20) `F07B-LOCAL` | @Yaman-A-E; @cakarburkayy; @ismail-cevik | P1 | 2026-12-07 → 2026-12-13 | 14–20 h | [#19](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/19), [#18](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/18) |
| [#21](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/21) `F08-UI` | @tahaugurtoyran; @caferkilinc; @cakarburkayy | P0 | 2026-11-02 → 2026-11-15 | 16–24 h | [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) |
| [#22](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/22) `F08-INTEGRATE` | @tahaugurtoyran; @caferkilinc; @ismail-cevik | P0 | 2026-11-16 → 2026-11-22 | 8–12 h | [#21](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/21), [#15](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/15), [#17](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/17), [#18](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/18) |
| [#23](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/23) `F09-CONTEXT` | @Yaman-A-E; @cakarburkayy; @caferkilinc | P0 | 2026-11-09 → 2026-11-15 | 18–26 h | [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11), [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) |
| [#24](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/24) `F09-SCHED` | @Yaman-A-E; @cakarburkayy; @ismail-cevik | P0 | 2026-11-16 → 2026-11-22 | 10–16 h | [#23](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/23) |
| [#25](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/25) `F10-PATCH` | @Yaman-A-E; @caferkilinc; @ismail-cevik | P0 | 2026-11-23 → 2026-11-29 | 18–26 h | [#13](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/13), [#22](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/22), [#24](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/24) |
| [#26](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/26) `F11-VALIDATE` | @ismail-cevik; @cakarburkayy; @caferkilinc | P0 | 2026-11-30 → 2026-12-06 | 18–26 h | [#17](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/17), [#25](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/25), [#18](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/18) |
| [#27](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/27) `F11-RETRY` | @Yaman-A-E; @ismail-cevik; @cakarburkayy | P0 | 2026-11-30 → 2026-12-06 | 6–10 h | [#26](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/26) |
| [#28](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/28) `F12-REVIEW` | @tahaugurtoyran; @ismail-cevik; @cakarburkayy | P0 | 2026-11-16 → 2026-11-29 | 12–18 h | [#21](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/21), [#11](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/11) |
| [#29](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/29) `F12-FINAL` | @caferkilinc; @ismail-cevik; @cakarburkayy | P0 | 2026-12-01 → 2026-12-06 | 14–22 h | [#26](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/26), [#27](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/27), [#28](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/28) |
| [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30) `F13-BASIC` | @tahaugurtoyran; @cakarburkayy; @caferkilinc | P0 | 2026-11-30 → 2026-12-06 | 10–16 h | [#29](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/29), [#15](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/15) |
| [#31](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/31) `F13-ADV` | @tahaugurtoyran; @caferkilinc; @ismail-cevik | P1 | 2026-12-07 → 2026-12-13 | 10–16 h | [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30) |
| [#32](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/32) `F14-PY` | @cakarburkayy; @ismail-cevik; @caferkilinc | P1 | 2026-12-07 → 2026-12-13 | 14–22 h | [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30), [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) |
| [#33](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/33) `F14-JSTS` | @cakarburkayy; @Yaman-A-E; @ismail-cevik | P1 | 2026-12-14 → 2026-12-20 | 18–26 h | [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30), [#14](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/14) |
| [#34](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/34) `F14-MIX` | @tahaugurtoyran; @cakarburkayy; @ismail-cevik | P1 | 2026-12-18 → 2026-12-20 | 6–10 h | [#32](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/32), [#33](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/33) |
| [#35](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/35) `F15-P0` | @ismail-cevik; @tahaugurtoyran; @caferkilinc | P0 | 2026-12-07 → 2026-12-13 | 16–24 h | [#30](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/30) |
| [#36](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/36) `F15-EXPERIMENT` | @caferkilinc; @Yaman-A-E; @ismail-cevik | P0 | 2026-12-14 → 2026-12-20 | 18–26 h | [#35](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/35), [#8](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/8) |
| [#37](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/37) `F15-HANDIN` | @tahaugurtoyran; @caferkilinc; @ismail-cevik | P0 | 2026-12-21 → 2026-12-27 | 10–16 h | [#35](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/35), [#36](https://github.com/caferkilinc/refactoring-ai-generated-code/issues/36) |

Native sync evidence: [successful run](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39774558427). The previous API verification matched all 31 parents and 53 prerequisite edges. The graph has no cycle and no transitive Local AI blocker on a P0 task; these invariants also pass unit tests. No task has been closed to manufacture acceptance.

## 5. Team workload

| Account | Primary task count | Primary allocation | Support allocation | Combined estimate | Review assignments |
|---|---:|---:|---:|---:|---:|
| @caferkilinc | 8 | 83.3 h | 45.0 h | 128.3 h | 6 |
| @ismail-cevik | 5 | 65.8 h | 42.9 h | 108.7 h | 13 |
| @Yaman-A-E | 6 | 63.0 h | 19.2 h | 82.2 h | 0 |
| @tahaugurtoyran | 7 | 64.4 h | 6.0 h | 70.4 h | 0 |
| @cakarburkayy | 5 | 68.6 h | 34.8 h | 103.4 h | 12 |

Estimates distribute task midpoint effort 70% primary / 30% support over calendar days. They are planning assumptions, not measured working hours or equal weekly commitments. Reviewer/coordination time is additional, including interface feedback from Taha and Alperen. Epics add zero duplicated effort. See [weekly table](TEAM_WORKLOAD.md) and regenerate using `python3 scripts/governance/workload.py` after reviewed plan changes. Capacity peaks of approximately 19–26 estimated hours require weekly agreement; share work or defer independent/P1 work if unavailable. Critical dependent targets must move when prerequisite acceptance slips.

## 6. P0 / P1 roadmap and first sprint

| Date / window | Target |
|---|---|
| 21 October–1 November | Scope/evidence protocol, governance, API/CIR/LanguageAdapter contracts, pilot, reproducible environment |
| 2–15 November | Safe input/V0, Java adapter, real quality and sandbox/baseline, independent UI/context development |
| 16–29 November | Deterministic security, first approval integration, conflict scheduling, real provider patches |
| 30 November–13 December | Candidate/retry/combined validation, basic report, tested P0 E2E |
| 13 December 2026 | P0 acceptance target |
| 20 December 2026 | P1 cutoff; resource-permitting Local AI, extra languages and advanced reporting |
| 14–20 December | Frozen experiments, failure-inclusive analysis, explicit limitations |
| 27 December 2026 | Reproducible package and academic delivery preparation target |
| 28–31 December 2026 | Fix/regression reserve; no new planned features |
| 1 January 2027 | Final course delivery; no invented submission hour |

First actionable assignments: Cafer completes scope/resource decisions in #8 and presents #38 for review; Burkay reviews #38 and co-designs #11 adapter/CIR contracts; İsmail reviews scope/contracts and prepares #10 reproducibility/QA requirements; Alperen checks #19 GPU/runtime evidence and #25 provider access without paid calls; Taha checks approval/API consumption and prepares #21 mock fixtures. #11 integration follows accepted #8; #10 integration follows accepted #1. Do not mark mocks, a task description or a review request as completed implementation.

## 7. Branch protection and review

On 22 October the GitHub Branches page listed no classic protection and Rulesets explicitly said none exists. Therefore **GitHub is not currently enforcing the proposed merge restrictions**. The contribution guide is currently procedural. The [proposed protection JSON](../.github/branch-protection.proposed.json) specifies a PR, one code-owner approval, stale approval dismissal, successful current checks, resolved conversations, admin enforcement and no force-push/deletion. It is a proposal, not an active policy.

PR #38: primary @caferkilinc, support @ismail-cevik, independent reviewer @cakarburkayy. Zero submitted reviews were found. Neither author nor primary/support may supply independent acceptance. CODEOWNERS includes valid Write/Admin accounts and independent alternatives; it awaits merge to the default branch. Review/merge approval must precede bootstrap activation; this report does not approve or merge its own PR.

## 8. GitHub Actions and actual validation

| Check / scenario | Result and scope |
|---|---|
| 27 governance unit tests | COMPLETED AND VERIFIED locally and in hosted Actions; isolated API fixtures |
| documentation-checks | COMPLETED AND VERIFIED; required documents and relative links |
| security-checks | COMPLETED AND VERIFIED; deterministic repository hygiene only, not a complete vulnerability scanner |
| Real bootstrap PR preview | COMPLETED AND VERIFIED in an earlier hosted push run: F01-GOV, zero mandatory prerequisites |
| Missing prerequisite / closed-only evidence | Unit rejection passes |
| Independent branch development / accepted dependency reevaluation | Unit positive cases pass; documented rerun procedure |
| Failed/missing CI and stale/self/primary/support review | Unit rejection passes |
| P0 independent of Local AI; branch/Plan ID/path traceability; cycle/API failure | Unit cases pass |
| Actual required-check merge blocking on main | PREPARED; not activated or live validated |
| Backend/frontend execution | NOT STARTED; no real app checks claimed before #10 |

Hosted evidence checked before the final documentation-only update:

- [CI run 39779470584](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39779470584) on `d5e3cce29cf7c14bc4de7d17e9bfda666af66b29`: governance-tests, documentation-checks, security-checks succeeded. Log confirms 27 tests. Preview is intentionally skipped for the PR event.
- [Earlier successful live preview](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/39775623542): read-only GitHub API inspection of actual PR #38. This does not demonstrate trusted-main enforcement.
- Latest report-only commit triggers fresh CI; inspect its result on PR #38 rather than treating these earlier SHAs as evidence for a newer revision.

The privileged-event gate checks out only trusted base SHA and runs with read-only contents/issues/PR/check permissions; it never executes untrusted PR code. Ordinary governance CI has read-only contents permission. Owner-only graph synchronization has issues write, refuses unexpected reparenting/deletion and is not an arbitrary issue writer. Checkout is pinned to an immutable commit. A closed prerequisite alone cannot pass: trusted acceptance, merged matching PR/head, independent current Write approval, successful applicable checks and evidence are required.

## 9. Changed files and team guide

PR #38 contains 32 changed paths:

```text
.github/CODEOWNERS
.github/ISSUE_TEMPLATE/{bug,config,research,task}.yml
.github/PULL_REQUEST_TEMPLATE.md
.github/{acceptance,branch-protection.proposed,task-plan}.json
.github/workflows/{dependency-gate,governance-ci,issue-graph-sync}.yml
.gitignore
CONTRIBUTING.md
README.md
SECURITY.md
docs/ARCHITECTURE.md
docs/DECISIONS/0001-scope-and-governance.md
docs/DEPENDENCY_MANAGEMENT.md
docs/DEVELOPMENT_ROADMAP.md
docs/PROJECT_STATUS.md
docs/README.md
docs/SETUP_REPORT.md
docs/TEAM_WORKFLOW.md
docs/TEAM_WORKLOAD.md
scripts/governance/{check_docs,gate,github_api,security_check,sync_issues,workload}.py
tests/governance/test_gate.py
```

[Team workflow](TEAM_WORKFLOW.md) and [CONTRIBUTING](../CONTRIBUTING.md) explain issue → prerequisite check → updated main → numbered branch → code/tests → commit/push → PR → CI/review → approved merge → evidence acceptance → issue/board update. macOS M3 and Windows PowerShell examples are included. CUDA is never assumed on Apple Silicon. Product approval gates, GitHub review and research experiment counts remain distinct.

## 10. Remaining owner actions in dependency order

1. Explicitly approve Project Write invitations for the four exact collaborators above. This is separate from already-verified repository Write.
2. Burkay independently reviews the final PR #38 revision. The owner then explicitly approves merge; no automatic merge is configured.
3. After approved bootstrap merge, run real canary checks on legitimate existing tasks. Verify trusted-base gate pass/fail, missing dependency/CI/review rejection and re-evaluation without faking accepted prerequisites.
4. After those live checks and explicit owner approval, activate main protection with only proven check names. Proposed command from an authorized owner session: `gh api --method PUT repos/caferkilinc/refactoring-ai-generated-code/branches/main/protection --input .github/branch-protection.proposed.json`. It has not been executed.
5. Independently review trusted acceptance entries through a restricted governance PR. Re-run failed Dependency gate jobs or push a normal new commit after prerequisite acceptance; closing an issue alone does not reevaluate the gate.
6. Confirm weekly capacity, GPU/runtime and provider/data-transfer/budget decisions. #19 and #25 remain resource-blocked; no purchase or API consumption is authorized by this report.

Original user instruction preserves these approval boundaries: “PR’leri otomatik merge etme”, “Kullanıcı erişimlerini onayım olmadan değiştirme” and “Yalnızca ... kritik koruma ayarı ... veya merge gibi yüksek etkili işlemlerde açık onay iste.” The general request to finish the work does not erase those explicit boundaries. No skill-specific extra approval requirement is being inferred.

## 11. Academic document continuity

The previously delivered five-person DOCX and role-swapped planning document remain preserved. They are academic/source documents, not automatically published files. The older H1–H12 schedule is superseded for implementation by the dated canonical GitHub plan; the GitHub instruction explicitly said not to rewrite the DOCX again. Taha retains Frontend/Reporting; Burkay retains Language Adapters/Analysis; Alperen retains Local AI/Parallel Refactoring. The public repository contains no academic DOCX. TÜBİTAK application/advisor eligibility and course approval remain separate decisions.

## 12. Completion boundary

Issues, assignment consistency, saved views, date/effort data, acceptance-safe routing and governance tests are established. Configuration files are prepared in the open PR. Private Project team access, independent review, merge and live main protection activation remain owner/reviewer actions; the platform itself remains development work. (Görev sistemi ve test edilmiş kurulum hazırlanmıştır; erişim/onay/aktivasyon adımları açıkça beklemede tutulur.)
