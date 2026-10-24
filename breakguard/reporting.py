from dataclasses import asdict
import hashlib
import json
from datetime import datetime, timezone

from . import __version__

LIMITS = [
    "Only the listed rule families are checked; zero findings is not Shopify compatibility certification.",
    "Standalone GraphQL edits check syntax, not an API schema, API version or response-consuming application code.",
    "Marked static JS/TS templates and GRAPHQL/GQL/QUERY/MUTATION Ruby heredocs are detection-only; extraction is heuristic.",
    "Dynamic/unparseable embedded queries, other string forms, languages and generated/ignored paths may be missed.",
    "ScriptTag findings are source-pattern candidates for manual review, not proof of an executed API call.",
]


def make_report(result, rules, mode="scan", changed=None, backup_id=None):
    return {
        "schema_version": 1,
        "breakguard_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "rule_ids": [r["id"] for r in rules],
        "rules_sha256": hashlib.sha256(json.dumps(rules, sort_keys=True).encode()).hexdigest(),
        "coverage": asdict(result.summary),
        "limits": LIMITS,
        "findings": [finding.to_dict() for finding in result.findings],
        "changed_files": changed or [],
        "backup_id": backup_id,
        "application_tests_run": False,
    }
