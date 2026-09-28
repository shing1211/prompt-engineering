#!/usr/bin/env bash
#
# Validate the prompt library. Runs the same checks as CI, locally.
#
#   scripts/validate.sh
#
# Steps:
#   1. frontmatter schema on every prompts/*.md
#   2. generators are idempotent (no drift)
#   3. generated tables in prompts/index.md are current
#   4. no line-ending or whitespace-policy violations
#   5. markdownlint, when available
#   6. internal links resolve, when the site is built
#
# Exits non-zero on the first failure.

set -euo pipefail

cd "$(dirname "$0")/.."

FAILURES=0

step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }
fail() { printf '\033[31mFAIL\033[0m %s\n' "$1"; FAILURES=$((FAILURES + 1)); }
ok()   { printf '\033[32mok\033[0m   %s\n' "$1"; }

# ---------------------------------------------------------------- 1. frontmatter

step "Frontmatter schema"

python3 - <<'PY' || exit 1
import re
import sys
from pathlib import Path

VALID_MODES = {"build", "plan", "review", "all"}
# Site scaffolding, not prompts.
SCAFFOLD = {"index", "tags"}
# index.md is a hand-written landing page; it still carries frontmatter but
# its body is prose, so only its metadata is checked.

REQUIRED = ("title", "description", "mode", "model", "category", "tags")

errors: list[str] = []
checked = 0

for path in sorted(Path("prompts").glob("*.md")):
    if path.stem in SCAFFOLD:
        continue
    checked += 1
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    if lines[0].strip() != "---":
        errors.append(f"{path}: no opening frontmatter fence")
        continue

    ends = [i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---"]
    if not ends:
        errors.append(f"{path}: no closing frontmatter fence")
        continue

    end = ends[0]
    block = lines[1:end]
    meta = {}
    for line in block:
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.strip()

    for field in REQUIRED:
        if field not in meta or not meta[field]:
            errors.append(f"{path}: frontmatter missing or empty '{field}'")

    mode = meta.get("mode", "")
    if mode and mode not in VALID_MODES:
        errors.append(f"{path}: mode '{mode}' not in {sorted(VALID_MODES)}")

    # title must match the H1
    h1 = re.search(r"^# (.+)$", "\n".join(lines[end + 1:]), re.MULTILINE)
    if h1 and meta.get("title") and h1.group(1).strip() != meta["title"].strip():
        errors.append(
            f"{path}: title '{meta['title']}' does not match H1 '{h1.group(1).strip()}'"
        )
    if h1 is None:
        errors.append(f"{path}: no H1 heading")

    # tags must be a non-empty list of lowercase kebab-case
    raw = meta.get("tags", "")
    tags = re.findall(r'"([^"]+)"', raw)
    if not tags:
        errors.append(f"{path}: tags must be a non-empty list")
    for tag in tags:
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", tag):
            errors.append(f"{path}: tag '{tag}' is not lowercase kebab-case")

    # description should be a single line
    desc = meta.get("description", "")
    if desc and desc.endswith("."):
        errors.append(f"{path}: description should not end with a period")

    if end + 1 < len(lines) and lines[end + 1].strip() != "":
        errors.append(f"{path}: no blank line after the closing frontmatter fence")

for error in errors:
    print(f"  {error}")

if errors:
    print(f"\n{len(errors)} frontmatter problem(s) in {checked} prompts", file=sys.stderr)
    sys.exit(1)

print(f"  {checked} prompts conform")
PY

if [ "$FAILURES" -eq 0 ]; then ok "frontmatter schema"; else fail "frontmatter schema"; fi

# ------------------------------------------------------------- 2/3. generators

step "Generators are idempotent"

for script in apply_titles.py apply_categories.py fix_heading_hierarchy.py; do
    before=$(git diff --stat -- prompts | tail -1 || true)
    if ! python3 "scripts/$script" >/dev/null; then
        fail "$script exited non-zero"
        continue
    fi
    after=$(git diff --stat -- prompts | tail -1 || true)
    if [ "$before" != "$after" ]; then
        fail "$script changed files; run it and commit the result"
    else
        ok "$script is idempotent"
    fi
done

step "Generated tables are current"

if python3 scripts/generate_index.py --check; then
    ok "index.md tables are current"
else
    fail "index.md tables are stale; run python3 scripts/generate_index.py"
fi

step "Site navigation"

if python3 scripts/check_nav.py; then
    ok "every prompt is listed in the nav"
else
    fail "nav does not match the files in prompts/"
fi

step "Vendor claims are marked as unverified"

if python3 scripts/check_vendor_claims.py; then
    ok "broker internals are not stated as settled fact"
else
    fail "a broker prompt asserts vendor internals without a verify instruction"
fi

# ------------------------------------------------------ 4. line endings + EOL

step "Line endings and whitespace policy"

crlf=0
# grep exits 1 when it matches nothing, which under `set -e` would abort the
# run before the count is read. The `|| true` keeps a clean file a pass.
crlf=$(grep -rlU $'\r' --include='*.md' --include='*.yml' --include='*.py' . 2>/dev/null | grep -v '^./site/' | wc -l | tr -d ' ') || true
if [ "$crlf" = "0" ]; then
    ok "no CRLF line endings"
else
    fail "$crlf file(s) contain CRLF line endings"
fi

missing_newline=0
for f in $(git ls-files '*.md'); do
    if [ -n "$(tail -c 1 "$f")" ]; then
        printf '      %s has no final newline\n' "$f"
        missing_newline=$((missing_newline + 1))
    fi
done
if [ "$missing_newline" = "0" ]; then
    ok "all Markdown files end with a newline"
else
    fail "$missing_newline file(s) missing a final newline"
fi

# ------------------------------------------------------------- 5. markdownlint

step "Markdown lint"

if command -v markdownlint >/dev/null 2>&1; then
    # shellcheck disable=SC2046
    if markdownlint --config .markdownlint.yaml prompts/*.md *.md 2>&1; then
        ok "markdownlint clean"
    else
        fail "markdownlint reported issues"
    fi
else
    printf 'skip  markdownlint not installed (CI runs it)\n'
fi

# ----------------------------------------------------------------- 6. links

step "Internal links"

if [ -d site ]; then
    if python3 scripts/check_links.py; then
        ok "internal links resolve"
    else
        fail "broken internal links"
    fi
else
    printf 'skip  site/ not built; run mkdocs build to check links\n'
fi

# ------------------------------------------------------------------ summary

printf '\n'
if [ "$FAILURES" -eq 0 ]; then
    printf '\033[32mAll checks passed.\033[0m\n'
    exit 0
fi
printf '\033[31m%s check(s) failed.\033[0m\n' "$FAILURES"
exit 1
