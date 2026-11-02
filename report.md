# PROJECT GENESIS v2.0 — F00-PLAN handoff

REPORT_SCHEMA_VERSION: 1<br>
PROJECT: Refactoring AI-Generated Code<br>
TASK_ID: F00-PLAN<br>
MILESTONE_ID: F00<br>
GITHUB_ISSUE: #8<br>
OWNER: Burkay Çakar (@cakarburkayy)<br>
DATE: 2026-11-02 (Europe/Istanbul)<br>
REPOSITORY: `C:\refactoring-ai-generated-code`<br>
BRANCH: `docs/8-freeze-evidence-protocol`<br>
BASE_COMMIT: `67233482f2d10462933328c4b162d150bb4b0993`<br>
STATUS: READY_TO_PUSH<br>
HANDOFF_STATUS: PENDING_PUSH_CONFIRMATION<br>
GIT_PUBLICATION: NOT_YET_CONFIRMED<br>
OWNER_PUBLICATION_AUTHORIZATION: Explicitly granted by Burkay in chat on 2026-11-02

## OBJECTIVE

Establish the bounded F00 research baseline, >=12-task dataset selection/freeze procedure, reproducible measurement and resource decisions against approved TR/EN SRS v0.4.0. Prepare evidence for human review; no pilot/application implementation or subsequent task.

## BASELINE

Preflight inspected root, `git status --short`, branch, HEAD, remotes and `git branch -vv`. The chat working directory was not a Git repository; the previously prepared repository above was verified as the expected origin. Initial worktree was clean on `main`, tracking `origin/main`. `git fetch origin --tags` succeeded; local and remote main both remained at BASE_COMMIT. No equivalent F00/issue-8 task branch existed; the new local branch starts at that SHA and has no upstream yet.

Historical September baseline `7e068040c3a4fb1a2f32783a4c592dc974324f36` (ten commits/eight Markdown files), PR #38 merge `5754ed6eeaeef0cce9bc46264c8baeddfb62f88c` and PR #39 merge `5c297836b9ec70112e7b662eac05ec966543a134` are ancestors of HEAD. Baseline has 53 tracked files: governance and documentation, no application or executable experiment. Issue #8 was fetched read-only and is open with no comments. Registry confirms Burkay/F00-PLAN, no technical prerequisites and no accepted Genesis handoff.

## IMPLEMENTED

- One [research baseline/protocol](docs/DECISIONS/0005-f00-research-baseline.md), with historical evidence, admission/exclusion states, >=12-task freeze, SHA-256 source/test integrity and Java pilot prerequisites.
- Separate quality/behavior results, explicit 50% target/formula, three matched repetitions per condition, failure-inclusive denominators, actual runtime/token/cost accounting and evidence retention.
- Resource matrix tied to existing tasks, owner-reported GPU/API contacts, and a separate attributed verbal academic approval record.
- Experiment README link and appended current project status; historical records preserved.
- Persistent owner-directed delivery rule: every task ends with its full verified SHA, commit-pinned report link and actual verification summary in chat (protocol section 8).

Only documentation is implemented here. Dataset NOT_FROZEN; pilot/product NOT_STARTED; research runs NOT_RUN. F00-PLAN completion does not complete the whole F00 milestone: F00-V0 remains outstanding.

## FILES_CHANGED

| Path | Change |
|---|---|
| `docs/DECISIONS/0005-f00-research-baseline.md` | Canonical F00 research protocol/resource record and persistent report-delivery policy |
| `experiments/README.md` | Link protocol and state actual evidence availability |
| `docs/PROJECT_STATUS.md` | Append F00 snapshot, publication authorization and report-delivery requirement |
| `report.md` | New latest-task handoff report under continuity exception |

## REQUIREMENTS_COVERED

FR-009, FR-047, FR-048, FR-049, FR-050; NFR-02, NFR-04, NFR-09, NFR-13. Protocol section 7 maps each to later real execution evidence. Supporting safety references: FR-003–004, FR-030–036, FR-038–044, NFR-01/03/05. Coverage means requirements-aligned protocol, not verified product implementation.

## ACCEPTANCE_CRITERIA

