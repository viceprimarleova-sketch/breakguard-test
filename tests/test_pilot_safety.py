import json
from pathlib import Path

import pytest

from breakguard import cli
from breakguard.backups import restore_backup
from breakguard.fixer import apply_with_backup, preview_fixes
from breakguard.scanner import load_rules, scan, scan_repository

QUERY = b'query Buyer { customer { id lastIncompleteCheckout { id } } }\r\n'


def rules():
    return load_rules(cli.default_rules_path())


def invoke(monkeypatch, *args):
    monkeypatch.setattr("sys.argv", ["breakguard", *map(str, args)])
    return cli.main()


@pytest.mark.parametrize("kind", ["missing", "file"])
def test_invalid_repository_is_operational_error(monkeypatch, tmp_path, capsys, kind):
    target = tmp_path / kind
    if kind == "file":
        target.write_text("not a directory")
    assert invoke(monkeypatch, target, "--json") == 2
    captured = capsys.readouterr()
    assert not captured.out
    assert "error:" in captured.err


def test_apply_json_remains_machine_readable_and_restore_is_exact(monkeypatch, tmp_path, capsys):
    query = tmp_path / "buyer.graphql"
    query.write_bytes(QUERY)
    assert invoke(monkeypatch, tmp_path, "--apply-fixes", "--json") == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out) == []
    backup_id = next(line.split(": ", 1)[1] for line in captured.err.splitlines() if line.startswith("Backup:"))
    assert query.read_bytes().endswith(b"\r\n")
    assert invoke(monkeypatch, tmp_path, "--restore", backup_id, "--json") == 1
    assert len(json.loads(capsys.readouterr().out)) == 1
    assert query.read_bytes() == QUERY


def test_preview_creates_no_backup_and_leaves_source_intact(tmp_path):
    query = tmp_path / "buyer.graphql"
    query.write_bytes(QUERY)
    assert preview_fixes(tmp_path, scan(tmp_path, rules()))
    assert query.read_bytes() == QUERY
    assert not (tmp_path / ".breakguard").exists()


def test_restore_refuses_all_files_if_one_has_later_edits(tmp_path):
    first, second = tmp_path / "a.graphql", tmp_path / "b.graphql"
    first.write_bytes(QUERY)
    second.write_bytes(QUERY)
    fixed = apply_with_backup(tmp_path, scan(tmp_path, rules()))
    after_first = first.read_bytes()
    second.write_bytes(b"# later work\n" + second.read_bytes())
    with pytest.raises(ValueError, match="edited after"):
        restore_backup(tmp_path, fixed.backup_id)
    assert first.read_bytes() == after_first
    assert second.read_bytes().startswith(b"# later work")


def test_restore_refuses_corrupt_backup(tmp_path):
    (tmp_path / "a.graphql").write_bytes(QUERY)
    fixed = apply_with_backup(tmp_path, scan(tmp_path, rules()))
    copy = tmp_path / ".breakguard" / "backups" / fixed.backup_id / "files" / "a.graphql"
    copy.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="integrity"):
        restore_backup(tmp_path, fixed.backup_id)


def test_write_failure_rolls_back_previously_changed_files(monkeypatch, tmp_path):
    from breakguard import backups
    for name in ("a.graphql", "b.graphql"):
        (tmp_path / name).write_bytes(QUERY)
    real_replace = backups.os.replace
    failed = False

    def fail_second(source, destination):
        nonlocal failed
        if Path(destination) == tmp_path / "b.graphql" and not failed:
            failed = True
            raise OSError("simulated disk failure")
        return real_replace(source, destination)

    monkeypatch.setattr(backups.os, "replace", fail_second)
    with pytest.raises(OSError, match="disk failure"):
        apply_with_backup(tmp_path, scan(tmp_path, rules()))
    assert (tmp_path / "a.graphql").read_bytes() == QUERY
    assert (tmp_path / "b.graphql").read_bytes() == QUERY


def symlink_or_skip(link, target):
    try:
        link.symlink_to(target, target_is_directory=target.is_dir())
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks requires OS permissions")


