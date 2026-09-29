# Worked example: `backend-services`

One prompt, one run, end to end. It is the process behind the runs recorded in
the [verification register](verification.md), written out in full so a reader
can judge the process rather than take the register's word for it.

The prompt is [`prompts/backend-services.md`](../prompts/backend-services.md),
published in full, so it is not re-excerpted here. What follows is the rest of
the exchange: what the prompt was given, what it produced, what was actually
committed, and what the run got wrong.

## About the corpus, and why every example here is abstract

The codebase this run was made against is private. It is not open source, it is
not described anywhere in this repository, and nothing published here should be
treated as a reference to it.

Every example in this document is therefore generalised: identifiers, file and
directory names, the subject matter of the individual implementations, the
commit under analysis, and every count are all removed. The code is also
described in the abstract rather than in one language's vocabulary — a
contract, an implementation, a package — so that nothing here reads as a
quotation of the tree it came from. What is left is the *shape* of the code,
which is the part that generalises and the only part a reader in a different
codebase can act on.

That is a deliberate constraint, not caution for its own sake. The failure mode
outlives the codebase; the evidence does not help anybody outside it, and a
name that survives into a public file is a pointer rather than a finding. A
public file cannot be unpublished, so the generalisation is what makes it
honest rather than merely careful. The register says which prompts were run;
this document says what happened when one was.

The mechanism is described in [the fingerprint check](../scripts/check_no_fingerprint.py)
and in the register. What it cannot catch is counts and product names, so those
were removed by reading, and that is stated here so the guarantee is not
over-read.

## The input

The prompt was pointed at a private codebase with one question: what does this
prompt miss?

A read-only probe produced a report first, and the report is what the prompt
was then run against. The report is long. This is the part of it that carried
the findings, abridged and generalised — identifiers replaced with
descriptions, counts removed, and the sections that produced nothing omitted
entirely.

```text
Probe report — the integration layer of a private codebase.
Read-only: no build, no test run, no writes to the tree.

Shape: a codebase in which one language, one module, a layer where a single
contract is implemented by many packages, and a test suite that says which
packages satisfy which contract.

1. Is there one shared interface?
   There is a declared contract, and every implementation asserts that it
   satisfies the contract, with the compiler checking the assertion. The
   package comment names a subset of the implementations as the ones that
   implement it, and that subset is smaller than the set that actually does.
   The same name is declared again in a different package, with a different
   method set and different names for the same concepts. A reader searching
   for the contract by name gets several incompatible answers and no way to
   tell which one binds.
   The test suite documents the capabilities separately and says explicitly
   that none of them implies another. Some files carry a comment claiming a
   narrower capability than their own code provides.

2. Where the implementations disagree
   A shared error-kind package exists. Some implementations import it. The
   rest emit formatted strings, so a classification lookup over their errors
   yields one generic kind for every failure, including ones that were
   retryable.
   Among the implementations that did adopt it, how a given failure is
   classified depends on which one saw it. One treats a caller's cancellation
   as a dependency's fault. One matches on substrings anywhere in a message,
   including a bare status code.
   Deadline budgets and reconnect backoff constants are declared per
   implementation, and the values actually in use are inconsistent even where
   they are declared, because each file chooses its own.

3. Is authentication implemented once, or per implementation?
   Per implementation. No credential, session, or auth interface exists at the
   layer at all. Each implementation carries its own acquisition mechanism.
   A search for any refresh or re-login function returns nothing. The only
   trace of a lifecycle is a hook wired to a value that is never populated.
   One implementation is the only place where acquisition is explicit and can
   fail; the rest hide it inside a dependency.

4. Would a new implementation know the contract?
   No. There is no template, no scaffold, no generated skeleton. A new
   implementation is written by copying an existing one, most likely the
   nearest in shape, and inherits its error classification, retry, context
   handling, auth and idempotency behaviour. The existing conformance checks
   constrain what each implementation declares it can do. None of them
   constrains behaviour, and a new implementation that ignores the taxonomy
   passes all of them.
```

The report was abridged, and not only for safety. Whole sections were left out
because nothing in them generalised into an anti-pattern, and the sections that
were kept are shorter than the originals. What survives above is the evidence
for the four anti-patterns in the diff, and nothing else.

## The output