| ID | Expected | Actual / evidence | Result |
|---|---|---|---|
| AC-01 | Inspect safe actual repository baseline | Clean main/expected origin and upstream; fetch unchanged SHA; numbered branch created; BASELINE above | PASS |
| AC-02 | Align approved TR/EN v0.4.0 without demoting P0 | Protocol sections 1/7 preserve seven languages, Falcon-Mamba and safety/reporting scope; bilingual governance tests pass | PASS |
| AC-03 | Preserve history and decisions | Historical and both merge commits are ancestors; existing ADRs unchanged; status only appended | PASS |
| AC-04 | Define task, inclusion/exclusion and >=12 fixed tasks honestly | Protocol section 2; no samples invented, dataset NOT_FROZEN | PASS |
| AC-05 | Define freeze, V0/tests, versions and evidence IDs | Protocol sections 2–3; raw-byte manifests, change control and traceable evidence chain | PASS |
| AC-06 | Separate behavior/quality; define formulas/denominators | Protocol section 4; target >=50%, new findings, zero/missing values and failed behavior retained | PASS |
| AC-07 | Three matched repetitions/condition with cost/failures | Protocol section 4; SEQ/PAR R1–R3, fixed inputs/settings, planned/started/request denominators; none executed | PASS |
| AC-08 | Evidence-based resource statuses and roles | Protocol section 5; local Git/Python verified, resource contacts owner-reported, actual GPU/API/toolchain/data access UNKNOWN | PASS |
| AC-09 | Separate course approval from product-owner approval | Hakan Çağlar verbal approval on 2026-10-28 reported by Burkay; Burkay's later explicit instruction accepts this for AC-09. Protocol section 6 retains REPORTED provenance and unknown exact viewed revision | PASS — owner-accepted verbal evidence |
| AC-10 | Authorized files only, no later implementation | Existing path gate accepts exactly four listed Markdown files; full diff/content inspected; no protected changes | PASS |
| AC-11 | Execute actual applicable checks | 101 governance tests, documentation, security hygiene, path policy and whitespace checks pass; outputs below | PASS |
| AC-12 | Accurate task/owner/baseline/files/results/blockers/publication/conditional successor | This report contains actual outcomes and unresolved later resources; full published SHA and pinned report are delivered in the final chat receipt | PASS |

AC-09's original independent-document requirement is superseded only by the owner's explicit instruction in this chat: no reference exists, verbal approval was obtained, and AC-09 is to pass. No academic document or authenticated GitHub approval is fabricated. Git's latest reachable main commit before 2026-10-28 end-of-day is BASE_COMMIT, dated 2026-10-27; it is a plausible scope reference, not proof of what the academic approver viewed.

## VERIFICATION

Commands run from the repository above on Windows with Git 2.53.0.windows.3 and Python 3.14.5. `PYTHONDONTWRITEBYTECODE=1` prevents generated Python cache artifacts; no dependencies installed.

| Command / inspection | Result | Relevant evidence |
|---|---|---|
| `git rev-parse --show-toplevel`; `git status --short`; `git branch --show-current`; `git rev-parse HEAD`; `git remote -v`; `git branch -vv` | PASS | Actual root/origin, clean initial main and tracking; BASE_COMMIT |
| `git fetch origin --tags`; `git rev-parse main origin/main` | PASS | Successful fetch; both SHAs equal BASE_COMMIT |
| `git for-each-ref --format=%(refname) refs/heads refs/remotes`; `git switch -c docs/8-freeze-evidence-protocol` | PASS | No equivalent existing branch; new branch based on main |
| `git log 7e068040c3a4fb1a2f32783a4c592dc974324f36 --oneline --max-count=12`; `git ls-tree -r --name-only HEAD`; ancestry checks for the three historical/merge SHAs | PASS | Historical scaffold retained; no product/experiment source; all ancestry checks exit 0 |
| `python3 -m unittest discover -s tests/governance -v` | PASS | Initial run: 101 tests in 0.141s; publication revision: 101 tests in 0.077s; both OK, exit 0 |
| `python3 scripts/governance/check_docs.py` | PASS | Exit 0: Local documentation links and required artefacts verified |
| `python3 scripts/governance/security_check.py` | PASS | Exit 0: Repository hygiene checks passed; not a claim of full security analysis |
| Existing `gate.check_paths` against actual modified + untracked paths via inline `python3 -` | PASS | Exactly four authorized paths accepted; no policy bypass, staged changes or HEAD change |
| `git diff --check`; untracked-file whitespace/UTF-8 inspection via inline `python3 -` | PASS | Initial staged check FAILED on Markdown two-space hard breaks in new files; converted to explicit HTML breaks and reran the staged check without weakening it |
| `git diff --stat`; `git status --short`; full diff/content review | PASS | Only the four listed Markdown files; both existing-file diff and new protocol/report content inspected |
| Direct protocol-to-AC/FR/NFR review | PASS | Protocol sections 1–7 and criterion table above; no fictional measurements |
| Product builds/tests, real provider/model runs and scientific experiment | NOT_APPLICABLE | Documentation-only F00-PLAN; none executed |
| Hosted PR CI and authenticated current-HEAD owner approval | NOT_RUN | Not run at the prepublication snapshot; final current-HEAD hosted results belong in the publication receipt |

