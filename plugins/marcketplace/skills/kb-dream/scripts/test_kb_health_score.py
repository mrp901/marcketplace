import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("kb_health_score.py")

METRICS = {
    "freshness": {"sessions": {"measured": True, "days_ago": 2}},
    "learning": {
        "memory": {"measured": True, "stuck_at_none": 0, "repeat_candidates": []},
        "ledger": {"measured": True, "unmarked_over_window": 0, "items": 3},
    },
}


def score(payload):
    p = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(payload),
                       capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout)


class CarryForward(unittest.TestCase):
    def test_unadjudicated_repeats_keep_the_prior_value(self):
        rc, out = score({"metrics": METRICS, "prior": {"learning.confirmed_repeats": 1}})
        self.assertEqual(rc, 0)
        self.assertEqual(out["values"]["learning.confirmed_repeats"], 1)
        self.assertEqual(out["carried"], ["learning.confirmed_repeats"])
        self.assertNotIn("learning.confirmed_repeats", out["signals"], "carried, not graded")

    def test_adjudicated_repeats_replace_the_prior(self):
        rc, out = score({"metrics": METRICS, "confirmed_repeats": 0,
                         "prior": {"learning.confirmed_repeats": 1}})
        self.assertEqual(out["values"]["learning.confirmed_repeats"], 0)
        self.assertEqual(out["carried"], [])

    def test_a_carried_value_expires_after_30_days(self):
        rc, out = score({"metrics": METRICS, "now": "2026-11-09T10:00:00",
                         "prior": {"learning.confirmed_repeats": 1},
                         "prior_at": {"learning.confirmed_repeats": "2026-09-01T10:00:00"}})
        self.assertNotIn("learning.confirmed_repeats", out["values"])
        rc, out = score({"metrics": METRICS, "now": "2026-11-09T10:00:00",
                         "prior": {"learning.confirmed_repeats": 1},
                         "prior_at": {"learning.confirmed_repeats": "2026-10-20T10:00:00"}})
        self.assertEqual(out["values_at"]["learning.confirmed_repeats"], "2026-10-20T10:00:00",
                         "a carried value keeps its own date")

    def test_no_prior_means_nothing_to_carry(self):
        rc, out = score({"metrics": METRICS})
        self.assertNotIn("learning.confirmed_repeats", out["values"])
        self.assertEqual(out["carried"], [])

    def test_carried_value_does_not_move_the_overall_tag(self):
        rc, out = score({"metrics": METRICS, "prior": {"learning.confirmed_repeats": 9}})
        self.assertNotEqual(out["overall"]["tag"], "red")


if __name__ == "__main__":
    unittest.main()
