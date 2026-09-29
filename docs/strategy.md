# Growth Strategy

An internal working document. It records what has been tried, what the
measurement was, and what to do next. Updated as things land.

The goal is not stars. It is that someone building a multi-broker trading
system finds these prompts, and a stranger improves one of them.

---

## Where this library sits

Measured against the repos a reader would actually encounter:

| Repo | Stars | What it is |
|---|---|---|
| `awesome-opencode/awesome-opencode` | ~10.4k | The opencode directory. Curated index. |
| `ankitmundada/awesome-opencode-subagents` | ~62 | 100+ opencode subagents |
| `weisser-dev/awesome-opencode` | ~35 | 108 agents, 15 skills, CLI installer |
| `jshsakura/awesome-opencode-skills` | ~28 | 136+ opencode skills |
| `pagesailor/claude-code-prompts` | ~1k | Prompt patterns, studied from Claude Code |

And the large prompt collections, which compete on breadth rather than depth:
`f/prompts.chat` (~140k), `x1xhlol/system-prompts-and-models-of-ai-tools`
(~110k), `dair-ai/Prompt-Engineering-Guide` (~69k).

**The gap.** Two gaps, and they pull in opposite directions.

*The narrow one.* Sixteen of the 45 prompts cover multi-broker trading
systems. No repository in either list holds that ground. Generic prompts
compete with lists two orders of magnitude larger — `api-design.md` alone will
never be found by someone searching for API design. It is only reachable as
part of a coherent whole. That is what the financial prompts are for: they are
the part nobody else has.

*The one that decides the whole strategy.* This library aims at people building
agent tools and coding agents, across many topics. That audience is larger and
better served by breadth than by a vertical wedge, and a library that claims
both has to earn both. A third of the library is one domain; a reader who wants
a Go gRPC prompt is not a trading developer and should not feel like they have
landed in the wrong place.

**The resolution.** Lead with breadth and the agent-tool audience, because
that is who the library is for. Keep the financial prompts as the depth
differentiator rather than the front door, and let them be the proof that the
prompt structure works on genuinely hard problems. Breadth is the claim; the
trading prompts are the evidence.

This reverses an earlier decision. The README previously led with the trading
wedge and the nav led with the financial categories, on the reasoning that a
narrow wedge is easier to be known for. That reasoning was sound for a
single-domain library and wrong for this one — it made a 45-prompt library read
as a 16-prompt one.

---

## The two strategies

They are not alternatives. They run in sequence.

### A. Lead with breadth, earn the depth — mostly done

The positioning decision is made: the README leads with the prompt count and
the agent-tool audience, and the site nav leads with architecture and
application development. The financial prompts sit under Financial
Engineering, near the end, as the differentiator rather than the frame.

Remaining work in this lane:

- [x] README leads with breadth and the agent-tool audience
- [x] Site nav leads with architecture and application, not the financial
      categories
- [x] One-line description carries the count and the audience, not the wedge
- [x] System-prompt framing: how to pick a prompt by mode, and how to compose
      several for multi-area work
- [x] A worked example: one prompt, end to end, in a real repo, with output.
      Now `docs/worked-example.md`, generalised, and ending on a section
      about what the prompt got wrong. The value was never the anti-patterns
      it ends with — it was showing the process, review cutting what the run
      produced included, because an example that shows only successes is not
      believed and teaches nothing
- [x] A verification register: one row per prompt recording whether it has
      been run against a real codebase, generated into a Verified column in
      the index so a reader can see the shape of the evidence without opening
      anything. Thirty-eight of the forty-five rows say no, and that is the finding
      rather than a shortfall in it: the result of the pass is that most of this
      library is still a guess, and the register is where that is stated
- [ ] Broaden the non-trading set. The breadth claim is currently carried by
      the other 29 of 45; the honest way to firm it up is to add more areas,
      not to remove the financial ones.