Governance checks do not validate an application. Security hygiene is the existing limited credential/private-artifact check, not full SAST/SCA. A local path-policy check does not replace live GitHub dependency/owner/CI checks.

## ARCHITECTURE_AND_SCOPE

Preserved approved architecture, all P0 scope, developer rotation, registry and protected governance files. Older P1/optional-model, independent-review and pending-merge/graph statements are identified as historical in protocol section 1; no repository-wide cleanup. Existing project-local `development-handoff` skill was read and its procedure followed manually; no automatic skill execution claimed. The initial task stopped before commit/push. The owner explicitly authorized publication in the follow-up. No dependency installation, API inference, model download or application code change.

## RESOURCE_STATUS / RISKS_AND_BLOCKERS

- **Local F00 acceptance:** no unresolved blocking check or required resource decision for this documentation task after the owner's AC-09 clarification. READY_TO_PUSH means local evidence is ready for human review/publication, not that the handoff is accepted.
- **F00 academic gate resolved by owner decision:** verbal Hakan Çağlar approval recorded as REPORTED; independent artifact and exact viewed SHA unavailable. This limitation is disclosed, not represented as independently VERIFIED.
- **Later execution gates remain:** no frozen dataset, Java pilot or sandbox; GPU/model/runtime access and provider/API permissions, budget and privacy/retention consents are unverified. Alperen Enes Yaman and Taha Uğur Toyran are reported resource contacts; per-resource custodian split is UNKNOWN. See protocol matrix for resolving actions and existing dependencies.
- **Schedule:** registry due date 2027-01-01; time/channel and available capacity UNKNOWN. Historical 436–666 person-hours are not a verified delivery forecast. No scope demotion or new deadline.
- **Publication/handoff pending:** local documentation is not an accepted handoff or completed milestone; hosted checks and authenticated current-head owner approval apply after the authorized publication.

## NEXT_TASK_CANDIDATE / ROTATION

F00-V0 (#9) is a candidate after accepted F00-PLAN, its existing sole prerequisite. This is not authorization or a claim of present eligibility; orchestrator decides the next task. F01-ENV's dependency remains F01-GOV; no new edges or assignments were added.

CURRENT_OWNER: Burkay<br>
NEXT_OWNER_IF_ACCEPTED: Cafer<br>
ROTATION_ADVANCE: NOT_YET_CONFIRMED

## AUTHORIZED PUBLICATION / MANDATORY REPORT DELIVERY

On 2026-11-02 Burkay explicitly authorized committing/pushing the final F00 work, gave owner approval, and required the actual report plus SHA to be delivered in chat every time. This supersedes the prior stop-before-commit/push restriction for this task. The connected GitHub identity was verified as `cakarburkayy`.

Publish the reviewed four-file change on `docs/8-freeze-evidence-protocol`, with a PR targeting `main` and these identity lines:

```text
Task: #8
Plan: F00-PLAN
```

The PR must retain real acceptance/check evidence. The user's authorization allows recording the authenticated `GENESIS-OWNER-APPROVED: <CURRENT_PR_HEAD_SHA>` comment through the verified owner account after the final HEAD is known. New commits invalidate previous SHA-bound approval. Hosted CI/dependency/readiness results remain mandatory; no merge, issue closure or rotation advancement is implied.

Report delivery is not complete merely because this file exists locally. Every subsequent authorized task must deliver the full verified SHA, commit link, report link pinned to that SHA, actual checks/PR status and readable summary in the final chat response. This persistent rule is recorded in ADR 0005 section 8 and PROJECT_STATUS. A later evidence-only commit may record an already verified published task SHA; the report's final containing SHA is supplied externally in chat to avoid impossible self-reference.

Submit the published SHA/report for orchestrator acceptance, then stop. F00-V0 and F01-ENV are not authorized by this publication request.
