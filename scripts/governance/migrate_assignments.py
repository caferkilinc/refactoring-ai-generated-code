"""One-time GitHub issue assignee migration; safe read-only preflight by default.

Use ONLY after reviewed Genesis policy is integrated into main. It intentionally
does not change technical task IDs, native issue dependencies, issue status,
milestones, labels, title or historical comments.
"""
import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from github_api import GitHub
from gate import validate_plan

ROOT = Path(__file__).resolve().parents[2]
FIXED_FIELDS = re.compile(
    r"(?m)^- (?:Primary Owner|Supporting Developer|Independent Reviewer):[^\n]*\n?"
)
PRIORITY_FIELD = re.compile(r"(?m)^(- Priority: )(P[01])\s*$")


def replacement(issue, task, team):
    """Return exact minimized PATCH body or None; fail on ambiguous source."""
    body = issue.get("body") or ""
    identity = "<!-- plan-id: " + task["plan_id"] + " -->"
    if body.count(identity) != 1:
        raise ValueError("Issue plan marker mismatch: #" + str(task["issue_number"]))
    if issue.get("state") not in ("open", "closed"):
        raise ValueError("Unknown issue status: #" + str(task["issue_number"]))
    assignees = issue.get("assignees", [])
    if not isinstance(assignees, list):
        raise ValueError("Issue assignees missing")
    names = {u["login"].lower() for u in assignees}
    if not names <= {user.lower() for user in team}:
        raise ValueError("Unrecognized issue assignee: #" + str(task["issue_number"]))
    matched = list(PRIORITY_FIELD.finditer(body))
    if len(matched) != 1:
        raise ValueError("Priority field missing or duplicated: #" + str(task["issue_number"]))
    current = matched[0].group(2)
    if current not in (task["priority"], "P1"):
        raise ValueError("Unexpected priority: #" + str(task["issue_number"]))
    if current == "P1" and task["priority"] != "P0":
        raise ValueError("Forbidden change from P1: #" + str(task["issue_number"]))
    after = FIXED_FIELDS.sub("", body)
    after = PRIORITY_FIELD.sub(lambda m: m.group(1) + task["priority"], after)
    changed = bool(assignees or after != body)
    return {"body": after, "assignees": []} if changed else None


def prepare(plan, api):
    """Read ALL registered issues before writing; preserve the original 31 tasks/54 links."""
    validate_plan(plan)
    legacy = [t for t in plan["tasks"] if t["issue_number"] in ({1} | set(range(8, 38)))]
    scope = plan.get("scope_decision_2026_10_27", {})
    if (len(legacy) != 31 or len(plan["tasks"]) != 34
            or scope.get("original_native_dependency_edges") != 54
            or sum(len(task["dependencies"]) for task in plan["tasks"]) != 69):
        raise ValueError("Approved 31-task baseline or 34-task dependency graph changed; stop")
    prepared = []
    for task in plan["tasks"]:
        issue = api.call("/issues/" + str(task["issue_number"]))
        patch = replacement(issue, task, plan["team"])
        prepared.append((task["issue_number"], issue, patch))
    return prepared


def run(plan, api, apply=False, approved=False):
    prepared = prepare(plan, api)
    changed = [(n, original, patch) for n, original, patch in prepared if patch]
    if not apply:
        return {"mode": "DRY_RUN", "planned": [n for n, _, _ in changed]}
    if not approved:
        raise ValueError("--apply requires explicit --owner-approved")
    if plan.get("scope_decision_2026_10_27", {}).get("graph_sync_status") != "VERIFIED":
        raise ValueError("Native GitHub parent/dependency graph must be VERIFIED before live assignment changes")
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=ROOT, text=True
    ).strip()
    if branch != "main":
        raise ValueError("Live migration may run only from checked-out main")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise ValueError("Working tree not clean")
    if plan.get("assignment_migration", {}).get("status") == "COMPLETE":
        raise ValueError("Registry is already marked COMPLETE")
    done = []
    for n, original, patch in changed:
        # Recheck the relevant issue immediately before write.
        latest = api.call("/issues/" + str(n))
        if (latest.get("body") != original.get("body")
                or latest.get("assignees") != original.get("assignees")):
            raise RuntimeError("Concurrent live issue change at #" + str(n)
                               + "; changes already applied: " + repr(done))
        api.call("/issues/" + str(n), method="PATCH", data=patch)
        done.append(n)
    return {"mode": "APPLIED_NOT_YET_ACCEPTED", "updated": done}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--owner-approved", action="store_true")
    args = parser.parse_args()
    plan = json.loads((ROOT / ".github/task-plan.json").read_text(encoding="utf-8"))
    if args.apply and not args.owner_approved:
        parser.error("--apply requires explicit --owner-approved")
    if args.apply and (os.environ.get("GITHUB_REPOSITORY") != plan["repository"]):
        parser.error("GITHUB_REPOSITORY must match the reviewed registry")
    result = run(plan, GitHub(), apply=args.apply, approved=args.owner_approved)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
