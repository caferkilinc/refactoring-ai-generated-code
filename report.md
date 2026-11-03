# PROJECT GENESIS v2.0 — F00-V0 handoff

REPORT_SCHEMA_VERSION: 1<br>
PROJECT: Refactoring AI-Generated Code<br>
TASK_ID: F00-V0<br>
MILESTONE_ID: F00<br>
OWNER: Cafer Kılınç (@caferkilinc)<br>
GITHUB_ISSUE: #9<br>
DATE: 2026-11-03 (Europe/Istanbul)<br>
BRANCH: feature/9-java-v0-pilot<br>
BASE_COMMIT: aa7d2c810a3c19dbc92bd6efa69c517a598dde7e<br>
STATUS: REVIEW_REQUIRED<br>
HANDOFF_STATUS: BLOCKED<br>
PUBLICATION: VERIFIED_FOR_OBSERVED_COMMITS — final containing HEAD delivered externally<br>
OBSERVED_IMPLEMENTATION_SHA: 5ad4c27f591e86c6b81cc140214eff75c7d65922<br>
OBSERVED_CI_CORRECTION_SHA: eae5d891e926ec12b87375023f33b813cc1c64a2<br>
OWNER_APPROVAL: PENDING — no authenticated current-HEAD approval<br>
LOCAL_ARTIFACT_STATE: LOCAL_SEALED_PENDING_OWNER_ACCEPTANCE

## OBJECTIVE

Implement only the genuine AI-generated Java inventory/order pilot, its
external fixed tests, truthful provenance, distinct raw-byte SHA-256 manifests,
reproduction procedure and real pilot-checks workflow. This does not complete
F00, the twelve-task study, any adapter or the refactoring platform.

## BASELINE

Repository: `/Users/caferkilinc/Desktop/refactoring-ai-generated-code/refactoring-ai-generated-code`.
Canonical origin: `https://github.com/caferkilinc/refactoring-ai-generated-code.git`.
Initial local main was `7e068040c3a4fb1a2f32783a4c592dc974324f36`, 110 commits
behind, zero ahead. Only the two known untracked `.DS_Store` files existed;
tracked/staged files were clean, one worktree, no in-progress Git operation.
Verified their paths absent from incoming main, preserved them, fetched all
canonical branch refs/tags, and ran `git pull --ff-only origin main`.
Main now equals BASE_COMMIT. Existing main `.gitignore` ignores those preserved
files. No equivalent issue-9 branch existed; created the branch above at main.

