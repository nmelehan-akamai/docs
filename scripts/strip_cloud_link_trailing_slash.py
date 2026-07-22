#!/usr/bin/env python3
"""Remove the trailing slash from internal `/cloud/` markdown links.

Walks every markdown file under the docs directory and rewrites inline
markdown links whose target starts with `/cloud/`, dropping the slash at the
end of the path:

    [Get Started](/cloud/marketplace-docs/get-started/)
    [Get Started](/cloud/marketplace-docs/get-started)

Links carrying an anchor are handled too, with the slash removed from the
path portion:

    [Configure](/cloud/guides/foo/#configure)
    [Configure](/cloud/guides/foo#configure)

Only markdown link syntax is matched, so bare `/cloud/` strings elsewhere in
the prose (external URLs, file paths) are left alone.

Usage:
    python3 scripts/strip_cloud_link_trailing_slash.py [--dry-run] [--path docs]
"""

import argparse
import os
import re
import sys

# The target of an inline markdown link pointing at /cloud. Confined to a
# single line so an unbalanced paren cannot run the match into later content.
LINK_RE = re.compile(r"(?<=\]\()/cloud[^)\n]*(?=\))")


def strip_slash(match):
    """Drop the trailing slash from the path portion of a link target."""
    target = match.group(0)
    # Split off an anchor or query string, leaving just the path to trim.
    split = re.search(r"[#?]", target)
    if split:
        path, suffix = target[: split.start()], target[split.start() :]
    else:
        path, suffix = target, ""

    return path.rstrip("/") + suffix


def rewrite_file(path, dry_run):
    """Rewrite `path` with trailing slashes stripped. Returns links changed."""
    with open(path, encoding="utf-8") as f:
        content = f.read()

    updated, _ = LINK_RE.subn(strip_slash, content)
    if updated == content:
        return 0

    # subn's count includes untouched matches, so count real differences.
    changes = sum(
        1
        for before, after in zip(LINK_RE.findall(content), LINK_RE.findall(updated))
        if before != after
    )

    if not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)

    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default="docs", help="directory to walk (default: docs)")
    parser.add_argument("--dry-run", action="store_true", help="report files without modifying them")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        sys.exit("No such directory: {}".format(args.path))

    files = 0
    links = 0
    for root, _, names in os.walk(args.path):
        for name in names:
            if not name.endswith(".md"):
                continue
            full = os.path.join(root, name)
            changed = rewrite_file(full, args.dry_run)
            if changed:
                files += 1
                links += changed
                print("{} ({} link{})".format(full, changed, "" if changed == 1 else "s"))

    verb = "would be updated" if args.dry_run else "updated"
    print("\n{} link(s) across {} file(s) {}.".format(links, files, verb))


if __name__ == "__main__":
    main()