What the run produced: four anti-patterns, offered as additions to the prompt's
existing anti-patterns section. This is the output **as first drafted**, not as
committed. Three of the four carried text a reviewer cut, and one of those cuts
is the single most useful thing this example has to teach, so the drafts are
shown with it.
>
> **❌ Restate the contract in every implementation instead of sharing it.** A
> shared definition is the one place that says what cancellation, error
> classification, and timeout budget mean for an interface; restated per
> implementation, each of those meanings is local to one implementation and
> the drift stays invisible until a caller depends on a difference nobody
> wrote down. It bites hardest at high fan-out — many implementations of one
> contract — where the shared definition is the only thing they hold in common
> beyond the name.
>
> **❌ Adopt a shared error taxonomy in some implementations and let the rest
> fall through to its default.** Every implementation that never joined
> degrades to a single safe-looking classification for all failures, so a
> caller routing on the taxonomy handles the members and silently mishandles
> the rest. Written per implementation rather than shared, the same classifier
> gives one physical failure several classifications, and only a caller can
> reveal that. High fan-out: with few implementations, read them side by side.
>
> **❌ Integrate a dependency whose credentials expire without stating who
> renews them.** Acquisition, refresh, rotation, and expiry are lifecycle
> behaviour, and a contract of method signatures states none of it, so each
> integration invents its own or inherits the nearest one, including the part
> where nothing renews. The omission is invisible until a credential expires in
> production, and a refresh path that exists but never fires reads as covered.
> High fan-out: a lifecycle per integration is affordable only while there are
> few enough to keep in your head.
>
> **❌ Onboard a new integration by copying the nearest existing one.** With no
> contract stating what an implementation owes, its author picks one to copy by
> shape and inherits whatever that one happens to get wrong — error
> classification, retry, timeouts, cancellation — none of it constrained by a
> test. What the system does under failure then becomes a property of which
> file was opened rather than of a decision anyone made. High fan-out, and it
> needs an existing implementation to copy.

That is the run, abridged in length and not in substance. It is not a clean
result, and the next section is what survived of it.

## The diff

The committed change. The prompt already carried a dozen anti-patterns; these
four were appended after the last of them, and nothing existing was edited or
removed. Layer 4 was the only section touched.

```diff
--- a/prompts/backend-services.md
+++ b/prompts/backend-services.md
@@ -103,6 +103,31 @@ Load before acting:
+- ❌ **Restate the contract in every implementation instead of sharing it.** A
+  shared definition is the one place that says what cancellation, error
+  classification, and timeout budget mean for an interface; restated per
+  implementation, each of those meanings is local to one implementation and
+  the drift stays invisible until a caller depends on a difference nobody
+  wrote down. It bites hardest at high fan-out — many implementations of one
+  contract — where the shared definition is the only thing they hold in common
+  beyond the name.
+- ❌ **Adopt a shared error taxonomy in some implementations and let the rest
+  fall through to its default.** Every implementation that never joined
+  degrades to a single safe-looking classification for all failures, so a
+  caller routing on the taxonomy handles the members and silently mishandles
+  the rest. High fan-out: with few implementations, read them side by side.
+- ❌ **Integrate a dependency whose credentials expire without stating who
+  renews them.** Acquisition, refresh, rotation, and expiry are lifecycle
+  behaviour, and a contract of method signatures states none of it, so each
+  integration invents its own or inherits the nearest one, including the part
+  where nothing renews. The omission is invisible until a credential expires in
+  production, and a refresh path that exists but never fires reads as covered.
+- ❌ **Onboard a new integration by copying the nearest existing one.** With no
+  contract stating what an implementation owes, its author picks one to copy by
+  shape and inherits whatever that one happens to get wrong, none of it
+  constrained by a test. What the system does under failure then becomes a
+  property of which file was opened rather than of a decision anyone made. High
+  fan-out, and it needs an existing implementation to copy.
```

Comparing the two sections is the whole point. Three of the four differ, and
each differs for its own reason: the second lost a sentence, the third lost its
scope clause, and the fourth lost a list from inside a sentence and was
otherwise untouched. The count of anti-patterns is unchanged, because a
sentence is not a bullet. The committed text is the draft with the review
applied — which is what any reader should assume about every entry in this
library, including the ones that survived unchanged.

## What the prompt got wrong

A worked example that shows only successes teaches nothing, and a reader who
believes it has been shown a success is a reader who will not notice the next
one. This is the section that makes the other three worth reading.

### It named the symptoms and missed the layer above them

The prompt already told a reader about duplicated retry loops, missing timeouts
and error taxonomies that do not match. All three were in the codebase. None of
them is a defect in a file — each is what you get when a shared definition is
written out again by hand, somewhere else, every time. The prompt's framing is
per-component, so a reader following it carefully fixes the loops and leaves
the cause in place, and the next implementation puts it back.

That is the finding the run actually produced: not four new anti-patterns, but
one design decision behind the three the prompt already named. It is the kind
of thing only a run can surface, and the prompt now says it, but it is worth
naming that the prompt was not wrong. It was incomplete at the layer above the
one it was written at.

### The guardrails would not have caught it either

Worse, a reader could follow this prompt exactly and still build the thing the
run found. Its guardrails ask for verification and for unverified assumptions to
be recorded. Neither asks where a shared definition lives, so nothing in the
prompt turns "nobody shares the contract" into a failure.

