# Design Notes: Deferred and Rejected Proposals

This file records proposals that were considered and **not** adopted, with the
reasoning and with what would reopen each one. It exists so that a settled
question is not re-litigated, and so that "no" can be told apart from "not
yet".

It applies the discipline these formats ask of their own documents: a DRF
`alternatives[]` entry carries `conditions_for_reconsideration`, and a
rejection recorded without them is the thing that gets re-argued every six
months.

Entries are added when a proposal is declined, not on a schedule.

---

## Where the current entries came from

All of them come from one feedback round in September 2026: eight DRF decisions
and twenty CRF entities documenting a snow-modelling project, where most of the
context is institutions and third-party software the author does not own. Every
document validated against 0.3.0, so nothing below was a bug report - it was
friction that the canonical corpus, a company documenting its own systems,
never exposed.

Two caveats that bear on how much weight the evidence carries, and which are
themselves part of the reasoning below:

- It is **one author and one project**. Not independent adoption; dogfooding in
  a genuinely different domain.
- The items that turn on *domain fit* rather than internal logic are exactly
  the ones a second non-canonical corpus would settle.

What shipped from that round is in the [changelog](./CHANGELOG.md) under 0.3.1.

---

## Deferred

### An `ownership` axis on CRF entities, and the missing subject

**Asked for:** a transversal `ownership: internal | third_party | external`, or a
boolean `external`, on `organization` and `system`, because `org_type` enumerates
only internal shapes (`company`, `division`, `department`, `team`, `squad`,
`working_group`) and `type: system` reads as a claim of ownership.

**Already possible today:** `attributes` is optional and so is `org_type`, so
nothing forces a false value - an external organization can simply omit it. And
the graph already carries ownership: `owns` / `owned_by` edges express
"Météo-France owns S2M" precisely.

**Why not adopted:** the flag is a shortcut around a hole one level down. CRF has
no notion of a **subject** - no way to say which organization is "us" - so
`owned_by` cannot be read as "not ours" by any consumer. A boolean would paper
over that, and would then leak: if `system` needs it, so eventually do `policy`
(imposed by a regulator), `fact` (produced by someone else), and `capability`.
Adopting it would also commit CRF to growing its ontology attribute by
attribute as each new domain appears, which does not terminate.

**Reopens when:** the prior question is answered - whether CRF is a fixed core
with `x_` as the only escape, or whether domains get profiles/extensions. That
decision determines whether this is a two-field patch or a structural change.
A second non-canonical corpus showing the same need would also reopen it.

**Meanwhile:** `owns` / `owned_by` edges for the relationship, plus an `x_`
field for the flag.

### Plural sources

**Asked for:** `fact.attributes.source_reference` to accept `string | array<string>`,
because evidence is frequently plural and the workaround was concatenating URLs
with `;`.

**Why not adopted now:** arity is only half the problem. In the corpus that one
field carried three different kinds of value - a URL, a system query
(`"GSC API, sc-domain:..."`), and a prose placeholder
(`"pending field verification"`). Accepting an array makes the concatenation
legal without making it interpretable. And the same singular-string assumption
sits in `assumptions[].source`, `interventions[].source`,
`constraints[].source`, and `provenance.source`: fixing one leaves the format
less coherent than it is now. This is also the only item in the round with
consumer-breaking implications, since a widened type breaks readers that assume
a string even though every existing document stays valid.

**Reopens when:** it can be done as one pass over every `source`-shaped field in
both formats, in a minor release, with the question of *what a source is*
settled first - a free string, a typed reference, or a registry of forms.

**Meanwhile:** the entity `description` or an `x_` field. This is stated in the
[CRF specification](./crf/spec/crf-specification.md#provenance).

---

## Rejected

### A `weakest_assumption_confidence` field

Derived data. It would go stale the moment an assumption was edited, and a stale
confidence number is worse than none. Validators compute the comparison when
they run - shipped in 0.3.1 as the advisory
`confidence_rests_on_weakest_assumption`.

Not reopening. What *would* be a real improvement is the missing axis underneath
it: confidence alone does not say whether an assumption is load-bearing. A
`criticality` or `blocking` marker on `assumptions[]`, which would let the
advisory fire only on premises the decision actually depends on, is a legitimate
future proposal - and so is linking `assumptions[]` to the `context_refs[]` that
restate them, since the corpus held the same proposition at confidence 20 as a
CRF fact and 30 as a DRF assumption with nothing able to notice the divergence.

### A `retracted_positions[]` block

Rejected in favour of extending `alternatives[]`. A parallel block duplicates
`decision`, `rationale_against`, and `conditions_for_reconsideration`, and
forces every consumer to read two arrays to enumerate the option space.

### A `was_held: true` boolean instead of a reference

Rejected because a flag cannot say *whose* position it was, and the corpus needs
that distinction: one document retracted the author's own proposal, another
corrected the user's opening premise. `retracted_by` points at an intervention,
and `interventions[].source` already records who raised it, so the link carries
what the boolean cannot at the same cost.

### An enum for `context.constraints[].source`

Rejected, not deferred. Three reasons, in order of weight:

1. The values in the corpus are in Spanish. An enum fixes the vocabulary in
   English, and there is no value-level escape convention in either format -
   `x_` prefixes field *names*, not values. Enumerating would cost a
   non-English adopter either their working language or a mass of extensions.
2. Constraints in scientific, regulatory, and industrial domains do not
   decompose into a fixed set. A decision constrained by atmospheric
   predictability is not usefully filed under `technical`.
3. It is the one change in the round that would invalidate existing documents.

Shipped instead: a documented ten-value **registry** in the
[DRF specification](./drf/spec/drf-specification.md#constraint-sources), with
the field explicitly open and tooling told to treat unknown values as valid.

An advisory that reports *mutually inconsistent* sources within one corpus -
`technical` alongside `tecnico`, say - remains a reasonable future addition, and
is a different thing from constraining the vocabulary.

### Expanding the `interventions[].type` enum

Nobody asked, and the usage data argues against it: across eight documents,
`external_input` appeared five times, `insight` twice, `challenge` once, and
`constraint` not at all. The existing values are already unevenly used; adding
more would not help.

---

## See Also

- [CHANGELOG](./CHANGELOG.md) - what did ship, and why
- [CONTRIBUTING](./CONTRIBUTING.md) - how to propose a change
- [DRF validation rules](./drf/spec/validation-rules.md) - the rules referenced above
