from importlib.metadata import version as distribution_version
from pathlib import Path

import breakguard
from breakguard.cli import default_rules_path
from breakguard.scanner import load_rules, scan
from breakguard.fixer import apply_fixes, preview_fixes


def _rules():
    return load_rules(default_rules_path())


def test_runtime_and_distribution_versions_match():
    assert breakguard.__version__ == distribution_version("breakguard")


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


def test_price_rule_requires_nearby_warning_context(tmp_path: Path):
    q = tmp_path / "queries.graphql"
    q.write_text("""query A {
  draftOrder(id: "gid://shopify/DraftOrder/1") {
    warnings {
      ... on DraftOrderDiscountNotAppliedWarning {
        discountTitle
      }
    }
  }
}

query B {
  somethingElse {
    one
    two
    three
    four
    five
    six
    seven
    eight
    nine
    priceRule
  }
}
""", encoding="utf-8")

    findings = scan(tmp_path, _rules())

    assert all(f.rule_id != "SHOPIFY-ADMIN-2026-10-PRICERULE" for f in findings)


def test_fix_preview_is_unified_diff_and_does_not_modify_file(tmp_path: Path):
    q = tmp_path / "queries.graphql"
    original = """query X {
  customer(id: "gid://shopify/Customer/1") {
    lastIncompleteCheckout {
      id
    }
  }
}
"""
    q.write_text(original, encoding="utf-8")

    findings = scan(tmp_path, _rules())
    previews = preview_fixes(tmp_path, findings)

    assert q.read_text(encoding="utf-8") == original
    assert set(previews) == {"queries.graphql"}
    assert "--- a/queries.graphql" in previews["queries.graphql"]
    assert "+++ b/queries.graphql" in previews["queries.graphql"]
    assert "-    lastIncompleteCheckout {" in previews["queries.graphql"]


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


def test_packaged_default_rules_path_exists():
    path = default_rules_path()
    assert path.exists()
    assert path.name == "shopify_2026_10.json"
