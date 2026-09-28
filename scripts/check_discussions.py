#!/usr/bin/env python3
"""Check the repository's discussion categories against the intended set.

GitHub seeds a new Discussions board with six generic categories. This
library wants eight: the six retuned in place, plus Prompt Requests and
Adoption Reports.

There is no public API to create, rename, or delete a discussion category.
`createDiscussionCategory` and `updateDiscussionCategory` do not exist on the
GraphQL Mutation type, and there is no REST endpoint. Category changes have
to be made in the web UI at:

    https://github.com/shing1211/prompt-engineering/discussions/settings

So this script does not apply anything. It reports the current state against
the intended state, prints the exact manual steps, and exits non-zero on
drift so the check can be run periodically or in CI.

    python3 scripts/check_discussions.py
"""

from __future__ import annotations

import json
import subprocess
import sys

OWNER = "shing1211"
REPO = "prompt-engineering"

SETTINGS_URL = (
    f"https://github.com/{OWNER}/{REPO}/discussions/settings"
)

# slug -> (intended name, intended description, emoji)
INTENDED = {
    "announcements": (
        "Announcements",
        "Releases, notable additions, and changes to the frontmatter contract.",
        ":mega:",
    ),
    "q-a": (
        "Q&A",
        "How to use or adapt an existing prompt. Mark the reply that solved it.",
        ":pray:",
    ),
    "ideas": (
        "Ideas",
        "Suggestions about the library: generators, search, opencode packaging.",
        ":bulb:",
    ),
    "general": (
        "General",
        "Anything that fits nowhere else.",
        ":speech_balloon:",
    ),
    "polls": (
        "Polls",
        "Vote on roadmap priorities.",
        ":ballot_box:",
    ),
    "show-and-tell": (
        "Show and tell",
        "What you built with these prompts.",
        ":raised_hands:",
    ),
    "prompt-requests": (
        "Prompt Requests",
        "Propose a prompt that does not exist yet. Agree on scope before writing.",
        ":memo:",
    ),
    "adoption-reports": (
        "Adoption Reports",
        "How you wired a prompt in, and what happened.",
        ":bar_chart:",
    ),
}

# Categories to create, as (name, description, emoji).
TO_CREATE = [
    ("Prompt Requests", "Propose a prompt that does not exist yet. Agree on scope before writing.", ":memo:"),
    ("Adoption Reports", "How you wired a prompt into your workflow, and what happened.", ":bar_chart:"),
]

QUERY = """
query {
  repository(owner: "%s", name: "%s") {
    discussionCategories(first: 50) {
      nodes { slug name description }
    }
  }
}
""" % (OWNER, REPO)


def fetch() -> list[dict[str, str]]:
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        sys.exit(f"error: gh api graphql failed\n{result.stderr.strip()}")
    payload = json.loads(result.stdout)
    return payload["data"]["repository"]["discussionCategories"]["nodes"]


def main() -> int:
    nodes = fetch()
    by_slug = {n["slug"]: n for n in nodes}
    print(f"repository has {len(nodes)} discussion categories\n")

    drift = False

    for slug, (name, description, emoji) in INTENDED.items():
        node = by_slug.get(slug)
        if node is None:
            drift = True
            print(f"  [ ] {name:<18} not present, needs creating")
            continue

        problems = []
        if node["name"] != name:
            problems.append(f"name is {node['name']!r}, want {name!r}")
        if (node.get("description") or "").strip() != description:
            problems.append(
                f"description is {node.get('description')!r}, want {description!r}"
            )

        if problems:
            drift = True
            print(f"  [ ] {name:<18} " + "; ".join(problems))
        else:
            print(f"  [x] {node['name']:<18} name and description correct")

    extra = [n for n in nodes if n["slug"] not in INTENDED]
    if extra:
        drift = True
        print("\n  unexpected categories present:")
        for n in extra:
            print(f"    - {n['name']} (delete or adopt)")

    if drift:
        print("\nCategories must be edited in the web UI; no public API exists.")
        print(f"  {SETTINGS_URL}\n")
        print("Create these, in order:")
        for name, description, emoji in TO_CREATE:
            print(f"  + {name}")
            print(f"      emoji:      {emoji}")
            print(f"      description: {description}")
        print("\nThen set the name, description, and emoji on each of these:")
        for slug, (name, description, emoji) in INTENDED.items():
            node = by_slug.get(slug)
            if node is None:
                continue
            if node["name"] == name and (node.get("description") or "").strip() == description:
                continue
            print(f"  ~ {node['name']}  ->  {name}")
            print(f"      emoji:       {emoji}")
            print(f"      description: {description}")
        print("\nDelete any category not listed above, unless there is a reason to keep it.")
        return 1

    print("\nAll discussion categories match the intended set.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
