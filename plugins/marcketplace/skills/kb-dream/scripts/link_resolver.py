#!/usr/bin/env python3
"""Deterministic link resolution for kb-dream's link pass.

Usage:
    link_resolver.py <kb-root> <changed-file> [<changed-file> ...]

For each markdown or wikilink-style link found in the given files, reports one of:
    OK        target basename exists at exactly the linked path
    REPOINT   target basename exists at exactly one OTHER path (unambiguous - safe to act)
    AMBIGUOUS target basename exists at more than one other path (surface, don't guess)
    FORWARD   target basename exists nowhere (leave it - a forward reference)

Degrades gracefully: if <kb-root> is not a local, listable directory (the knowledge base
is a remote connector with no bulk directory listing available to this script), prints one
line saying so and exits 0 rather than failing - the caller falls back to resolving links
one at a time via its `kb: search` / `kb: read` tool calls instead.

stdlib only, no third-party dependencies.
"""

import os
import re
import sys
import urllib.parse

MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+\.md)\)")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")


def index_basenames(root):
    index = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        if os.sep + ".utility" in dirpath or os.sep + ".obsidian" in dirpath:
            continue
        for fn in filenames:
            if fn.lower().endswith(".md"):
                index.setdefault(fn, []).append(os.path.relpath(os.path.join(dirpath, fn), root))
    return index


def resolve_links(path, text, basenames, root):
    results = []
    for _label, target in MD_LINK_RE.findall(text):
        target = target.split("#", 1)[0].strip()
        if not target or target.startswith(("http://", "https://")):
            continue
        target = urllib.parse.unquote(target)
        target_abs = os.path.normpath(os.path.join(os.path.dirname(path), target))
        base = os.path.basename(target)
        results.append(_classify(path, target, base, target_abs, root, basenames))
    for title in WIKILINK_RE.findall(text):
        base = title.strip() + ".md"
        results.append(_classify(path, title, base, None, root, basenames))
    return results


def _classify(path, target, base, target_abs, root, basenames):
    candidates = basenames.get(base, [])
    rel_path = os.path.relpath(path, root)
    if target_abs is not None:
        target_rel = os.path.relpath(target_abs, root)
        if target_rel in candidates:
            return (rel_path, target, "OK", [target_rel])
    others = [c for c in candidates if target_abs is None or os.path.relpath(target_abs, root) != c]
    if not others:
        return (rel_path, target, "FORWARD", [])
    if len(others) == 1:
        return (rel_path, target, "REPOINT", others)
    return (rel_path, target, "AMBIGUOUS", others)


def main(argv):
    if len(argv) < 2:
        print("usage: link_resolver.py <kb-root> <changed-file> [...]", file=sys.stderr)
        return 2
    root = argv[0]
    if not os.path.isdir(root):
        print(f"NO LOCAL LISTING: {root} is not a local directory; resolve manually via kb: search")
        return 0
    basenames = index_basenames(root)
    for path in argv[1:]:
        if not os.path.isfile(path):
            print(f"SKIP: {path} not found locally")
            continue
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        for rel_path, target, status, candidates in resolve_links(path, text, basenames, root):
            line = f"{status}\t{rel_path}\t{target}"
            if candidates:
                line += "\t" + ", ".join(candidates)
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
