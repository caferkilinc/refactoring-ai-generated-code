# Project Genesis v3.0 — Codex-native governance

**Phase 1.** This policy takes effect after explicit protected owner authorization, reviewed integration on canonical `main`, and verification of hosted enforcement. Until then, follow the currently effective protected workflow. After activation this document supersedes the development-governance process in the [v2.1 protocol](PROJECT_GENESIS_ORCHESTRATOR_PROTOCOL_V2_1.md) and dated operational snapshots. The [v2 owner decision](../DECISIONS/0004-sole-owner-approval.md), [PR #45 delegation](../DECISIONS/0006-pr45-revision-bound-delegation.md), and prior acceptances remain historical evidence. The approved product [SRS TR](../SRS.md), [SRS EN](../SRS_EN.md), [architecture](../ARCHITECTURE.md), and separate product approvals remain authoritative for product behavior. Activation must explicitly reconcile the older execution-governance clauses in those approved records.

## Authority and trusted sources

- Protected owner decisions and approved product contracts govern scope and security. Repository permissions and branch rules govern GitHub operations. Neither a task contract nor a PR can grant itself wider permissions.
- Verify canonical `caferkilinc/refactoring-ai-generated-code` and query live `refs/heads/main`. Pin the source SHA for [task-plan](../../.github/task-plan.json), [acceptance](../../.github/acceptance.json), applicable product documents and [project status](../PROJECT_STATUS.md). Confirm the SHA again before integration, acceptance or issuing a task contract. Reconcile drift before proceeding. The trusted registry supplies active task, owner, scope, and required checks. Native GitHub dependencies must agree with the registry. Issue assignees, PR text, chat and project cards can provide context only.
- The single active writer rotates **Burkay → Cafer → Alperen Enes Yaman → İsmail → Taha Uğur Toyran → Burkay**. The active developer explicitly authorizes Codex to execute the registered task through a bounded contract with repository, issue, task ID, owner, pinned baseline, branch, accepted prerequisites, allowed scope, acceptance criteria, checks and stop conditions. A separate, recorded owner exception is required for protected maintenance during another developer's turn. Maintenance does not consume a turn.

## Execution and publication

1. **Sync safely.** Verify origin, branch/upstream, local changes, linked worktrees, Git locks, attributes and checkout configuration. Fetch the canonical references without pruning or forcing. Fast-forward clean `main` only when verified safe. Preserve local work and use a dedicated numbered topic branch. Stop on divergence, source uncertainty or unauthorized scope.
2. **Implement and verify.** Load the relevant approved sources, execute the bounded task, run applicable positive and negative checks, review the real diff and record commands, outcomes and limitations in `report.md`. `LOCAL_VERIFIED` requires passing applicable local checks. Pause after two speculative repairs without new evidence.
3. **Review and authorize.** The active human developer reviews the actual diff and test evidence and explicitly authorizes each publication operation. Commit, push and PR creation require authorization for their own scope. Review the final commit SHA before pushing. On the PR conversation the authenticated developer records merge-scope approval as one exact line:

   ```text
   GENESIS-DEVELOPER-APPROVED: <PLAN_ID> <OWNER/REPO> <BRANCH> <FULL_HEAD_SHA> merge
   ```

   The trusted gate matches the API comment actor to the active developer and PR author, and checks the task, canonical head repository, branch, revision and scope. `DEVELOPER_APPROVED` is evidence of review and authorization for that revision and scope. A new head needs fresh approval. Delete a withdrawn marker and rerun the gate before merging. GitHub's independent PR review, where required, remains separate from the developer's comment.
4. **Verify hosted evidence.** The read-only Dependency gate runs policy from current trusted `main`. Rerun it after approval and CI complete. `HOSTED_VERIFIED` requires dependency-gate and merge-readiness plus all applicable successful GitHub Actions checks for the revision, and any independently required hosted reviews and rules. Changes to head, policy, dependencies or authorization require fresh checks. Completed runs are snapshots, so recheck mutable evidence immediately before a human-authorized merge.
5. **Confirm publication.** Keep the PR route to `main` and existing protections. `MERGED` requires the GitHub merge record, matching source SHA and a merge commit reachable from verified `main`. It leaves acceptance pending.

## Protected changes

Obtain separate, recorded authorization from the project owner for changes to approved SRS or major architecture, mandatory scope reductions, security policy weakening, frozen research data, irreversible destructive operations, or governance changes that expand authority. The authorized protected task must still cover each changed path. The gate checks known protected paths, including both sides of renames, and requires the owner's authenticated `GENESIS-OWNER-APPROVED: <FULL_HEAD_SHA>` comment as well as the active developer's approval. Human scope and security review must detect protected intent expressed elsewhere. Keep existing GitHub review, dependency, CI and security controls. A protected PR must never supply the policy that authorizes its own head.

## Independent acceptance and next prompt

- An independent verifier checks the reviewed contract against actual diff, acceptance criteria, approval, CI, source/merge ancestry, completed issue and evidence links. Use the gate's read-only handoff mode from trusted policy to validate a candidate record. The input has `pr`, `head_sha`, canonical `developer` and HTTPS `evidence`, optionally `ci_sha` for the PR head or actual merge commit. Supply the independently verified current `main` as `--policy-sha`.

  ```sh
  python3 scripts/governance/gate.py --mode handoff --pr PR_NUMBER --expected-head HEAD_SHA --policy-sha MAIN_SHA --handoff-record REVIEWED_RECORD.json
  ```

  The command reads registry and acceptance at the pinned SHA. `REVIEW_REQUIRED` proposes a next index and owner with no writes. `ALREADY_ACCEPTED` has no rotation effect. A different revision for an already accepted task or a missing record for a used key blocks reconciliation. Historical records without `developer` retain their original approval evidence.
- `HANDOFF_ACCEPTED` requires the independently reviewed record and rotation update to land together in trusted `main`, with exact head, merge and CI evidence. Treat `plan_id:head_sha` as the idempotency key. Check the latest registry and accepted issue before preparing the update. If main moves, reverify against the new SHA and repeat the duplicate check. A failed, incomplete, withdrawn or duplicate handoff leaves the owner and index in place. Phase 1 supplies verification and a proposal only. Recording and publication remain explicit protected operations.
- After confirmed acceptance, Codex may draft a **preparation-only** prompt for the next registered developer from fresh main, approved product sources and accepted prerequisites. Include owner, task/issue, repository, baseline, branch, allowed and forbidden scope, checks, acceptance evidence, and stop conditions. The next human developer verifies and authorizes execution. If the next task, prerequisites, source, or authority are ambiguous, stop and report the specific gap. Phase 1 does not automate task selection, prompt generation, publication, or rotation writes.

## Recovery

Keep task, branch, head/main SHAs, actors, approval/CI URLs, check results and acceptance key in the review record. If enforcement cannot be verified, stop publication and preserve the branch and evidence. Recheck policy and actual GitHub configuration with the authorized administrator. Roll back a published policy through a separately owner-authorized revert PR with the same review and check protections. Preserve the acceptance registry and audit history during reconciliation.
