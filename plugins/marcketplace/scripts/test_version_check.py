#!/usr/bin/env python3
"""Tests for version_check.py (stdlib only, offline, no credentials).

    python3 -m unittest plugins/marcketplace/scripts/test_version_check.py

The repo's other tests are TypeScript, for the hooks module (`claude plugin test`); a
SessionStart hook written as a script has none of its own, so this is a plain unittest file
beside the script. Every fetch is a stub: nothing here touches the network.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import version_check as vc  # noqa: E402

LINE = ("marcketplace: this machine runs {x}, main is {y}. "
        "Update the plugin on claude.ai, then restart Claude Code.")


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = os.path.join(self.tmp.name, "plugin")
        os.makedirs(os.path.join(self.root, ".claude-plugin"))
        self.cache = os.path.join(self.tmp.name, "marcketplace", "version-check.json")

    def install(self, version):
        with open(os.path.join(self.root, ".claude-plugin", "plugin.json"), "w", encoding="utf-8") as fh:
            json.dump({"name": "marcketplace", "version": version}, fh)

    def stub(self, answer):
        calls = []

        def fetch():
            calls.append(1)
            return answer

        return fetch, calls


class Versions(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(vc.parse_version("1.12.0"), (1, 12, 0))
        self.assertGreater(vc.parse_version("1.12.0"), vc.parse_version("1.9.1"))  # numeric, not text
        self.assertIsNone(vc.parse_version("main"))
        self.assertIsNone(vc.parse_version(None))

    def test_version_of_a_manifest(self):
        self.assertEqual(vc.version_of('{"name": "x", "version": "1.11.0"}'), "1.11.0")
        self.assertIsNone(vc.version_of("not json"))
        self.assertIsNone(vc.version_of('{"name": "x"}'))
        self.assertIsNone(vc.version_of('{"version": "latest"}'))

    def test_drift_line(self):
        self.assertEqual(vc.drift_line("1.10.4", "1.12.0"), LINE.format(x="1.10.4", y="1.12.0"))
        self.assertIsNone(vc.drift_line("1.12.0", "1.12.0"))
        self.assertIsNone(vc.drift_line("1.13.0", "1.12.0"), "a copy ahead of main is not drift")
        self.assertIsNone(vc.drift_line("1.12.0", None))
        self.assertIsNone(vc.drift_line(None, "1.12.0"))


class Check(Fixture):
    def test_prints_one_line_when_behind(self):
        self.install("1.10.4")
        fetch, _ = self.stub("1.12.0")
        self.assertEqual(vc.run(self.root, self.cache, now=1000, fetch=fetch, env={}),
                         LINE.format(x="1.10.4", y="1.12.0"))

    def test_silent_when_current(self):
        self.install("1.12.0")
        fetch, _ = self.stub("1.12.0")
        self.assertIsNone(vc.run(self.root, self.cache, now=1000, fetch=fetch, env={}))

    def test_cache_holds_for_12_hours_then_refetches(self):
        self.install("1.10.4")
        fetch, calls = self.stub("1.12.0")
        vc.run(self.root, self.cache, now=1000, fetch=fetch, env={})
        vc.run(self.root, self.cache, now=1000 + 12 * 3600 - 1, fetch=fetch, env={})
        self.assertEqual(len(calls), 1)
        vc.run(self.root, self.cache, now=1000 + 12 * 3600, fetch=fetch, env={})
        self.assertEqual(len(calls), 2)

    def test_cached_main_is_compared_with_the_local_version_every_time(self):
        self.install("1.10.4")
        fetch, calls = self.stub("1.12.0")
        vc.run(self.root, self.cache, now=1000, fetch=fetch, env={})
        self.install("1.12.0")  # the user updated and restarted inside the 12 hours
        self.assertIsNone(vc.run(self.root, self.cache, now=2000, fetch=fetch, env={}))
        self.assertEqual(len(calls), 1)

    def test_failed_lookup_is_silent_and_not_retried_for_an_hour(self):
        self.install("1.10.4")
        fetch, calls = self.stub(None)
        self.assertIsNone(vc.run(self.root, self.cache, now=1000, fetch=fetch, env={}))
        self.assertIsNone(vc.run(self.root, self.cache, now=1000 + 3599, fetch=fetch, env={}))
        self.assertEqual(len(calls), 1)
        vc.run(self.root, self.cache, now=1000 + 3600, fetch=fetch, env={})
        self.assertEqual(len(calls), 2)

    def test_a_fetch_that_raises_is_silent(self):
        self.install("1.10.4")

        def boom():
            raise RuntimeError("network down")

        self.assertIsNone(vc.run(self.root, self.cache, now=1000, fetch=boom, env={}))

    def test_unreadable_local_manifest_is_silent(self):
        fetch, calls = self.stub("1.12.0")  # no plugin.json installed
        self.assertIsNone(vc.run(self.root, self.cache, now=1000, fetch=fetch, env={}))
        self.assertEqual(calls, [], "no local version, so no reason to look")

    def test_failure_stamp_is_written_before_the_fetch(self):
        self.install("1.10.4")
        seen = []

        def fetch():
            seen.append(vc.read_cache(self.cache))
            return "1.12.0"

        vc.run(self.root, self.cache, now=1000, fetch=fetch, env={})
        self.assertEqual(seen, [(1000.0, None)], "the stamp is there while the lookup runs")
        self.assertEqual(vc.read_cache(self.cache), (1000.0, "1.12.0"), "and success overwrites it")

    def test_a_lookup_killed_mid_flight_still_backs_off(self):
        self.install("1.10.4")

        def hang_then_die():
            raise SystemExit(1)  # what the hook timeout's kill looks like from here

        with self.assertRaises(SystemExit):
            vc.run(self.root, self.cache, now=1000, fetch=hang_then_die, env={})
        fetch, calls = self.stub("1.12.0")
        self.assertIsNone(vc.run(self.root, self.cache, now=1000 + 60, fetch=fetch, env={}))
        self.assertEqual(calls, [])

    def test_cache_is_keyed_by_repo(self):
        self.install("1.10.4")
        fetch_a, calls_a = self.stub("1.12.0")
        fetch_b, calls_b = self.stub("1.10.4")
        vc.run(self.root, self.cache, now=1000, fetch=fetch_a, env={}, repo="owner/a")
        vc.run(self.root, self.cache, now=1001, fetch=fetch_b, env={}, repo="owner/b")
        self.assertEqual((len(calls_a), len(calls_b)), (1, 1), "another repo is not served from a's entry")
        self.assertEqual(vc.read_cache(self.cache, "owner/a"), (1000.0, "1.12.0"), "and a's entry survives")
        self.assertEqual(vc.read_cache(self.cache, "owner/b"), (1001.0, "1.10.4"))

    def test_corrupt_cache_is_ignored(self):
        self.install("1.10.4")
        os.makedirs(os.path.dirname(self.cache))
        with open(self.cache, "w", encoding="utf-8") as fh:
            fh.write("{not json")
        fetch, calls = self.stub("1.12.0")
        self.assertEqual(vc.run(self.root, self.cache, now=1000, fetch=fetch, env={}),
                         LINE.format(x="1.10.4", y="1.12.0"))
        self.assertEqual(len(calls), 1)

    def test_switches_turn_it_off(self):
        self.install("1.10.4")
        fetch, calls = self.stub("1.12.0")
        for env in ({"MARCKETPLACE_VERSION_CHECK": "0"}, {"MARCKETPLACE_HEADLESS": "1"}):
            self.assertIsNone(vc.run(self.root, self.cache, now=1000, fetch=fetch, env=env))
        self.assertEqual(calls, [])

    def test_unwritable_cache_does_not_break_the_check(self):
        self.install("1.10.4")
        fetch, _ = self.stub("1.12.0")
        blocked = os.path.join(self.tmp.name, "file-not-dir")
        with open(blocked, "w", encoding="utf-8") as fh:
            fh.write("x")
        self.assertEqual(vc.run(self.root, os.path.join(blocked, "c.json"), now=1000, fetch=fetch, env={}),
                         LINE.format(x="1.10.4", y="1.12.0"))


class Emit(unittest.TestCase):
    def test_hook_output_carries_the_line_for_the_user_and_for_claude(self):
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            vc.emit(LINE.format(x="1.10.4", y="1.12.0"))
        out = json.loads(buf.getvalue())
        self.assertEqual(out["systemMessage"], LINE.format(x="1.10.4", y="1.12.0"))
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn("1.10.4", out["hookSpecificOutput"]["additionalContext"])


if __name__ == "__main__":
    unittest.main()
