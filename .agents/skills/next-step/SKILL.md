---
name: next-step
description: Generate the Project Genesis next-task prompt from verified main and a canonically accepted handoff. Use for "Next step promptunu hazırla." or "Sonraki görev promptunu oluştur."
---

# Project Genesis next step

Use [repo-bootstrap](../repo-bootstrap/SKILL.md) to establish repository identity and trusted main. Use [task-context](../task-context/SKILL.md) to inspect only the approved product requirements, architecture sections, and issue relevant to the registered task. Resolve any scope gap before issuing a prompt.

1. Run `python -B scripts/governance/next_step.py status` from the canonical root. Stop if acceptance, assignment, dependencies or the pilot integrity gate is blocked.
   For the first post-migration handoff, read the [protected sequencing record](../../../docs/governance/migrations/POST_MIGRATION_HANDOFF.json). The planned developer is Alperen (`Yaman-A-E`). An exact frozen-related task must be reconciled with the canonical active assignment through the authorized protected workflow. Report unresolved task identity or assignment conflicts. Preserve the existing product rotation.
2. Run `python -B scripts/governance/next_step.py draft` to preview the contract. It verifies active trusted v3, native dependencies, the last accepted PR, phase state and source provenance. A merged task with pending acceptance provides no next-task authority. When a local archive is requested, run `python -B scripts/governance/next_step.py draft --archive`. It creates `docs/handoffs/<TASK-ID>/NEXT_STEP_PROMPT.md` without replacing an existing prompt.
3. Before anyone relies on the draft, run `python -B scripts/governance/next_step.py validate --prompt PATH`. A changed main revision, changed evidence, or altered prompt requires regeneration from trusted sources.
4. Hand the prompt to the registered developer and stop. The developer separately authorizes execution through [task-execution](../task-execution/SKILL.md). Any GitHub publication of the prompt follows the applicable documentation authorization and [safe-publish](../safe-publish/SKILL.md).

The [MIG-05 report](../../../docs/reports/MIG-05.md) documents the protected transaction boundary and activation prerequisites.