- [ ] Decide whether this repository's own documents belong on the site, and
      if so, what they cost. `docs/verification.md` is a repository document
      and a reader looking for it in the sidebar will not find it, which is
      the gap the verification pass left open. The site's `docs_dir` is
      `prompts/`, so putting a repo document on it is not a nav entry: the
      file has to exist under `prompts/`, and every script that treats
      `prompts/` as the prompt set then has to be told the difference —
      `check_nav.py`, `generate_index.py`'s on-disk set, and the frontmatter
      loop in `validate.sh`. A copy needs one source of truth removed from
      it; a symlink builds but degrades to a text file on a Windows checkout
      without symlink support, which renders as a broken page. Until this is
      decided the default is off-site, and every repository document inherits
      it, so decide it before the second such document lands rather than after.
- [ ] A short post per topic cluster, written where developers already read:
      r/algotrading and quant finance for the trading prompts, plus the
      engineering and AI-tooling venues for the rest.

### B. Package for the harness — highest reach, largest effort

Right now a prompt is a Markdown file you copy. The repos above beat that
by being installable.

- [ ] Emit `.opencode/agent/*.md` so `git clone` into `~/.config/opencode/`
      makes all 45 available as named subagents
- [ ] Emit the Claude Code and Codex equivalents from the same source, so
      one prompt set serves three harnesses
- [ ] A `Makefile` or `install.sh` that regenerates and installs
- [ ] Declare the source of truth clearly. The generator writes into a
      build directory that is gitignored; `prompts/` stays canonical

This is the difference between a document and a tool, and it is what the
28-to-62 star repos are already attempting. It is also the single highest-leverage
item here: it is the one change that makes the breadth claim true for a reader,
because installation is how you discover what a library contains.

**Order matters.** A. first, because it costs nothing and B is wasted if the
positioning is unclear. B second, because it multiplies whatever A already
achieved. If only one of them gets done, B is the one — packaging serves the
breadth claim, and a repo that cannot be installed is a document no matter how
good the prompts are.

---

## Directory submissions

The single highest-leverage action available. These are the pages people
actually land on.

| Target | Action | Status |
|---|---|---|
| `awesome-opencode/awesome-opencode` | The directory. Has a `contributing.md` and a machine-readable `data/` directory, so there is a defined entry format. ~10.4k stars, actively updated. | Not submitted. Needs the opencode-native form from track B first. |
| `hesreallyhim/awesome-claude-code` | ~23k stars, curated, prunes dead entries. Has a CSV export. | Not submitted. |
| `ComposioHQ/awesome-claude-skills` | ~33k stars, "contribute a new resource, fork then PR". | Not submitted. |
| `f/prompts.chat` | The largest prompt library. Contribution model is stricter. | Worth an attempt once the library has a track record. |
| `Promptslab/Awesome-Prompt-Engineering` | ~4k, academic-adjacent. | Low cost, low value. |

Submit only after the repo is in a state worth submitting to: license,
README, CI green, site live, topics set. All of that is this release.

---

## Repo metadata

GitHub search is the highest-leverage lever and the cheapest to pull.

- [x] Description set, carrying the prompt count and the audience
- [x] Topics set (see below)
- [x] Pages URL set as the repository `homepage`, which is what puts the link
      in the repository header
- [ ] Pin the repo from your profile page. A pinned repo appears in a
      profile's prominent list, which is how star-collectors find projects.
      This is a profile-level action rather than a repository setting, so
      there is no API or CLI route to it

Topics applied: `prompt-engineering`, `opencode`, `claude-code`,
`agentic-ai`, `ai-prompts`, `system-prompts`, `ai-agents`, `coding-agents`,
`developer-tools`, `architecture`, `fintech`, `trading`, `golang`, `aws`,
`devops`, `llm`, `rag`.

The set carries the agent-tooling audience first and the financial cluster
second, matching the README. Topics indexed on `trading` and `fintech` do reach
the vertical audience, which is the point of keeping them, but they should not
outnumber the terms the positioning now leads with.

---

## Community mechanics