Live Issue #8 is closed/completed, #9 open; native #9 predecessor is only #8.
Trusted registry confirms active `caferkilinc` / `F00-V0`, rotation index 1.
Acceptance records PR #44 source `a281caec295487b78371bac1e106cb378fa64bba`;
merge `ac321cb43fdea3f6b64bb1631de8daca8cf1d229` is an ancestor of BASE_COMMIT.
The previous report is retained in Git history at
[the accepted source revision](https://github.com/caferkilinc/refactoring-ai-generated-code/blob/a281caec295487b78371bac1e106cb378fa64bba/report.md).
The development-handoff skill was read and its procedure followed manually;
no automatic skill invocation or parallel agent framework is claimed.

## IMPLEMENTED

- One generated standard-library `Inventory` class and immutable receipt, with
  defensive initial-state copy, stock lookup, successful orders, validation,
  insufficient-stock rejection, exact-stock boundary and state preservation.
- Java 21 Maven project, pinned plugins and test-only JUnit 5.12.2; ten fixed
  external regression tests. No production dependency or artificial defect.
- Exact execution contract, contemporaneous generation instruction and one
  attributable source-generation attempt; separate versioned source/test
  manifests with external manifest digest receipts.
- Read-only integrity verifier; temporary-copy reproduction with actual Maven
  execution and Surefire XML inspection; meaningful failing-regression probe.
- Least-privilege, pinned-action GitHub workflow defining `pilot-checks`.
  Hosted execution passed at the observed CI-correction revision; see publication evidence.

## FILES_CHANGED

- `.github/workflows/pilot-checks.yml` — only new permitted workflow.
- `experiments/original-ai-code/java-inventory-v0/` — original `Inventory.java`,
  `pom.xml`, task-local `.gitignore` excluding `target/`.
- `tests/fixtures/java-inventory-v0/src/test/java/org/genesis/pilot/InventoryTest.java`.
- `experiments/java-pilot/` — README, `verify_integrity.py`, `reproduce.py`,
  `provenance/`, two `manifests/*.json` plus `.sha256` receipts, and actual
  command/result/log artifacts under `evidence/`.
- `experiments/README.md`, `experiments/original-ai-code/README.md`,
  `docs/PROJECT_STATUS.md` — bounded local-state links and historical distinction.
- `report.md` — latest-task snapshot; previous report remains in history.

No governance code/tests/registries, AGENTS.md, SRS, architecture, roadmap or
other protected workflow was edited. Build output stays ignored and temporary
reproduction workspaces are removed. Original local file inventory is recorded in
[verification.json](experiments/java-pilot/evidence/verification.json); the complete
published task inventory and hosted results are in
[publication-checks.json](experiments/java-pilot/evidence/publication-checks.json).

## REQUIREMENTS_COVERED

| Requirement | Bounded task evidence |
|---|---|
| FR-003 | Original bytes preserved; post-seal execution in disposable derivatives |
| FR-009 | Actual Java 21/Maven AI output, prompt/attempt record, external JUnit tests and hashes |
| NFR-02 | Separate raw-byte manifests, before/after verification and negative probes |
| NFR-04 | Actual tool/environment outputs, pinned build/test configuration and reproduction logs |
| NFR-09 | One small standard-library class, no database/server/framework or test inflation |

This is pilot-level coverage, not full-platform acceptance of these requirements.
JavaParser/PMD/CPD/JaCoCo, security scanners and product sandbox belong to their
later tasks; no coverage or quality-improvement percentage is claimed.

## GENERATION_PROVENANCE

[Recorded attempt ledger](experiments/java-pilot/provenance/generation.json)
links the saved owner contract, current agent instruction and actual output.
`F00-V0-GEN-001` is one genuine current-Codex attempt. First compilation/tests
passed; no source correction occurred. Provider OpenAI and agent Codex are
known. Exact serving model ID/revision, sampling settings, provider request ID,
usage/cost and provider-side timestamps are UNKNOWN because not exposed.
The capture time is explicitly distinguished from provider generation time.
No historical metadata or failed attempts were fabricated; this is attributable
agent evidence, not complete or independently attested provider provenance.

The synthetic owner-authorized pilot uses no third-party/customer source,
production data or secret; no external inference request was made. This task
contract permits local controlled pilot verification. It does not grant public
publication or blanket execution rights over later untrusted inputs.

## V0_INTEGRITY

Source revision: `java-inventory-v0.1`, locally sealed pending owner acceptance.
[Manifest](experiments/java-pilot/manifests/v0-source.json): five files covering
production source, POM and three provenance artifacts. Raw-byte manifest SHA-256:

`1650a915ea6516e52ac27c1a4c98a11d0ddd62155f41ec6a21835b0195311376`

Original generated `Inventory.java` capture SHA-256:

`64578428482fd874797fb56822b50690f30565afbc5c1a4bed2b27128a4d2e21`

The original source still matches its first captured bytes. Sorted paths and
serialization/version are recorded in the manifest. Its digest receipt is
separate; no self-referential hash or build output is in the input inventory.
Do not regenerate receipts to bless drift. Changes require a traceable baseline
revision and owner decision. Unsigned hashes are integrity evidence, not proof
against simultaneous adversarial replacement of inputs and receipts.

## TEST_SUITE_INTEGRITY

[Fixed-suite manifest](experiments/java-pilot/manifests/fixed-tests.json) covers
one external JUnit source with ten behavioral tests. Manifest SHA-256:

`d5f17c053d0e9d6f0e7e6a7b2a51c8039edbb42d8a0b025a46a9193740b63028`

Test bytes were not edited after capture/seal. Source and tests passed integrity
checks before and after temporary-copy execution. This local seal is not a
Burkay-approved dataset freeze: the minimum twelve-task dataset is NOT_FROZEN.

## ACCEPTANCE_CRITERIA

| ID | Expected | Actual and evidence | Result |
|---|---|---|---|
| AC-01 | Repository and accepted predecessor verified | Canonical URL, live #8 completed, acceptance #8/#44 and main ancestry; BASELINE | PASS |
| AC-02 | Correct active developer/task | Registry `caferkilinc` / F00-V0, open #9, single native predecessor #8 | PASS |
| AC-03 | Available Java 21 and Maven | Temurin 21.0.4+7; user-local Maven 3.9.11, verified distribution digest; environment.json | PASS |
| AC-04 | Genuine AI output and attributable provenance | One actual attempt, saved instructions/output hash, truthful UNKNOWN metadata; generation.json | PASS |
| AC-05 | Successful compilation | Initial and temporary-copy Maven builds exit 0; maven-initial.log.json / reproduction.log.json | PASS |
| AC-06 | Coherent inventory/order behavior | Real state/receipt assertions; InventoryTest and actual Surefire results | PASS |
| AC-07 | Passing external fixed JUnit suite | 10 tests, 0 failures/errors/skips in each successful build | PASS |
| AC-08 | Failure and boundary cases | Invalid/unknown/insufficient, exact/zero/max stock, rejected-state preservation and defensive copy | PASS |
| AC-09 | Reproducible V0 manifest | Raw-byte source manifest verified in original and derivative; changed-source probe rejected | PASS |
| AC-10 | Reproducible test manifest | Separate test manifest verified; changed/missing-test probes rejected | PASS |
| AC-11 | Unchanged sealed source/tests | Before/after checks and original capture digest match; formal owner freeze still pending | PASS |
| AC-12 | No artificial defects in V0 | Source reviewed; first attempt unchanged; deliberate failing probe exists only in a disposable derivative | PASS |
| AC-13 | Real hosted pilot-checks workflow | Corrected workflow executed ten actual JUnit tests and before/after integrity checks on Ubuntu; run 41687880387, source eae5d891e926ec12b87375023f33b813cc1c64a2 | PASS |
| AC-14 | Accurate check outcomes | Actual local and hosted evidence; required four checks passed at observed correction SHA; merge-readiness failed for missing owner approval, preview SKIPPED | PASS |
| AC-15 | Scoped final diff | Existing path gate and full new/modified-file review; verification.json | PASS |
| AC-16 | Evidence-based handoff | This report, actual artifacts, limitations and human actions; publication pending | PASS |

All sixteen task criteria have local/hosted evidence at the observed correction
revision. This is not accepted handoff or merge readiness: Burkay approval,
final-containing-HEAD verification and orchestrator acceptance remain separate.
The final chat receipt supplies fresh checks for the containing report revision.

## VERIFICATION

Actual initial command, using the installed Maven executable:

```sh
/Users/caferkilinc/.local/share/project-genesis/apache-maven-3.9.11/bin/mvn -B -ntp -f experiments/original-ai-code/java-inventory-v0/pom.xml clean verify
```

Exit 0; ten actual JUnit tests passed. The initial build occurred before local
sealing; later verification uses a derivative. Repeatable post-seal commands:

```sh
python3 -B experiments/java-pilot/verify_integrity.py
python3 -B experiments/java-pilot/reproduce.py --maven /Users/caferkilinc/.local/share/project-genesis/apache-maven-3.9.11/bin/mvn
python3 -B -m unittest discover -s tests/governance -v
python3 -B scripts/governance/check_docs.py
python3 -B scripts/governance/security_check.py
git diff --check
```

Local outcomes: 102 governance tests passed; documentation and security hygiene
checks passed; workflow YAML parsed; task path policy passed; source/test
integrity passed. Exact command outputs are in verification.json. Security
hygiene remains a limited credential/private-artifact check.

[Environment](experiments/java-pilot/evidence/environment.json),
[initial build](experiments/java-pilot/evidence/initial-run.json),
[reproduction](experiments/java-pilot/evidence/reproduction.json),
[integrity probes](experiments/java-pilot/evidence/integrity-negative-probes.json),
[regression rejection](experiments/java-pilot/evidence/regression-rejection.json)
and [final local verification](experiments/java-pilot/evidence/verification.json)
record actual commands/results and limitations. The deliberate regression
caused five test failures, Maven exit 1 as expected; it is a successful negative
validation probe, not a concealed generation failure. The six integrity probes
all returned nonzero as required. The two successful local builds produced JAR
SHA-256 `932baefb2c4d17abf836ed2dd503b4d145e7604fa68533166288e3e38035e6bb`.

At the observed correction SHA, governance-tests, documentation-checks,
security-checks and pilot-checks all completed SUCCESS. Dependency-gate passed;
merge-readiness failed for missing Burkay approval, and dependency-gate-preview
was SKIPPED. Exact runs/jobs and source/test-merge revisions are in publication
evidence. These are task PR checks, not old main results. The report-containing
revision will be checked again and its results delivered in the final chat
receipt. Governance/hygiene do not prove full product security or E2E behavior.
Initial new-file whitespace review identified Maven's natural trailing spaces in
raw log output. Exact bytes were preserved losslessly in JSON log artifacts
(with raw-byte SHA-256), and raw copies kept user-locally; no check was weakened.
Affected checks were rerun. Full source/static review, workflow syntax review, task path policy, ignored
build-output inspection and whitespace checks are included in final local
verification. No failing check was suppressed or test weakened.

## ARCHITECTURE_AND_SCOPE

The seven mandatory languages, real Falcon-Mamba, two product approvals,
immutable artifacts, isolated candidate/combined verification and complete
reporting remain P0. None is implemented by this small pilot. No dependency
edge, registry, architecture, team rotation or milestone completion was changed.
Only necessary Maven tooling was installed user-locally; no unrelated framework,
model, cloud API, deployment or system package upgrade occurred.

## RISKS_AND_BLOCKERS

- Publication was explicitly authorized and observed; Burkay's authenticated
  final-HEAD approval, merge authorization and orchestrator acceptance remain.
  merge-readiness is FAILED for that missing approval; no gate was bypassed.
- Exact serving model metadata is unavailable and disclosed; do not claim full
  provider-level provenance. No additional historic prompt/model input is invented.
- Local execution is controlled synthetic pilot verification, not the later
  product sandbox. Future untrusted uploads must not run directly on the host.
- Both local macOS and hosted Ubuntu execution passed with the pinned tools,
  and the observed JAR digests matched. Other platforms are unverified. No
  coverage guarantee, behavioral equivalence proof, quality reduction or
  research result is claimed.
- Project board read failed in startup with INSUFFICIENT_SCOPES (`read:project`);
  issue/registry authority was available. No credential or scope was changed.
- Later GPU/model/API permissions, budget, toolchains, privacy/data intake and
  dataset freeze gates remain outstanding; no new Java dependency is invented.

## NEXT_TASK_CANDIDATE

NOT_AUTHORIZED. Orchestrator selects later work only after accepted F00-V0
handoff. Do not start F01-ENV, F02-CONTRACT, F04-JAVA, Falcon-Mamba or any adapter.

## ROTATION

CURRENT_OWNER: Cafer (@caferkilinc)<br>
ROTATION_INDEX: 1 (unchanged)<br>
NEXT_OWNER_IF_ACCEPTED: Alperen Enes Yaman (@Yaman-A-E)<br>
ROTATION_ADVANCED: NO<br>
ACCEPTED_HANDOFF: NOT_CLAIMED

## HUMAN_ACTION

Cafer explicitly authorized commit, push and opening PR #45 in this chat on
2026-11-03. Publication preflight passed and both observed commits were pushed
with local/remote SHA equality and clean worktrees. The PR targets main and has:

```text
Task: #9
Plan: F00-V0
```

Burkay alone must provide an authenticated approval for the actual final PR HEAD:
`GENESIS-OWNER-APPROVED: <CURRENT_PR_HEAD_SHA>`. A new commit invalidates an old
approval. Then re-evaluate the live readiness gate under the applicable merge
policy; no merge or acceptance is authorized by this task. The final chat receipt
provides the actual full containing SHA, commit link, SHA-pinned report, PR state
and fresh check results. This evidence-only report update links already observed
published commits, not its own unknowable containing SHA. No endless
self-reference commit is created. Send that receipt and this report to the
orchestrator. Do not close Issue #9 or advance rotation. Stop after publication.

## First publication and bounded hosted-CI correction

Implementation commit `5ad4c27f591e86c6b81cc140214eff75c7d65922` was pushed
to canonical `feature/9-java-v0-pilot`; local/remote SHA matched and the worktree
was clean. [PR #45](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/45)
was opened by authenticated `caferkilinc`, targeting main. Earlier NOT_RUN and
pre-push statements above describe the prior local snapshot.

The first [Governance CI](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41687630454)
passed all three required governance jobs; the bootstrap preview was SKIPPED.
[Dependency gate](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41687630473)
passed dependency-gate but correctly failed merge-readiness for missing current
Burkay approval. [Pilot CI](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41687630491)
failed before Maven/JUnit: setup-java rejected `21.0.4+7` and listed the exact
available vendor-normalized version `21.0.4+7.0.LTS`. The only runtime correction
sets that offered version in the permitted pilot workflow; generated V0, POM,
provenance, fixed tests and their manifests remain byte-identical. This failed
setup is retained as an actual CI failure, not a failed source-generation attempt.
See [hosted history](experiments/java-pilot/evidence/hosted-ci-history.json).
The corrected revision `eae5d891e926ec12b87375023f33b813cc1c64a2` was pushed
and observed with the following real results:

| Workflow / job | Result | Evidence |
|---|---|---|
| Governance CI: governance-tests, documentation-checks, security-checks | SUCCESS | [41687880397](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41687880397) |
| Java pilot checks: pilot-checks | SUCCESS; 10 tests, 0 failures/errors/skips; V0/tests unchanged | [41687880387](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41687880387) |
| Dependency gate: dependency-gate | SUCCESS | [41687877219](https://github.com/caferkilinc/refactoring-ai-generated-code/actions/runs/41687877219) |
| Dependency gate: merge-readiness | FAILURE: missing current Burkay owner approval | Same dependency run |
| dependency-gate-preview | SKIPPED; not counted as PASS | Same governance run |

The pilot job checked out GitHub test-merge revision
`2ab3b76724eb3ca5d45eccb3a3eded9b71c49cba` associated with that PR source HEAD,
not a merged main commit. PR #45 remains OPEN and UNMERGED, Issue #9 OPEN,
acceptance/rotation unchanged. [Publication evidence](experiments/java-pilot/evidence/publication-checks.json)
records the observed source revision and actual job results. This containing
report revision is a later documentation/evidence update; its final full SHA
and fresh hosted results are supplied in the external final receipt.
