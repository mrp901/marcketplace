#!/usr/bin/env python3
"""Tests for runtime_refs.py (stdlib only, offline). Builds a throwaway git repo per test.

    python3 -m unittest plugins/marcketplace/scripts/test_runtime_refs.py
"""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runtime_refs as rr  # noqa: E402

ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
SCHEMA = "plugins/marcketplace/shared/profile-schema.md"


def write(root, rel, text):
    path = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


class Fixture(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = os.path.join(tmp.name, "repo")
        self.home = os.path.join(tmp.name, "runtime")
        os.makedirs(self.repo)
        os.makedirs(self.home)
        self.git("init", "-q")

    def git(self, *args):
        subprocess.run(["git", "-C", self.repo, *args], check=True, capture_output=True, env=ENV)

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)

    def build(self):
        """Base: two skills, an env var, two profile keys. Head: one skill, no env var, one key."""
        r = self.repo
        write(r, "plugins/demo/skills/old-skill/SKILL.md", "old\n")
        write(r, "plugins/demo/skills/keeper/SKILL.md", "keep\n")
        write(r, "plugins/demo/scripts/tool.py", "import os\nos.environ.get('DEMO_OLD_FLAG')\n")
        write(r, SCHEMA, "| Key | Notes |\n|---|---|\n| `org.name` | kept |\n| `chat.gone_key` | dropped |\n")
        self.commit("base")
        self.git("tag", "base")
        self.git("rm", "-rq", "plugins/demo/skills/old-skill")
        write(r, "plugins/demo/scripts/tool.py", "import os\n")
        write(r, SCHEMA, "| Key | Notes |\n|---|---|\n| `org.name` | kept |\n")
        self.commit("head")

    def run_cli(self, *extra, paths=None):
        argv = ["--repo", self.repo, "--base", "base", "--head", "HEAD",
                "--paths", *(paths or [self.home]), *extra]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = rr.main(argv)
        return code, out.getvalue()


class Collect(Fixture):
    def test_collects_each_kind(self):
        self.build()
        got = rr.collect(self.repo, "base", "HEAD")
        self.assertEqual(got["skills"], [{"plugin": "demo", "skill": "old-skill"}])
        self.assertEqual(got["profile_keys"], ["chat.gone_key"])
        self.assertEqual(got["env_vars"], ["DEMO_OLD_FLAG"])

    def test_token_boundaries(self):
        rx = rr.token_re("vault-pulse")
        self.assertTrue(rx.search("/marcketplace:vault-pulse profile=x"))
        self.assertTrue(rx.search("if ($h -match 'vault-pulse profile=')"))
        self.assertFalse(rx.search("vault-pulse-extra"))
        self.assertFalse(rr.token_re("pulse").search("vault-pulse"))


class Scan(Fixture):
    def test_hit_and_exit_code(self):
        self.build()
        write(self.home, "scripts/run.ps1", '$p = "/demo:old-skill profile=$r"\nif ($h -match "old-skill") {\n')
        code, out = self.run_cli()
        self.assertEqual(code, 1)
        self.assertIn("run.ps1:1: /demo:old-skill (removed in this diff)", out)
        self.assertIn("run.ps1:2: old-skill (removed in this diff)", out)
        self.assertEqual(out.count("run.ps1:1:"), 1)  # the qualified form wins over the bare one

    def test_env_var_and_key_hits(self):
        self.build()
        write(self.home, "settings.json", '{"env": {"DEMO_OLD_FLAG": "1"}, "k": "chat.gone_key"}\n')
        code, out = self.run_cli()
        self.assertEqual(code, 1)
        self.assertIn("DEMO_OLD_FLAG", out)
        self.assertIn("chat.gone_key", out)

    def test_clean_case_still_summarises(self):
        self.build()
        write(self.home, "scripts/ok.ps1", "keeper and pulse and old-skill-extra\n")
        code, out = self.run_cli()
        self.assertEqual(code, 0)
        self.assertIn("removes 1 skill(s), 1 profile key(s), 1 env var(s)", out)

    def test_skips_binary_and_dot_git(self):
        self.build()
        with open(os.path.join(self.home, "blob.bin"), "wb") as fh:
            fh.write(b"\0old-skill\0")
        write(self.home, ".git/config", "old-skill\n")
        code, out = self.run_cli()
        self.assertEqual(code, 0)
        self.assertIn("scanned 0 file(s)", out)

    def test_extra_appends_and_json(self):
        self.build()
        extra = os.path.join(self.home, "more")
        write(extra, "a.txt", "old-skill\n")
        code, out = self.run_cli("--extra", extra, "--json")
        self.assertEqual(code, 1)
        data = json.loads(out)
        self.assertEqual(data["hits"][0]["name"], "old-skill")
        self.assertEqual(data["collected"]["env_vars"], ["DEMO_OLD_FLAG"])

    def test_missing_path_is_not_an_error(self):
        self.build()
        code, _ = self.run_cli(paths=[os.path.join(self.home, "nope")])
        self.assertEqual(code, 0)


class Errors(Fixture):
    def test_bad_ref_is_exit_2(self):
        self.build()
        with contextlib.redirect_stderr(io.StringIO()):
            code = rr.main(["--repo", self.repo, "--base", "no-such-ref", "--paths", self.home])
        self.assertEqual(code, 2)

    def test_bad_usage_is_exit_2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(rr.main(["--bogus"]), 2)


if __name__ == "__main__":
    unittest.main()
