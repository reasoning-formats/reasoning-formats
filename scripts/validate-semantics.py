#!/usr/bin/env python3
"""Check the semantic rules in drf/spec/validation-rules.md across all examples.

JSON Schema validates the shape of a single document. These are the rules it
cannot express: cross-document reference integrity, temporal ordering, identifier
uniqueness, acyclicity, and the advisory DRF-to-CRF consistency checks.

Rule identifiers below match the RULE names in drf/spec/validation-rules.md.

Severity follows the table in that document:

    ERROR     document is invalid                  -> always fails the run
    WARNING   valid but problematic                -> fails only with --strict
    ADVISORY  best-practice recommendation         -> reported, never fails

Usage:
    python3 scripts/validate-semantics.py [--strict] [--quiet]

Requires the pinned tooling dependencies:
    pip install -r requirements-dev.txt
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import iter_example_docs, pick_kind  # noqa: E402

ERROR, WARNING, ADVISORY = "ERROR", "WARNING", "ADVISORY"

INVERSE = {
    "owns": "owned_by", "owned_by": "owns",
    "depends_on": "dependency_of", "dependency_of": "depends_on",
    "constrains": "constrained_by", "constrained_by": "constrains",
    "invalidates": "invalidated_by", "invalidated_by": "invalidates",
    "part_of": "contains", "contains": "part_of",
    "produces": "produced_by", "produced_by": "produces",
    "related_to": "related_to",
}

DECISION_SOURCE = re.compile(r"^decision:([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$")


class Report:
    def __init__(self):
        self.findings = []

    def add(self, severity, rule, where, message):
        self.findings.append((severity, rule, str(where), message))

    def count(self, severity):
        return sum(1 for f in self.findings if f[0] == severity)


def ts(value):
    """Parse an RFC 3339 timestamp into an aware datetime, or None."""
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def load_corpus():
    drf, crf = [], []
    for rel, index, doc in iter_example_docs():
        where = f"{rel}" if index == 0 else f"{rel} [doc {index}]"
        kind = pick_kind(doc)
        if kind == "drf":
            drf.append((where, doc))
        elif kind == "crf":
            crf.append((where, doc))
    return drf, crf


def check_uniqueness(rep, drf, crf):
    """RULE: unique_decision_id, unique_intervention_ids (section 10)."""
    by_id = defaultdict(list)
    for where, doc in drf:
        by_id[doc["decision"]["id"]].append(where)
    for uuid_value, places in by_id.items():
        if len(places) > 1:
            rep.add(ERROR, "unique_decision_id", ", ".join(places),
                    f"decision.id {uuid_value} is reused across {len(places)} documents")

    by_entity = defaultdict(list)
    for where, doc in crf:
        by_entity[doc["entity"]["id"]].append(where)
    for uuid_value, places in by_entity.items():
        if len(places) > 1:
            rep.add(ERROR, "unique_entity_id", ", ".join(places),
                    f"entity.id {uuid_value} is reused across {len(places)} documents")

    for where, doc in drf:
        seen = defaultdict(int)
        for item in doc.get("interventions", []):
            seen[item["id"]] += 1
        for key, count in seen.items():
            if count > 1:
                rep.add(ERROR, "unique_intervention_ids", where,
                        f"intervention id {key!r} appears {count} times in one document")


def check_temporal(rep, drf, crf, now):
    """RULE: created_before_updated, intervention_timestamps_ordered (section 8)."""
    for where, doc in drf:
        meta = doc["meta"]
        created, updated = ts(meta.get("created_at")), ts(meta.get("updated_at"))
        if created and updated and updated < created:
            rep.add(ERROR, "created_before_updated", where,
                    f"meta.updated_at ({meta['updated_at']}) is before meta.created_at ({meta['created_at']})")

        stamps = [ts(i.get("timestamp")) for i in doc.get("interventions", [])]
        known = [s for s in stamps if s]
        if known != sorted(known):
            rep.add(ADVISORY, "intervention_timestamps_ordered", where,
                    "interventions are not in chronological order")

        validated_at = ts((doc.get("context_validation") or {}).get("validated_at"))
        if validated_at and created and validated_at < created:
            rep.add(WARNING, "validated_at_consistency", where,
                    "context_validation.validated_at precedes meta.created_at")

    for where, doc in crf:
        entity = doc["entity"]
        validity = entity.get("validity") or {}
        start, end = ts(validity.get("valid_from")), ts(validity.get("valid_until"))
        if start and end and end <= start:
            rep.add(ERROR, "validity_window_ordered", where,
                    f"validity.valid_until ({validity['valid_until']}) is not after valid_from ({validity['valid_from']})")

        prov = entity["provenance"]
        created, updated = ts(prov.get("created_at")), ts(prov.get("updated_at"))
        if created and updated and updated < created:
            rep.add(ERROR, "created_before_updated", where,
                    "provenance.updated_at is before provenance.created_at")


def check_context_refs(rep, drf, crf, now):
    """RULE: context_ref_type_match, context_temporal_validity, approved_with_violations (section 11).

    `now` is used only for the forward-looking `context_since_expired` advisory;
    the WARNING-level staleness check is anchored to validated_at instead, so
    that results do not change as wall-clock time passes.
    """
    entities = {doc["entity"]["id"]: (where, doc["entity"]) for where, doc in crf}

    for where, doc in drf:
        cv = doc.get("context_validation") or {}
        for ref in cv.get("context_refs", []):
            target = entities.get(ref["context_id"])
            if target is None:
                rep.add(WARNING, "context_ref_resolves", where,
                        f"context_id {ref['context_id']} ({ref.get('context_name', '?')}) "
                        "is not an entity in this corpus")
                continue

            _, entity = target
            if entity["type"] != ref["context_type"]:
                rep.add(WARNING, "context_ref_type_match", where,
                        f"context_type declared {ref['context_type']!r} but entity "
                        f"{ref['context_id']} is {entity['type']!r}")

            end = ts((entity.get("validity") or {}).get("valid_until"))
            if end:
                # Expiry is judged against the moment the validation was performed,
                # not against today. A 2024 decision validated against a policy that
                # ran to mid-2024 was correct then and stays correct forever; only a
                # validation performed after the expiry is actually stale.
                as_of = (ts(cv.get("validated_at"))
                         or ts(doc["meta"].get("updated_at"))
                         or ts(doc["meta"].get("created_at")))
                if as_of and end < as_of:
                    rep.add(WARNING, "context_temporal_validity", where,
                            f"validated against {entity['name']!r} on {as_of.date()}, "
                            f"after it expired on {entity['validity']['valid_until']}")
                elif end < now and doc["meta"]["status"] in {"approved", "draft", "review"}:
                    rep.add(ADVISORY, "context_since_expired", where,
                            f"{entity['name']!r} expired on {entity['validity']['valid_until']}, "
                            "after this decision was validated; consider revalidating")

            if ref["validation_status"] == "violated" and not ref.get("advisory_notes"):
                rep.add(ADVISORY, "violated_requires_notes", where,
                        f"violated reference to {ref.get('context_name', ref['context_id'])} has no advisory_notes")

        if doc["meta"]["status"] == "approved":
            for ref in cv.get("context_refs", []):
                if ref["validation_status"] == "violated":
                    rep.add(WARNING, "approved_with_violations", where,
                            f"approved decision still marks {ref.get('context_name', ref['context_id'])!r} "
                            "as 'violated'; an accepted exception belongs in 'acknowledged'")


def check_context_outputs(rep, drf, crf):
    """RULE: output_updates_requires_id, output_reason_recommended (section 11)."""
    entities = {doc["entity"]["id"] for _, doc in crf}
    for where, doc in drf:
        for out in (doc.get("context_validation") or {}).get("context_outputs", []):
            if out["action"] in {"updates", "invalidates"}:
                target = out.get("entity_id")
                if target and target not in entities:
                    rep.add(WARNING, "output_target_resolves", where,
                            f"context_output {out['action']} targets {target}, "
                            "which is not an entity in this corpus")
            if not out.get("reason"):
                rep.add(ADVISORY, "output_reason_recommended", where,
                        f"context_output {out['action']} has no reason")


def check_decision_graph(rep, drf):
    """RULE: circular_dependency_prevention, supersedes_state_consistency (section 5)."""
    known = {doc["decision"]["id"]: (where, doc) for where, doc in drf}
    depends = defaultdict(set)

    for where, doc in drf:
        me = doc["decision"]["id"]
        for link in doc["decision"].get("related_decisions", []):
            target = link["id"]
            if target == me:
                rep.add(ERROR, "no_self_reference", where,
                        f"decision references itself via {link['relationship']!r}")
                continue
            if target not in known:
                rep.add(ADVISORY, "related_decision_resolves", where,
                        f"{link['relationship']} -> {target} is not in this corpus "
                        "(expected when the decision lives elsewhere)")
                continue
            if link["relationship"] == "depends_on":
                depends[me].add(target)
            if link["relationship"] == "supersedes":
                other_where, other = known[target]
                if other["meta"]["status"] != "superseded":
                    rep.add(WARNING, "supersedes_state_consistency", where,
                            f"supersedes {target}, whose status is "
                            f"{other['meta']['status']!r} rather than 'superseded' ({other_where})")

    for cycle in find_cycles(depends):
        rep.add(ERROR, "circular_dependency_prevention", "corpus",
                "circular depends_on chain: " + " -> ".join(cycle))


def check_entity_graph(rep, crf, drf):
    """RULE: relationship_target_exists, inverse consistency, supersession (section 12)."""
    entities = {doc["entity"]["id"]: (where, doc["entity"]) for where, doc in crf}
    decisions = {doc["decision"]["id"] for _, doc in drf}
    edges = set()
    supersedes = defaultdict(set)

    for where, doc in crf:
        entity = doc["entity"]
        me = entity["id"]

        for rel in entity.get("relationships", []):
            target = rel["target_id"]
            if target == me:
                rep.add(ERROR, "no_self_relationship", where,
                        f"entity relates to itself via {rel['type']!r}")
                continue
            if target not in entities:
                rep.add(WARNING, "relationship_target_exists", where,
                        f"{entity['name']!r} --{rel['type']}--> {target} does not resolve")
                continue
            edges.add((me, rel["type"], target))

        sup = entity.get("supersedes")
        if sup:
            target = sup["entity_id"]
            if target == me:
                rep.add(ERROR, "no_circular_supersession", where,
                        "entity supersedes itself")
            elif target not in entities:
                rep.add(WARNING, "supersedes_creates_chain", where,
                        f"supersedes {target}, which is not in this corpus")
            else:
                supersedes[me].add(target)

        match = DECISION_SOURCE.match(entity["provenance"]["source"])
        if match and match.group(1) not in decisions:
            rep.add(WARNING, "decision_provenance_format", where,
                    f"provenance.source references decision {match.group(1)}, "
                    "which is not in this corpus")

    for source, rel_type, target in sorted(edges):
        if (target, INVERSE[rel_type], source) not in edges:
            rep.add(ADVISORY, "relationship_inverse_consistency", entities[source][0],
                    f"{entities[source][1]['name']!r} --{rel_type}--> "
                    f"{entities[target][1]['name']!r} has no {INVERSE[rel_type]} edge back")

    for cycle in find_cycles(supersedes):
        rep.add(ERROR, "no_circular_supersession", "corpus",
                "circular supersession chain: " + " -> ".join(cycle))


def check_advisories(rep, drf):
    """RULE: confidence_phase_consistency, assumption and synthesis advisories (sections 2, 6, 7)."""
    for where, doc in drf:
        state = doc["cognitive_state"]
        if state["phase"] == "decision" and state["confidence"] < 50:
            rep.add(ADVISORY, "confidence_phase_consistency", where,
                    f"phase is 'decision' but confidence is {state['confidence']} (< 50)")

        for assumption in doc.get("assumptions", []):
            confidence = assumption.get("confidence")
            if confidence is None:
                continue
            if assumption["validated"] and confidence < 60:
                rep.add(ADVISORY, "validated_assumption_confidence", where,
                        f"validated assumption at confidence {confidence}: "
                        f"{assumption['description'][:60]}")
            if not assumption["validated"] and confidence >= 80:
                rep.add(ADVISORY, "unvalidated_critical_assumptions", where,
                        f"unvalidated assumption at confidence {confidence}: "
                        f"{assumption['description'][:60]}")

        for item in doc.get("interventions", []):
            if not item.get("impact"):
                rep.add(ADVISORY, "intervention_has_impact", where,
                        f"intervention {item['id']} records no impact")

        if doc["meta"]["status"] == "approved":
            synthesis = doc["synthesis"]
            if not synthesis.get("follow_ups"):
                rep.add(ADVISORY, "approved_synthesis_complete", where,
                        "approved decision has no follow_ups")
            if not synthesis.get("alternatives"):
                rep.add(ADVISORY, "approved_synthesis_complete", where,
                        "approved decision records no alternatives")


def find_cycles(graph):
    """Return each cycle in a directed adjacency map, as a list of node lists."""
    cycles, colour = [], {}

    def visit(node, stack):
        colour[node] = "grey"
        stack.append(node)
        for nxt in sorted(graph.get(node, ())):
            if colour.get(nxt) == "grey":
                cycles.append(stack[stack.index(nxt):] + [nxt])
            elif colour.get(nxt) is None:
                visit(nxt, stack)
        stack.pop()
        colour[node] = "black"

    for node in sorted(graph):
        if colour.get(node) is None:
            visit(node, [])
    return cycles


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--strict", action="store_true",
                        help="treat WARNING findings as failures")
    parser.add_argument("--quiet", action="store_true",
                        help="hide ADVISORY findings")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    drf, crf = load_corpus()
    rep = Report()

    check_uniqueness(rep, drf, crf)
    check_temporal(rep, drf, crf, now)
    check_context_refs(rep, drf, crf, now)
    check_context_outputs(rep, drf, crf)
    check_decision_graph(rep, drf)
    check_entity_graph(rep, crf, drf)
    check_advisories(rep, drf)

    order = {ERROR: 0, WARNING: 1, ADVISORY: 2}
    for severity, rule, where, message in sorted(rep.findings, key=lambda f: (order[f[0]], f[1], f[2])):
        if severity == ADVISORY and args.quiet:
            continue
        print(f"{severity:8s} {rule:38s} {where}\n         {message}")

    errors, warnings, advisories = (rep.count(s) for s in (ERROR, WARNING, ADVISORY))
    print(
        f"\nChecked {len(drf)} DRF and {len(crf)} CRF document(s): "
        f"{errors} error(s), {warnings} warning(s), {advisories} advisory item(s)"
    )
    if errors:
        return 1
    if warnings and args.strict:
        print("Failing because --strict treats warnings as errors.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