The fix is one guardrail in the guardrails section, stating that before the
first implementation is written the shared definition has to exist and the rest
have to import it. This pass did not add it — the work was scoped to the
anti-patterns section — so the gap is still open, and it is recorded as one
rather than left for a reader to discover.

### A caveat that told the smallest reader to skip the entry meant for them

The credential entry, as drafted, ended with a scope clause: *High fan-out: a
lifecycle per integration is affordable only while there are few enough to keep
in your head.* Cut in review, and it is the most instructive failure here.

The clause was a rationalisation, not a property. Unmodelled credential expiry
is as true of a small fleet as of a large one, because every integration
invents its own refresh whatever the size of the fleet. What the clause did
was tell a reader with a small fleet — which is most readers of this prompt —
that the one entry that applies to them unconditionally does not describe
them. A conditional warning is valuable; a conditional warning that is false is
worse than none, because it sounds like a considered limit and gets believed.

The other fan-out clauses stayed, because they are genuinely true: restating
a contract by hand costs nothing when there is one place to restate it, and
copying an implementation needs an implementation to copy. The distinction is
not "some caveats are fine", it is *is this clause true, and for whom*.

### Two entries argued one point between them

The taxonomy entry was drafted with two failure modes: implementations that
never joined the shared taxonomy, and implementations that each wrote their own
classifier so one physical failure gets several classifications. The second
restates the first entry's mechanism — written per implementation rather than
shared — inside the one entry whose distinct mechanism is membership. Cut,
which is the "second lost a sentence" diff above seen close up.

That is not a wrong answer; it is the ordinary failure of a run that has more to
say than slots to say it in, and it is caught by a reader, not by a tool.

### A safety claim that was checked by assumption, and was wrong

The run reported that it had checked the published file for corpus fingerprints
and found none. That is true. What it also claimed — that the check could not
have missed a name the library does not already publish, so its silence was
proof that nothing had leaked — was false. Reading the checker's source rather
than its imports showed the coverage is partial by construction: the vocabulary
is the set of venue names this library already publishes, because naming a
venue in order to forbid it would publish the name, so anything outside that
set passes silently. The library publishing a prompt about a venue does not
put that venue in the vocabulary.

Nothing leaked. The claim was still wrong, and it was corrected in place rather
than appended to, because a wrong safety claim left in a report is a claim
someone will rely on next time. The generalisable lesson: when a run says its
own safety net has a gap, that gap has to be read out of the net's source. The
gap was the interesting part and it was nearly asserted rather than found.

### The leak was in the commit message, not the file

The file was clean. The commit message was not. It described running the prompt
against a named layer of a production codebase, and a layer in someone's tree
is a directory layout, not a shape. One clause, in the one place nobody thinks
to look because the diff is right there being reviewed.

The message is not quoted here, and the reason is the point: quoting it would
put the name back into a public file, which is the exact thing the rewrite
existed to prevent. A lesson about not publishing a name is not a licence to
publish it once more inside the sentence explaining why.

The message was rewritten to describe the shape of the code rather than where
the code lives, and the branch was unpushed, so the history was amended rather
than followed by a correction. That is the whole reason the constraint is
executable rather than a promise: the fingerprint is as easy to write in
prose about the work as in the work itself.

### The two best findings did not fit the prompt at all

The strongest material in the probe report was not about contracts or
boundaries. It was a configuration value that, when unrecognised, fell through
to the production default instead of failing — the strongest general finding in
the report — and a check that could not fail being read as coverage. Both
generalise. Neither belongs in a prompt about service boundaries.

They were rejected on scope, and the rejection was correct: a prompt written
from experience does not get better by absorbing a finding that is not about
its subject. But they had nowhere to go, because no prompt in the library owns
them, so the honest outcome of the run is two findings that exist only as
follow-up items. A verification pass that only reports what fits the prompt
under test is reporting on the prompt, not on the run, and a reader who sees
four tidy anti-patterns should know that two of the best things found are not
in them.

### No test was added, and that is the finding

The library's own check for this prompt passes before and after the change,
because it asserts that an anti-patterns section exists and carries enough
entries — not that anything in it improved. It would have passed on a worse
prompt and it passes on a better one.

No test was written claiming the new anti-patterns are better, because such a
test would pass without proving anything, and a green check that cannot fail is
worse than no check: it reports safety that is not there. What actually holds
this change together is the fingerprint check, which catches names, paths and
commits and provably does not catch counts or product names, plus a human
reading every added line. Half the assurance came from the gate and half from
the reading, and the reading is the half no test in this repository can
replace.

None of this is institutionalisation, and none of it should be read as a
process yet. A register, a worked example and a gate are three things somebody
has to remember to do; a process is what happens when nobody has to. The
useful claim is only that the practice has started, and that the register will
say so honestly for as long as thirty-nine of the forty-two prompts have not
been run.
