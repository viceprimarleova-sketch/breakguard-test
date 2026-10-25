"""Offline QA of synthetic migration cases against local Shopify introspection.

This is a release-review utility, not a schema check in the product CLI.
It reads four local, complete introspection files and never calls a store/API.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import tempfile

from graphql import build_client_schema, parse, validate

from breakguard import graphql_edits
from breakguard.backups import restore_backup
from breakguard.cli import default_rules_path
from breakguard.fixer import apply_with_backup, preview_fixes
from breakguard.scanner import load_rules, scan


def warning_query(selection: str, fragments: str = "", outer: str = "") -> str:
    return """mutation ReviewWarnings($input: DraftOrderInput!) {
  draftOrderCalculate(input: $input) {
    calculatedDraftOrder {
      warnings {
        %s
        ... on DraftOrderDiscountNotAppliedWarning {
          %s
        }
      }
    }
  }
}
%s
""" % (outer, selection, fragments)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("admin-before", "admin-after", "customer-before", "customer-after"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a new output path; existing reports are never overwritten.")

    schemas, identities = {}, {}
    for name in ("admin_before", "admin_after", "customer_before", "customer_after"):
        data = getattr(args, name).read_bytes()
        document = json.loads(data)
        schemas[name] = build_client_schema(document.get("data", document))
        identities[name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

    price = "priceRule { title discountCodes(first: 1) { nodes { code } } }"
    cases = [
        ("customer_normal", "customer", True,
         "query Buyer { customer { id lastIncompleteCheckout { id appliedGiftCards { id } } } }", ""),
        ("customer_only", "customer", False,
         "query Buyer { customer { lastIncompleteCheckout { id } } }", ""),
        ("customer_alias", "customer", False,
         "query Buyer { customer { id legacy: lastIncompleteCheckout { id } } }", ""),
        ("price_normal", "admin", True, warning_query(price), ""),
        ("price_title_alias", "admin", False,
         warning_query("discountTitle: message " + price), ""),
        ("price_code_alias", "admin", False,
         warning_query("discountCode: message " + price), ""),
        ("price_outer_alias", "admin", False,
         warning_query(price, outer="discountTitle: message"), ""),
        ("price_fragment_alias", "admin", False,
         warning_query("...WarningLabel " + price,
                       "fragment WarningLabel on DraftOrderDiscountNotAppliedWarning { discountTitle: message }"), ""),
        ("price_compatible_fragment", "admin", True,
         warning_query("...WarningLabel " + price,
                       "fragment WarningLabel on DraftOrderDiscountNotAppliedWarning { label: message }"), ""),
        ("price_external_fragment", "admin", False,
         warning_query("...ExternalFields " + price),
         "fragment ExternalFields on DraftOrderDiscountNotAppliedWarning { discountTitle: message }"),
    ]
    rules = load_rules(default_rules_path())
    results = []
    with tempfile.TemporaryDirectory(prefix="breakguard-schema-review-") as temporary:
        for name, surface, automatic, source, validation_context in cases:
            root = Path(temporary) / name
            root.mkdir()
            path = root / "case.graphql"
            original = (source + "\n").encode()
            path.write_bytes(original)
            before_errors = [e.message for e in validate(
                schemas[surface + "_before"], parse(source + "\n" + validation_context))]
            target_before = [e.message for e in validate(
                schemas[surface + "_after"], parse(source + "\n" + validation_context))]
            assert not before_errors, (name, before_errors)
            assert target_before, (name, "The target schema should reject the removed field.")
            findings = scan(root, rules)
            assert len(findings) == 1, (name, findings)
            assert bool(findings[0].auto_fix) is automatic, (name, findings)
            previews = preview_fixes(root, findings)
            assert path.read_bytes() == original, (name, "preview modified source")
            result = apply_with_backup(root, findings)
            updated = path.read_text()
            after_errors = [e.message for e in validate(
                schemas[surface + "_after"], parse(updated + "\n" + validation_context))]
            remaining = scan(root, rules)
            if automatic:
                assert previews and result.changed == [path.name] and result.backup_id
                assert not after_errors and not remaining, (name, after_errors, remaining)
                assert restore_backup(root, result.backup_id) == [path.name]
            else:
                assert not previews and result.changed == [] and result.backup_id is None
                assert after_errors and remaining, (name, "manual case must remain visible")
            assert path.read_bytes() == original, (name, "source not exactly preserved/restored")
            results.append({
                "case": name, "surface": surface, "automatic_edit": automatic,
                "before_schema_errors": before_errors,
                "target_before_schema_errors": target_before,
                "target_after_schema_errors": after_errors,
                "changed_files": result.changed,
                "remaining_findings": [asdict(f) for f in remaining],
                "exact_preservation_or_restore": True,
                "synthetic_source": source,
                "validation_context_from_another_file": validation_context,
            })
    report = {
        "scope": "Offline full-schema validation of synthetic cases, not an application or store test.",
        "package_version": version("breakguard"),
        "graphql_edits_sha256": hashlib.sha256(Path(graphql_edits.__file__).read_bytes()).hexdigest(),
        "schema_files": identities,
        "cases_passed": len(results),
        "automatic_cases": sum(case[2] for case in cases),
        "manual_cases": sum(not case[2] for case in cases),
        "results": results,
        "not_validated": ["live Shopify behavior", "response consumers", "customer usefulness", "willingness to pay"],
    }
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({key: report[key] for key in ("cases_passed", "automatic_cases", "manual_cases")}, indent=2))


if __name__ == "__main__":
    main()
