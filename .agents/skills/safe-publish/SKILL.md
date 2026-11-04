---
name: safe-publish
description: Publish one reviewed Project Genesis task after explicit PUSHLA authorization. Use for commit, feature push, pull request, hosted gates and verified merge under active trusted policy.
---

# Publish one reviewed Genesis task

Use only after an actual authorized developer reviews the exact content, review ID, scope and verification results. Interpret `PUSHLA` or an unambiguous equivalent in that context as consent for the eligible publication transaction. Discussion, an earlier revision's approval and `ONAYLA` for local review alone grant no publication authority. Keep implementation and publication separate.

1. Recheck repository identity and live main through [repo-bootstrap](../repo-bootstrap/SKILL.md). Reconcile current task, actor and protected authority through [task-context](../task-context/SKILL.md). Follow the separately authorized [activation procedure](../../../docs/reports/MIG-04.md) for protected governance work.
2. Carry the exact private contract, session, review ID, diff and developer decision from [task-execution](../task-execution/SKILL.md). Require actual local checks per [verification](../verification/SKILL.md), a reviewed report, and independently verified protected authority where applicable. Authenticate to GitHub as that same developer. When the reviewed scope explicitly contains protected authority and the authenticated developer is the project owner, the one command covers it.
3. Use the trusted [publisher](../../../scripts/governance/safe_publish.py). Keep JSON inputs and the journal outside the checkout. Supply the actual decision reference for the exact reviewed content. The developer's `GH_TOKEN` must be available to the process without appearing in argv, the contract or logs. The supported classic protection configuration must be verifiable, including Actions-bound checks. A token with insufficient privileges blocks the affected operation.

```text
python -B scripts/governance/safe_publish.py --contract CONTRACT.json --session SESSION.json --review REVIEW.json --journal PUBLICATION.json --review-id EXACT_REVIEW_ID --approval PUSHLA --approval-ref HUMAN_DECISION_REFERENCE
```

The helper commits only reviewed paths and verifies the committed bytes. It preserves unrelated work and blocks if unrelated changes are staged. It pushes only the verified feature ref, reconciles the task PR, posts an authenticated SHA-bound approval comment and triggers fresh trusted gate checks. Mandatory CI must pass on the exact revision. Native GitHub reviews, when required, remain mandatory. A PR author's issue comment is an attestation with a separate role from a native review.

After a bounded wait, merge proceeds automatically when all gates pass. A pending result preserves the PR and journal for resumption with the same approval. If a push or merge fails, preserve the commit or PR and report the error. Resuming unchanged work with the same journal and authorization requires no new confirmation. A different diff, base, developer or review requires a new review. The helper does not keep running after the process exits.

Verify the actual merge and post-merge checks. Use [development-handoff](../development-handoff/SKILL.md) for evidence without re-entering execution. When trusted main has activated MIG-05, the publisher prepares one protected transaction containing acceptance, rotation and history. Review and integrate the exact transaction through the separately authorized route in the [MIG-05 report](../../../docs/reports/MIG-05.md). Until it lands, retain `MERGED_PENDING_ACCEPTANCE`. Resuming an already accepted PR evaluates phase eligibility without advancing rotation again. Use [next-step](../next-step/SKILL.md) only for a canonically accepted handoff.
