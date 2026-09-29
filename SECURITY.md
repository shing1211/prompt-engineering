# Security Policy

## Scope

This repository holds **prompt text and documentation only**. It contains no
executable code, no dependencies, and no build artifacts that run in your
environment. The `scripts/` directory is Python that operates on the
repository's own Markdown files; the site is built by MkDocs in GitHub
Actions.

That said, a prompt is executable in the sense that matters most here: paste
one into an agent and it will act on your repository with your permissions.
Two classes of report are therefore in scope.

### In scope

**Content safety.** A prompt that would cause an agent to do something
dangerous if followed literally. Examples:

- instructions that disable safety checks, or advise bypassing sandboxing,
  permission prompts, or approval gates
- instructions that exfiltrate code, credentials, or environment variables
- anything that instructs an agent to commit, push, or deploy without
  explicit human approval, in violation of the stated safety rules
- instructions that would place real trades, move money, or mutate production
  data as a side effect of a code task

**Injection.** Content that smuggles instructions past a human reviewer. The
library previously carried 62 `[reference:N]` artifacts from a generation
pass; a similar hidden instruction embedded in a prompt is worth reporting.

**Supply chain.** A workflow, script, or dependency that executes something
other than what it claims. This covers `.github/workflows/`, `scripts/`, and
any pinned version in the Pages build.

### Out of scope

- The security posture of the systems the prompts *describe*. A prompt
  covering IAM or threat modelling is not itself a vulnerability.
- Generated content in a fork you do not control.
- Missing hardening in a user's own project, because they used a prompt here.
- Weaknesses in MkDocs, Material, or Python. Report those upstream.

## Reporting

Report privately through
[GitHub's private vulnerability reporting][report]: on this repository, use
**Security → Report a vulnerability**.

If that page is unavailable, the feature may be disabled. In that case email
the maintainer at the address in the repository's public commits, or open a
discussion in a non-public channel of your choosing. **Do not open a public
issue for a vulnerability** — an issue is visible to everyone immediately,
including before a maintainer has read it.

Include:

- the file and line
- what the prompt instructs, quoted
- what you believe an agent would do as a result
- whether the issue is exploitable by a user who does not already trust the
  maintainer

Expect acknowledgement within 72 hours and a substantive response within seven
days. If a report is declined, you will get a reason.

## What happens next

1. Acknowledged, and the report is treated as confidential.
2. Reproduced against the current `main`.
3. Fixed in a commit that names the finding in the message, with a
   `SECURITY` marker in the message body.
4. The reporter is credited, unless they prefer otherwise.

If a report is already public, the same process applies but without the
confidentiality constraint.

## A note on prompt-triggered risk

Because these files are instructions rather than code, traditional SAST and
dependency scanning will not surface most of what matters in scope above.

Part of it is now automated. `scripts/check_vendor_claims.py` runs in CI and
fails a prompt that states a broker's auth internals, endpoint, or capability
as fact without an instruction to verify it, and fails one that presents a
broker-specific risk threshold as a universal rule. That check exists because
four vendor facts in this library were wrong when first published, and the
check cannot tell you a fact is *still* right — it only catches the pattern of
asserting without provenance.

The judgement about whether a claim is actually correct is still human. If a
prompt you rely on reads as if it would exceed its stated purpose, or states
something specific about a vendor you have reason to doubt, treat it as a
finding and report it.

[report]: https://docs.github.com/en/communities/maintaining-your-safety-on-github/reporting-abuse-or-spam
