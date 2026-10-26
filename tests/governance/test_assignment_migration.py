"""Regression tests for safe assignment cleanup after governance activation."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/governance"))
from migrate_assignments import replacement, run

PLAN = json.loads((ROOT / ".github/task-plan.json").read_text(encoding="utf-8"))


class FakeAPI:
    def __init__(self):
        self.issues = {}
        self.writes = []
        for task in PLAN["tasks"]:
            old = "P1" if task["issue_number"] in (19, 20, 31, 32, 33, 34) else task["priority"]
            self.issues[task["issue_number"]] = {
                "state": "open",
                "body": (
                    f"<!-- plan-id: {task['plan_id']} -->\n"
                    "- Primary Owner: @caferkilinc\n"
                    "- Supporting Developer: @ismail-cevik\n"
                    "- Independent Reviewer: @cakarburkayy\n"
                    f"- Priority: {old}\n"
                    "- Preserve legitimate acceptance and objective text.\n"
                ),
                "assignees": [{"login": "caferkilinc"}],
            }

    def call(self, path, method="GET", data=None, **kwargs):
        issue = int(path.split("/")[2])
        if method == "GET":
            return copy.deepcopy(self.issues[issue])
        if method == "PATCH":
            self.writes.append((issue, data))
            self.issues[issue].update(copy.deepcopy(data))
            return copy.deepcopy(self.issues[issue])
        raise AssertionError("Unknown method")


class IssueAssignmentMigrationTests(unittest.TestCase):
    def setUp(self):
        self.api = FakeAPI()

    def test_dry_run_preserves_all_issues_without_writes(self):
        result = run(PLAN, self.api)
        self.assertEqual("DRY_RUN", result["mode"])
        self.assertEqual(31, len(result["planned"]))
        self.assertEqual([], self.api.writes)

    def test_patch_preserves_objective_and_updates_promoted_priority(self):
        task = next(x for x in PLAN["tasks"] if x["issue_number"] == 19)
        patch = replacement(self.api.call("/issues/19"), task, PLAN["team"])
        self.assertIn("Preserve legitimate acceptance", patch["body"])
        self.assertIn("- Priority: P0", patch["body"])
        self.assertNotIn("- Primary Owner:", patch["body"])
        self.assertNotIn("- Supporting Developer:", patch["body"])
        self.assertNotIn("- Independent Reviewer:", patch["body"])
        self.assertEqual([], patch["assignees"])

    def test_unknown_assignee_aborts_without_any_mutation(self):
        self.api.issues[37]["assignees"] = [{"login": "outsider"}]
        with self.assertRaisesRegex(ValueError, "Unrecognized issue assignee"):
            run(PLAN, self.api)
        self.assertEqual([], self.api.writes)

    def test_missing_task_marker_aborts_without_mutation(self):
        self.api.issues[37]["body"] = "incorrect"
        with self.assertRaisesRegex(ValueError, "marker mismatch"):
            run(PLAN, self.api)
        self.assertEqual([], self.api.writes)

    def test_apply_needs_owner_approval_even_when_all_issues_valid(self):
        with self.assertRaisesRegex(ValueError, "owner-approved"):
            run(PLAN, self.api, apply=True, approved=False)
        self.assertEqual([], self.api.writes)

    def test_repeated_dry_run_is_idempotent_after_exact_cleanup(self):
        task = PLAN["tasks"][0]
        issue = self.api.issues[task["issue_number"]]
        issue.update(replacement(issue, task, PLAN["team"]))
        result = run(PLAN, self.api)
        self.assertNotIn(task["issue_number"], result["planned"])
        self.assertEqual([], self.api.writes)


if __name__ == "__main__":
    unittest.main()
