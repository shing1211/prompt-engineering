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

**The gap.** Sixteen of the 42 prompts here cover multi-broker trading
systems. No repository in either list holds that ground. That is the asset.

**The ceiling.** Generic prompts compete with lists that are two orders of
magnitude larger. `api-design.md` on its own will never be found by someone
searching for API design. It is only reachable as part of a coherent
whole.

---

## The two strategies

They are not alternatives. They run in sequence.

### A. Own the vertical — do this first, it is already mostly done

The positioning decision is made: the README leads with financial trading,
not with the prompt count. The site nav leads with the financial categories.

Remaining work in this lane:

- [x] README leads with the wedge
- [x] Site nav puts the financial domain first
- [x] One-line description carries the vertical, not the generic noun
- [ ] A worked example: one prompt, end to end, in a real repo, with output.
      This is the highest-value single artifact still missing. A reader who
      sees it work has a reason to believe the other 37 work.
- [ ] A short post per vertical cluster, written where trading developers
      already read. The audience is small and reachable: r/algotrading,
      quant finance communities, Hummingbot and Freqtrade Discord, fintech
      engineering blogs.

Expect a few hundred stars, from the right people. That is the goal.

### B. Package for the harness — highest reach, largest effort

Right now a prompt is a Markdown file you copy. The repos above beat that
by being installable.

- [ ] Emit `.opencode/agent/*.md` so `git clone` into `~/.config/opencode/`
      makes all 38 available as named subagents
- [ ] Emit the Claude Code and Codex equivalents from the same source, so
      one prompt set serves three harnesses
- [ ] A `Makefile` or `install.sh` that regenerates and installs
- [ ] Declare the source of truth clearly. The generator writes into a
      build directory that is gitignored; `prompts/` stays canonical

This is the difference between a document and a tool, and it is what the
28-to-62 star repos are already attempting. Doing it properly, with the
trading wedge, is the actual play.

**Order matters.** A. first, because it costs nothing and B is wasted if the
positioning is unclear. B second, because it multiplies whatever A already
achieved.

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

- [x] Description set, carrying the vertical
- [x] Topics set (see below)
- [x] Pages URL set as the repository `homepage`, which is what puts the link
      in the repository header
- [ ] Pin the repo from your profile page. A pinned repo appears in a
      profile's prominent list, which is how star-collectors find projects.
      This is a profile-level action rather than a repository setting, so
      there is no API or CLI route to it

Topics applied: `prompt-engineering`, `opencode`, `claude-code`,
`agentic-ai`, `ai-prompts`, `system-prompts`, `fintech`, `trading`,
`quant`, `golang`, `aws`, `devops`, `llm`, `rag`, `code-generation`.

Adding a topic later is trivial; adding all of them now is better, because
topic indexing takes time to settle.

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

This is the honest reason the vertical prompts are better than generic
ones, and it is sustainable only if the loop is closed.

---

## Explicitly not doing

**Reciprocal star swaps.** Star-for-star arrangements produce a number that
does not represent adoption, and the audience they attract is not the
audience for this library.

**Padding the prompt count with generic material.** Every added
`code-review.md` dilutes the one thing that makes this repository
distinguishable. Depth over count, always.

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
