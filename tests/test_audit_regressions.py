"""Regression cases from Shopify's public manager and published migration examples."""
from pathlib import Path

import pytest
from graphql import parse

from breakguard.cli import default_rules_path
from breakguard.fixer import apply_fixes, preview_fixes
from breakguard.scanner import load_rules, scan


def findings(root):
    return scan(root, load_rules(default_rules_path()))


@pytest.mark.parametrize("filename,source", [
    ("install.rb", 'SCRIPT_TAG_CREATE_MUTATION = <<~QUERY\nmutation ScriptTagCreate($input: ScriptTagInput!) {\n  scriptTagCreate(input: $input) { scriptTag { id } }\n}\nQUERY\n'),
    ("install.ts", 'const query = `mutation { scriptTagCreate(input: $input) { scriptTag { id } } }`;\n'),
    ("install.graphql", 'mutation { scriptTagUpdate(id: $id, input: $input) { scriptTag { id } } }\n'),
    ("install.js", 'admin.rest.resources.ScriptTag.create({});\n'),
    ("install.rb", 'ShopifyAPI::ScriptTag.new(session: session)\n'),
])
def test_script_tag_creation_forms_are_manual(tmp_path, filename, source):
    path = tmp_path / filename
    path.write_text(source)
    fs = findings(tmp_path)
    assert len(fs) == 1
    assert fs[0].auto_fix is None
    assert preview_fixes(tmp_path, fs) == {}
    assert apply_fixes(tmp_path, fs) == []
    assert path.read_text() == source


@pytest.mark.parametrize("filename,source", [
    ("cleanup.ts", 'const q = `mutation { scriptTagDelete(id: $id) { deletedScriptTagId } }`;\n'),
    ("audit.js", 'admin.rest.resources.ScriptTag.all({session});\n'),
    ("component.tsx", 'function ScriptTag() { return null; }\n'),
    ("notes.js", '// scriptTagCreate(input: $input)\n'),
    ("legacy.test.ts", 'admin.rest.resources.ScriptTag.create({});\n'),
    ("tests/install.rb", 'ShopifyAPI::ScriptTag.new(session: session)\n'),
])
def test_script_tag_non_creation_and_test_files_do_not_trigger(tmp_path, filename, source):
    path = tmp_path / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source)
    assert findings(tmp_path) == []


def test_real_price_rule_selection_is_replaced_as_a_whole(tmp_path):
    source = '''# Preserve this migration note.
fragment WarningFields on DraftOrderDiscountNotAppliedWarning {
  priceRule {
    title
    discountCodes(first: 1) {
      nodes { code }
    }
  }
}
'''
    path = tmp_path / "warning.graphql"
    path.write_text(source)
    fs = findings(tmp_path)
    assert len(fs) == 1 and fs[0].auto_fix
    preview = preview_fixes(tmp_path, fs)
    assert path.read_text() == source
    assert set(preview) == {path.name}
    assert apply_fixes(tmp_path, fs) == [path.name]
    result = path.read_text()
    document = parse(result)
    names = [field.name.value for field in document.definitions[0].selection_set.selections]
    assert names == ["discountTitle", "discountCode"]
    assert result.startswith("# Preserve this migration note.\n")
    assert findings(tmp_path) == []


def test_compact_customer_query_keeps_other_fields(tmp_path):
    source = 'query Buyer { customer { id lastIncompleteCheckout { id } emailAddress { emailAddress } } }\n'
    path = tmp_path / "customer.gql"
    path.write_text(source)
    assert apply_fixes(tmp_path, findings(tmp_path)) == [path.name]
    result = parse(path.read_text())
    fields = result.definitions[0].selection_set.selections[0].selection_set.selections
    assert [field.name.value for field in fields] == ["id", "emailAddress"]


