from pathlib import Path

from breakguard.scanner import load_rules, scan
from breakguard.fixer import apply_fixes


def _rules():
    return load_rules(Path(__file__).parents[1] / "rules" / "shopify_2026_10.json")


def test_scan_and_fix(tmp_path: Path):
    q = tmp_path / "queries.graphql"
    q.write_text("""query X {
  customer(id: "gid://shopify/Customer/1") {
    lastIncompleteCheckout {
      id
    }
  }
  draftOrder(id: "gid://shopify/DraftOrder/1") {
    warnings {
      ... on DraftOrderDiscountNotAppliedWarning {
        priceRule
      }
    }
  }
}
""", encoding="utf-8")
    (tmp_path / "legacy.js").write_text("admin.rest.resources.ScriptTag.create({})\n", encoding="utf-8")

    before = scan(tmp_path, _rules())
    assert len(before) == 3

    changed = apply_fixes(tmp_path, before)
    assert "queries.graphql" in changed

    after = scan(tmp_path, _rules())
    assert len(after) == 1
    assert after[0].rule_id == "SHOPIFY-ADMIN-SCRIPTTAG-2027-03"


def test_scan_respects_rule_extensions(tmp_path: Path):
    (tmp_path / "workflow.yml").write_text(
        'run: echo "ScriptTag lastIncompleteCheckout priceRule DraftOrderDiscountNotAppliedWarning"\n',
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "Migration notes: ScriptTag lastIncompleteCheckout priceRule DraftOrderDiscountNotAppliedWarning\n",
        encoding="utf-8",
    )
    (tmp_path / "legacy.ts").write_text(
        "admin.rest.resources.ScriptTag.create({})\n",
        encoding="utf-8",
    )
    (tmp_path / "query.gql").write_text(
        """query X {
  customer(id: "gid://shopify/Customer/1") {
    lastIncompleteCheckout {
      id
    }
  }
}
""",
        encoding="utf-8",
    )

    findings = scan(tmp_path, _rules())

    assert len(findings) == 2
    assert {f.file for f in findings} == {"legacy.ts", "query.gql"}
