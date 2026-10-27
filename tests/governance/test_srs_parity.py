"""Check reviewed bilingual SRS identity/priority parity without asserting final approval."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIREMENT = re.compile(r"^\|\s*((?:FR-\d{3})|(?:NFR-\d{2}))\s*\|\s*(P[01])\s*\|", re.MULTILINE)


class BilingualRequirementsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.turkish = (ROOT / "docs/SRS.md").read_text(encoding="utf-8")
        cls.english = (ROOT / "docs/SRS_EN.md").read_text(encoding="utf-8")
        cls.plan = json.loads((ROOT / ".github/task-plan.json").read_text(encoding="utf-8"))

    def test_bilingual_requirement_identity_and_priority(self):
        tr, en = [dict(REQUIREMENT.findall(s)) for s in (self.turkish, self.english)]
        self.assertEqual(len(tr), 79)
        self.assertEqual(len(en), 79)
        self.assertEqual(tr, en)
        self.assertEqual(set(tr), {
            *(f"FR-{i:03d}" for i in range(1, 63)),
            *(f"NFR-{i:02d}" for i in range(1, 18)),
        })
        self.assertTrue(all(priority == "P0" for priority in tr.values()))

    def test_owner_promoted_mandatory_milestones(self):
        tasks = self.plan["tasks"]
        self.assertEqual(34, len(tasks))
        self.assertEqual(69, sum(len(t["dependencies"]) for t in tasks))
        for issue in (19, 20, 31, 32, 33, 34, 40, 41, 42):
            task = next(t for t in tasks if t["issue_number"] == issue)
            self.assertEqual("P0", task["priority"], issue)

    def test_new_scope_preserves_original_graph_and_blocks_release_without_adapters(self):
        plan = {t["plan_id"]: t for t in self.plan["tasks"]}
        ids = {"F14-CS": 40, "F14-GO": 41, "F14-CPP": 42}
        for task_id, issue_number in ids.items():
            self.assertEqual(issue_number, plan[task_id]["issue_number"])
            self.assertEqual("P0", plan[task_id]["priority"])
            self.assertEqual(
                ["F02-CONTRACT", "F06-SANDBOX", "F11-VALIDATE"],
                plan[task_id]["dependencies"],
            )
        self.assertEqual(
            {"F14-PY", "F14-JSTS", *ids},
            set(plan["F14-MIX"]["dependencies"]),
        )
        self.assertTrue(
            {"F14-MIX", "F07B-LOCAL", "F13-ADV"} <= set(plan["F15-P0"]["dependencies"]),
        )
        old_tasks = [t for t in self.plan["tasks"] if t["issue_number"] <= 37]
        self.assertEqual(31, len(old_tasks))
        old_ids = {t["plan_id"] for t in old_tasks}
        original_to_original = sum(
            sum(dep in old_ids for dep in t["dependencies"]) for t in old_tasks
        )
        # In addition to preserving the original 54 edges, F15-P0 acquires
        # three new dependencies on existing tasks for complete first delivery.
        release_added = {"F13-ADV", "F07B-LOCAL", "F14-MIX"}
        self.assertTrue(release_added <= set(plan["F15-P0"]["dependencies"]))
        self.assertEqual(54, original_to_original - len(release_added))
        self.assertEqual("PENDING_SAFE_SYNC", self.plan["scope_decision_2026_10_27"]["graph_sync_status"])

    def test_no_immutable_person_assignments_in_technical_registry(self):
        for task in self.plan["tasks"]:
            self.assertFalse({"owner", "support", "reviewer"} & set(task),
                             task["plan_id"])
        state = self.plan["sequential_execution"]
        self.assertEqual(
            ["cakarburkayy", "caferkilinc", "Yaman-A-E", "ismail-cevik", "tahaugurtoyran"],
            state["team_sequence"],
        )
        self.assertEqual("cakarburkayy", state["active_owner"])
        self.assertFalse(state["handoff_confirmed"])


if __name__ == "__main__":
    unittest.main()