@pytest.mark.parametrize("source", [
    'query Buyer { customer { lastIncompleteCheckout { id } } }',
    'query Buyer { customer { a: lastIncompleteCheckout { id } b: lastIncompleteCheckout { id } } }',
    'query Buyer($show: Boolean!) { customer { id lastIncompleteCheckout @include(if: $show) { id } } }',
    'fragment W on DraftOrderDiscountNotAppliedWarning { legacy: priceRule { title } }',
    'fragment W on DraftOrderDiscountNotAppliedWarning { priceRule { id } }',
    'fragment W on DraftOrderDiscountNotAppliedWarning { priceRule { discountCodes(first: 10) { nodes { code } } } }',
    'query Buyer { customer { id lastIncompleteCheckout { id }',
])
def test_unsafe_or_ambiguous_graphql_stays_manual(tmp_path, source):
    path = tmp_path / "manual.graphql"
    path.write_text(source)
    fs = findings(tmp_path)
    assert fs
    assert all(f.auto_fix is None for f in fs)
    assert preview_fixes(tmp_path, fs) == {}
    assert apply_fixes(tmp_path, fs) == []
    assert path.read_text() == source


def test_comments_strings_schema_and_adjacent_context_do_not_trigger(tmp_path):
    source = '''# lastIncompleteCheckout priceRule
query Note { note(text: "lastIncompleteCheckout") }
fragment W on DraftOrderDiscountNotAppliedWarning { discountTitle }
query Other { unrelated { priceRule } }
'''
    (tmp_path / "queries.graphql").write_text(source)
    (tmp_path / "schema.graphql").write_text('type Customer { lastIncompleteCheckout: String }\n')
    assert findings(tmp_path) == []


def test_price_rule_beyond_old_eight_line_window_is_detected(tmp_path):
    source = 'fragment W on DraftOrderDiscountNotAppliedWarning {\n' + '\n' * 10 + 'priceRule { title }\n}\n'
    path = tmp_path / "warning.graphql"
    path.write_text(source)
    assert len(findings(tmp_path)) == 1
    assert apply_fixes(tmp_path, findings(tmp_path)) == [path.name]
    parse(path.read_text())


def test_existing_discount_fields_are_not_duplicated(tmp_path):
    path = tmp_path / "warning.graphql"
    path.write_text('fragment W on DraftOrderDiscountNotAppliedWarning { discountTitle discountCode priceRule { title } }')
    apply_fixes(tmp_path, findings(tmp_path))
    fields = parse(path.read_text()).definitions[0].selection_set.selections
    assert [field.name.value for field in fields] == ["discountTitle", "discountCode"]


def test_packaged_and_repository_rules_match():
    assert load_rules(default_rules_path()) == load_rules(Path(__file__).parents[1] / "rules/shopify_2026_10.json")


def test_fix_preserves_windows_line_endings(tmp_path):
    source = b'fragment W on DraftOrderDiscountNotAppliedWarning {\r\n  priceRule { title }\r\n}\r\n'
    path = tmp_path / "windows.graphql"
    path.write_bytes(source)
    apply_fixes(tmp_path, findings(tmp_path))
    result = path.read_bytes()
    assert result == b'fragment W on DraftOrderDiscountNotAppliedWarning {\r\n  discountTitle\r\n  discountCode\r\n}\r\n'


def test_mixed_safe_and_aliased_fields_on_same_line_stay_manual(tmp_path):
    path = tmp_path / "aliases.graphql"
    path.write_text('query Buyer { customer { id lastIncompleteCheckout { id } old: lastIncompleteCheckout { id } } }')
    fs = findings(tmp_path)
    assert len(fs) == 2
    assert all(f.auto_fix is None for f in fs)
    assert apply_fixes(tmp_path, fs) == []


def test_rule_exclusions_are_relative_to_scanned_repository(tmp_path):
    root = tmp_path / "tests" / "shopify-project"
    root.mkdir(parents=True)
    (root / "install.rb").write_text('ShopifyAPI::ScriptTag.new(session: session)\n')
    assert len(findings(root)) == 1