**A public roadmap, once there is one to be public.** The mechanism is worth
having: contributor proposes, maintainer implements, contributor is credited.
That is what produces organic pull requests. It needs somewhere to live, and
Discussions was the obvious candidate but was turned off for now, so it
currently runs on issue threads under the `idea` label. Revisit once there
is actual external traffic to serve; a discussion board with three posts in
it reads as an abandoned project, and issues serve the same purpose until
then.

**Adoption reports.** Social proof is what converts a reader into a sharer.
A trading bot screenshot or a benchmark beats any description of the
prompts. Ask the first few people who use one.

**A release cadence.** A tag every few weeks, even for small improvements,
signals maintenance. Staleness is the fastest way to lose a directory
listing.

**Responding fast.** On a public repo, response latency drives contributor
retention more than anything else. A one-line "good idea, PR welcome" is
worth more than a good roadmap.

---

## Content flywheel

The prompts describe a multi-broker trading platform. Building one produces
material the library should absorb.

- [ ] When a new broker or venue is added to the project, write the SDK
      prompt from what was actually painful
- [ ] When a bug teaches you something about order state or reconnect
      semantics, that belongs in the broker prompts
- [ ] Real failure modes are what make the anti-patterns sections worth
      reading. Generic ones are not
- [ ] An event-contracts prompt. The `data-platforms` pass turned up two
      findings that prompt cannot honestly hold: a contract naming a version
      field that no producer writes, so a consumer mid-deploy cannot tell
      which shape it received, and sibling consumers of one stream each
      answering an unparseable record in its own way. Both are message-schema
      properties rather than dataset properties, so both were rejected there
      and neither is published anywhere yet
- [ ] A fails-open default, for `security.md` or `devops.md`. The service-layer
      pass found a configuration value that fell through to the live default
      when unrecognised — the strongest general finding in that pass, and not
      closable by editing the file it was found in
- [ ] `jvm-backend` is the one prompt the verification pass could not move.
      No corpus with a JVM service layer was available to run it against, so
      the register records it as unverified with that reason attached. It is
      listed here rather than left out so it is not mistaken for a prompt
      nobody has got round to yet — it needs a different corpus, not more time

The same loop runs for the rest of the library — 29 of the 45 — against any
codebase worked on rather than the trading one. A prompt that has never been run
against a real repository is a guess, and the `platform-engineering` pass
proved it: running that prompt against real Kubernetes repositories turned up
three anti-patterns it did not previously name. Every prompt here should get
that treatment, and the financial prompts are simply the ones that have had it
most often.

`docs/verification.md` is the current answer to which of them have, for all of
them, and it is written to be argued with rather than trusted. A run that finds
nothing is a row that says so, and so is a run that finds the prompt was wrong
about something it claimed.

This is the honest reason the vertical prompts are better than generic
ones, and it is sustainable only if the loop is closed — which is also the
argument for extending it beyond the vertical.

---

## Explicitly not doing

**Reciprocal star swaps.** Star-for-star arrangements produce a number that
does not represent adoption, and the audience they attract is not the
audience for this library.

**Padding the prompt count with generic material.** Every added
`code-review.md` dilutes the one thing that makes this repository
distinguishable. Depth over count, always.

Note the tension with the breadth decision above, and the resolution: depth
is required, but depth is not the same as narrowness. The bar for a new
prompt is that it encodes something you learned by doing the work, not that it
is in the financial domain. A generic prompt added for count is padding; a
financial prompt written from a real integration is not.

**A Twitter or X launch.** Wrong audience for infrastructure and regulated
trading content.

---

## Measurement

| Metric | Baseline | Check quarterly |
|---|---|---|
| Stars | 0 | Direction, not magnitude |
| Distinct referrers to the site | 0 | Which submissions actually send traffic |
| Pull requests from non-maintainers | 0 | The real health signal |
| Issue threads with external participants | 0 | Is the roadmap working |
| Prompts with a reported real-world use | 0 | The only metric that validates the premise |

Re-evaluate track B's value after two quarters. If the directory submission
has not moved referrers, the packaging work is not paying for itself.