def test_scanner_and_fixer_refuse_external_symlink(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside.graphql"
    outside.write_bytes(QUERY)
    link = repo / "linked.graphql"
    symlink_or_skip(link, outside)
    result = scan_repository(repo, rules())
    assert not result.findings and result.summary.symlinks_skipped == 1
    finding = scan(tmp_path, rules())[0]
    finding.file = "linked.graphql"
    with pytest.raises(ValueError, match="symbolic link"):
        apply_with_backup(repo, [finding])
    assert outside.read_bytes() == QUERY


def test_symlink_backup_directory_aborts_before_source_edit(tmp_path):
    repo, outside = tmp_path / "repo", tmp_path / "outside"
    repo.mkdir()
    outside.mkdir()
    (repo / "a.graphql").write_bytes(QUERY)
    symlink_or_skip(repo / ".breakguard", outside)
    with pytest.raises(ValueError, match="symbolic link"):
        apply_with_backup(repo, scan(repo, rules()))
    assert (repo / "a.graphql").read_bytes() == QUERY
    assert list(outside.iterdir()) == []


def test_empty_coverage_report_discloses_limits(monkeypatch, tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "notes.txt").write_text("unscanned content")
    report = tmp_path / "report.json"
    assert invoke(monkeypatch, repo, "--report", report) == 0
    document = json.loads(report.read_text())
    assert document["coverage"]["files_scanned"] == 0
    assert document["coverage"]["files_unsupported"] == 1
    assert document["application_tests_run"] is False
    assert "not Shopify compatibility certification" in document["limits"][0]
    assert "does not certify" in capsys.readouterr().out


def test_report_failure_prevents_source_changes(monkeypatch, tmp_path):
    (tmp_path / "a.graphql").write_bytes(QUERY)
    destination = tmp_path / "absent" / "report.json"
    assert invoke(monkeypatch, tmp_path, "--apply-fixes", "--report", destination) == 2
    assert (tmp_path / "a.graphql").read_bytes() == QUERY
    assert not (tmp_path / ".breakguard").exists()


def test_unexpected_scanner_error_cannot_be_mistaken_for_findings(monkeypatch, tmp_path):
    def crash(*args):
        raise RuntimeError("internal fault")
    monkeypatch.setattr(cli, "scan_repository", crash)
    assert invoke(monkeypatch, tmp_path) == 2


@pytest.mark.parametrize("delimiter", ["GRAPHQL", "GQL", "QUERY", "MUTATION"])
def test_embedded_graphql_reports_real_source_lines_and_never_edits(tmp_path, delimiter):
    js = 'const query = `#graphql\nquery Buyer {\n  customer { id lastIncompleteCheckout { id } }\n}`;\n'
    ruby = 'QUERY = <<~GRAPHQL\nfragment Discount on DraftOrderDiscountNotAppliedWarning {\n priceRule { title }\n}\nGRAPHQL\n'
    ruby = ruby.replace("GRAPHQL", delimiter)
    (tmp_path / "buyer.ts").write_text(js)
    (tmp_path / "discount.rb").write_text(ruby)
    result = scan_repository(tmp_path, rules())
    assert {(f.file, f.line) for f in result.findings} == {("buyer.ts", 3), ("discount.rb", 3)}
    assert all(f.auto_fix is None and "Embedded" in f.review_reason for f in result.findings)
    assert result.summary.embedded_documents_scanned == 2
    assert apply_with_backup(tmp_path, result.findings).changed == []
    assert (tmp_path / "buyer.ts").read_text() == js
    assert (tmp_path / "discount.rb").read_text() == ruby


def test_dynamic_embedded_query_is_disclosed_as_unchecked(tmp_path):
    (tmp_path / "buyer.js").write_text('const q = `#graphql\nquery Buyer { customer { ${fields} } }`;')
    result = scan_repository(tmp_path, rules())
    assert not result.findings
    assert result.summary.embedded_documents_skipped == 1


def test_comment_and_unmarked_string_are_not_parsed_as_graphql(tmp_path):
    source = '// const q = gql`query X { customer { lastIncompleteCheckout { id } } }`;\n'
    source += 'const description = `customer { lastIncompleteCheckout { id } }`;\n'
    (tmp_path / "notes.ts").write_text(source)
    assert not scan(tmp_path, rules())


def test_backup_is_ignored_by_git_and_by_scanner(tmp_path):
    import subprocess
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "a.graphql").write_bytes(QUERY)
    apply_with_backup(tmp_path, scan(tmp_path, rules()))
    assert not scan(tmp_path, rules())
    status = subprocess.run(["git", "status", "--porcelain"], cwd=tmp_path, capture_output=True, text=True, check=True)
    assert ".breakguard" not in status.stdout


@pytest.mark.parametrize("existing_ignore", ["# existing project settings\n", "!backups/\n!backups/**\n"])
def test_snapshot_stays_ignored_without_changing_existing_project_settings(tmp_path, existing_ignore):
    import subprocess
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".breakguard").mkdir()
    ignore = tmp_path / ".breakguard" / ".gitignore"
    ignore.write_text(existing_ignore)
    (tmp_path / "a.graphql").write_bytes(QUERY)
    fixed = apply_with_backup(tmp_path, scan(tmp_path, rules()))
    visible = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "--", ".breakguard/backups"],
        cwd=tmp_path, capture_output=True, text=True, check=True,
    ).stdout
    assert not visible, "Original source and manifest must not appear in ordinary git add candidates"
    assert ignore.read_text() == existing_ignore
    assert restore_backup(tmp_path, fixed.backup_id) == ["a.graphql"]
    assert (tmp_path / "a.graphql").read_bytes() == QUERY
