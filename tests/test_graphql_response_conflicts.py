"""Preserve response names when a migration introduces new GraphQL fields."""
import pytest
from graphql import build_schema, parse, validate

from breakguard.cli import default_rules_path
from breakguard.fixer import apply_fixes, preview_fixes
from breakguard.scanner import load_rules, scan


@pytest.mark.parametrize("selection,fragments", [
    ("discountTitle: message priceRule { title }", ""),
    ("discountCode: message priceRule { title }", ""),
    ("...LegacyLabel priceRule { title }",
     "fragment LegacyLabel on DraftOrderDiscountNotAppliedWarning { discountTitle: message }"),
    ("...FieldsInAnotherFile priceRule { title }", ""),
])
def test_price_rule_with_reserved_or_unknown_response_names_stays_manual(
        tmp_path, selection, fragments):
    source = ("fragment WarningFields on DraftOrderDiscountNotAppliedWarning { "
              + selection + " }\n" + fragments + "\n")
    path = tmp_path / "warnings.graphql"
    path.write_text(source)
    findings = scan(tmp_path, load_rules(default_rules_path()))
    assert len(findings) == 1
    assert findings[0].auto_fix is None
    assert preview_fixes(tmp_path, findings) == {}
    assert apply_fixes(tmp_path, findings) == []
    assert path.read_text() == source
    assert not (tmp_path / ".breakguard").exists()


def test_alias_outside_warning_inline_fragment_stays_manual(tmp_path):
    source = """query Warnings {
  warnings {
    discountTitle: message
    ... on DraftOrderDiscountNotAppliedWarning { priceRule { title } }
  }
}
"""
    path = tmp_path / "warnings.graphql"
    path.write_text(source)
    findings = scan(tmp_path, load_rules(default_rules_path()))
    assert findings and findings[0].auto_fix is None
    assert apply_fixes(tmp_path, findings) == []
    assert path.read_text() == source


@pytest.mark.parametrize("selection,fragments", [
    ("label: message priceRule { title }", ""),
    ("discountTitle: discountTitle priceRule { title }", ""),
    ("...WarningLabel priceRule { title }",
     "fragment WarningLabel on DraftOrderDiscountNotAppliedWarning { label: message }"),
])
def test_compatible_response_names_still_allow_schema_valid_replacement(
        tmp_path, selection, fragments):
    # Minimal schema-shaped regression, supplemented by the separate full
    # official-schema audit. It does not certify an application's behavior.
    schema = build_schema("""
      type Query { warnings: [DraftOrderDiscountNotAppliedWarning!]! }
      type DraftOrderDiscountNotAppliedWarning {
        message: String!
        discountTitle: String
        discountCode: String
      }
    """)
    source = ("query Warnings { warnings { ... on DraftOrderDiscountNotAppliedWarning { "
              + selection + " } } }\n"
              + fragments + "\n")
    path = tmp_path / "warnings.graphql"
    path.write_text(source)
    findings = scan(tmp_path, load_rules(default_rules_path()))
    assert len(findings) == 1 and findings[0].auto_fix
    assert apply_fixes(tmp_path, findings) == [path.name]
    assert validate(schema, parse(path.read_text())) == []
