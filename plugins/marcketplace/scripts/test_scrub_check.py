#!/usr/bin/env python3
"""Tests for scrub_check.py (stdlib only, offline, no credentials).

    python3 -m unittest plugins/marcketplace/scripts/test_scrub_check.py

Each test builds a throwaway tree and a throwaway denylist, runs `main` against them and
reads the exit code and output. Nothing here touches the real denylist or the network.
"""

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrub_check as sc  # noqa: E402

DENYLIST = "FAIL cs fixture-name \\bZorbax\\b\n"


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = os.path.join(self.tmp.name, "repo")
        os.makedirs(self.root)
        self.denylist = os.path.join(self.tmp.name, "deny.txt")
        with open(self.denylist, "w", encoding="utf-8") as f:
            f.write(DENYLIST)
        # Point the default denylist at a path that does not exist, so a missing env var
        # means "none loaded" regardless of the machine running the tests.
        self._saved_default = sc.DEFAULT_DENYLIST
        sc.DEFAULT_DENYLIST = os.path.join(self.tmp.name, "absent.local.txt")
        self.addCleanup(setattr, sc, "DEFAULT_DENYLIST", self._saved_default)
        self._saved_env = os.environ.pop(sc.DENYLIST_ENV, None)
        self.addCleanup(self._restore_env)

    def _restore_env(self):
        os.environ.pop(sc.DENYLIST_ENV, None)
        if self._saved_env is not None:
            os.environ[sc.DENYLIST_ENV] = self._saved_env

    def write(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def run_main(self, argv, denylist=True):
        if denylist:
            os.environ[sc.DENYLIST_ENV] = self.denylist
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = sc.main(argv)
        return code, out.getvalue(), err.getvalue()


class RequireDenylist(Fixture):
    def test_exits_2_when_none_loaded(self):
        self.write("a.md", "clean text\n")
        code, out, err = self.run_main([self.root, "--require-denylist"], denylist=False)
        self.assertEqual(code, 2)
        self.assertIn("--require-denylist", err)
        self.assertIn("none loaded", out)

    def test_without_the_flag_a_missing_denylist_still_scans(self):
        self.write("a.md", "clean text\n")
        code, out, _ = self.run_main([self.root], denylist=False)
        self.assertEqual(code, 0)
        self.assertIn("none loaded", out)

    def test_passes_when_loaded_and_clean(self):
        self.write("a.md", "clean text\n")
        code, out, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 0)
        self.assertIn("1 pattern", out)
        self.assertIn("0 FAIL", out)

    def test_flag_may_come_first(self):
        self.write("a.md", "clean text\n")
        code, _, _ = self.run_main(["--require-denylist", self.root])
        self.assertEqual(code, 0)


class Scope(Fixture):
    def test_denylist_hit_fails(self):
        self.write("a.md", "this mentions Zorbax by name\n")
        code, out, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 1)
        self.assertIn("FAIL", out)
        self.assertIn("fixture-name", out)

    def test_profiles_dir_is_scanned(self):
        self.write("profiles/example.md", "org: Zorbax\n")
        code, out, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 1)
        self.assertIn("profiles", out)

    def test_claude_dir_is_skipped(self):
        self.write(".claude/worktrees/x/a.md", "Zorbax\n")
        code, _, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 0)

    def test_git_and_node_modules_are_skipped(self):
        self.write(".git/config", "Zorbax\n")
        self.write("node_modules/pkg/index.md", "Zorbax\n")
        code, _, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 0)

    def test_local_files_are_skipped(self):
        self.write("profiles/acme.local.md", "Zorbax\n")
        self.write("notes.local.txt", "Zorbax\n")
        code, _, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 0)

    def test_local_denylist_is_skipped_but_example_is_scanned(self):
        self.write("scrub_denylist.local.txt", "Zorbax\n")
        code, _, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 0)
        self.write("scrub_denylist.example.txt", "Zorbax\n")
        code, out, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 1)
        self.assertIn("scrub_denylist.example.txt", out)

    def test_source_dir_is_scanned(self):
        self.write("source/old/SKILL.md", "Zorbax\n")
        code, _, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 1)

    def test_confluence_page_id_shape_warns(self):
        self.write("a.md", "ref confluence:cloud-x/" + "1234567890" + " here\n")
        code, out, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 0)
        self.assertIn("wiki-page-id", out)

    def test_wiki_page_id_shape_warns_but_does_not_fail(self):
        self.write("a.md", "see pages/" + "1234567890" + " for it\n")
        code, out, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 0)
        self.assertIn("WARN", out)
        self.assertIn("wiki-page-id", out)


@unittest.skipUnless(shutil.which("git"), "git not installed")
class GitTracked(Fixture):
    def setUp(self):
        super().setUp()
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)

    def track(self, *rels):
        subprocess.run(["git", "add", "-f", "--"] + list(rels), cwd=self.root, check=True)

    def test_only_tracked_files_are_scanned(self):
        self.write("tracked.md", "Zorbax\n")
        self.write("untracked.md", "Zorbax\n")
        self.track("tracked.md")
        code, out, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 1)
        self.assertIn("tracked.md", out)
        self.assertNotIn("untracked.md", out)

    def test_untracked_leak_does_not_fail_in_a_git_tree(self):
        self.write("ok.md", "fine\n")
        self.write("untracked.md", "Zorbax\n")
        self.track("ok.md")
        code, _, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 0)

    def test_tracked_local_file_fails(self):
        self.write("profiles/acme.local.md", "fine\n")
        self.track("profiles/acme.local.md")
        code, out, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 1)
        self.assertIn("tracked-private-path", out)

    def test_tracked_claude_dir_fails(self):
        self.write(".claude/scratch/x.md", "fine\n")
        self.track(".claude/scratch/x.md")
        code, out, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 1)
        self.assertIn("tracked-private-path", out)

    def test_tracked_example_denylist_is_scanned(self):
        self.write("scrub_denylist.example.txt", "Zorbax\n")
        self.track("scrub_denylist.example.txt")
        code, _, _ = self.run_main([self.root, "--require-denylist"])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
