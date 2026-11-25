#!/usr/bin/env python3
"""Tests for version_bump_check.py (stdlib only, offline, no git).

    python3 -m unittest plugins/marcketplace/scripts/test_version_bump_check.py
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import version_bump_check as vb  # noqa: E402


def manifest(v):
    return json.dumps({"name": "marcketplace", "version": v})


LOG = "# Changelog\n\n## [Unreleased]\n\n## [1.15.0] - 2026-11-26\n\n## [1.14.0] - 2026-11-10\n"
SKILL = "plugins/marcketplace/skills/proactive-router/references/dispatch.md"


class Evaluate(unittest.TestCase):
    def test_skill_change_without_bump_fails(self):
        ok, msg = vb.evaluate([SKILL], manifest("1.14.0"), manifest("1.14.0"), LOG)
        self.assertFalse(ok)
        self.assertIn("still 1.14.0", msg)

    def test_skill_change_with_bump_and_changelog_passes(self):
        ok, _ = vb.evaluate([SKILL], manifest("1.14.0"), manifest("1.15.0"), LOG)
        self.assertTrue(ok)

    def test_bump_without_changelog_heading_fails(self):
        ok, msg = vb.evaluate([SKILL], manifest("1.15.0"), manifest("1.15.1"), LOG)
        self.assertFalse(ok)
        self.assertIn("## [1.15.1]", msg)

    def test_version_going_down_fails(self):
        ok, _ = vb.evaluate([SKILL], manifest("1.15.0"), manifest("1.14.0"), LOG)
        self.assertFalse(ok)

    def test_non_numeric_head_version_fails(self):
        ok, _ = vb.evaluate([SKILL], manifest("1.14.0"), manifest("next"), LOG)
        self.assertFalse(ok)

    def test_only_exempt_files_pass_without_bump(self):
        changed = [
            "plugins/marcketplace/scripts/test_version_check.py",
            "plugins/marcketplace/hooks/engine.test.ts",
            "plugins/marcketplace/evals/13-one-decide-per-idea.md",
            "plugins/marcketplace/skills/idea-spar/HISTORY.md",
        ]
        ok, _ = vb.evaluate(changed, manifest("1.14.0"), manifest("1.14.0"), LOG)
        self.assertTrue(ok)

    def test_changes_outside_the_plugin_pass_without_bump(self):
        ok, _ = vb.evaluate(["README.md", "ci/validate.yml", "RELEASING.md"],
                            manifest("1.14.0"), manifest("1.14.0"), LOG)
        self.assertTrue(ok)

    def test_scripts_and_hooks_are_behaviour(self):
        for path in ("plugins/marcketplace/scripts/version_check.py",
                     "plugins/marcketplace/hooks/register.ts",
                     "plugins/marcketplace/shared/state-schema.md"):
            self.assertEqual(vb.behaviour_files([path]), [path])

    def test_new_plugin_base_has_no_manifest(self):
        ok, _ = vb.evaluate([SKILL], "", manifest("1.15.0"), LOG)
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
