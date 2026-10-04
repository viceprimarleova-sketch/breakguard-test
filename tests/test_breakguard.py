from pathlib import Path
import json

from breakguard.scanner import load_rules, scan
from breakguard.fixer import apply_fixes


def test_scan_and_fix(tmp_path: Path):
    q = tmp_path / "queries.graphql"
    q.write_text("""query X {
  customer(id: \"gid://shopify/Customer/1\") {
    lastIncompleteCheckout {
      id
    }
  }
  draftOrder(id: \"gid://shopify/DraftOrder/1\") {
    warnings {
      ... on DraftOrderDiscountNotAppliedWarning {
        priceRule
      }
    }
  }
}
""", encoding="utf-8")
    (tmp_path / "legacy.js").write_text("admin.rest.resources.ScriptTag.create({})\n", encoding="utf-8")

    rules = load_rules(Path(__file__).parents[1] / "rules" / "shopify_2026_10.json")
    before = scan(tmp_path, rules)
    assert len(before) == 3

    changed = apply_fixes(tmp_path, before)
    assert "queries.graphql" in changed

    after = scan(tmp_path, rules)
    assert len(after) == 1
    assert after[0].rule_id == "SHOPIFY-ADMIN-SCRIPTTAG-2027-03"
