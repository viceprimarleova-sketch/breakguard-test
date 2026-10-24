from __future__ import annotations

import json
import os
import re
import stat
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

from .embedded import JS_EXTENSIONS, extract_documents
from .graphql_edits import GRAPHQL_ACTIONS, matches_action, plan_edits, query_fields


@dataclass
class Finding:
    rule_id: str
    severity: str
    file: str
    line: int
    message: str
    remediation: str
    source: str
    auto_fix: str | None
    review_reason: str | None = None

    def to_dict(self):
        return asdict(self)


@dataclass
class ScanSummary:
    files_seen: int = 0
    files_scanned: int = 0
    files_unsupported: int = 0
    symlinks_skipped: int = 0
    non_utf8_skipped: int = 0
    embedded_documents_scanned: int = 0
    embedded_documents_skipped: int = 0
    unparseable_graphql_files: int = 0


@dataclass
class ScanResult:
    findings: list[Finding]
    summary: ScanSummary


def load_rules(rule_file: Path) -> list[dict]:
    document = json.loads(rule_file.read_text(encoding="utf-8"))
    rules = document.get("rules") if isinstance(document, dict) else None
    if not isinstance(rules, list) or not rules:
        raise ValueError("Rules must contain a non-empty 'rules' array.")
    seen = set()
    for rule in rules:
        required = ("id", "severity", "pattern", "message", "remediation", "source")
        if not isinstance(rule, dict) or any(not isinstance(rule.get(k), str) for k in required):
            raise ValueError("Each rule needs string id, severity, pattern, message, remediation and source.")
        if rule["id"] in seen:
            raise ValueError("Rule identifiers must be unique.")
        seen.add(rule["id"])
        if rule.get("auto_fix") not in GRAPHQL_ACTIONS | {None}:
            raise ValueError("Unsupported automatic edit action.")
        if "extensions" in rule and (not isinstance(rule["extensions"], list)
                or any(not isinstance(ext, str) or not ext.startswith(".") for ext in rule["extensions"])):
            raise ValueError("Rule extensions must be a list of dotted file extensions.")
        if "regex" in rule:
            re.compile(rule["regex"])
    return rules


def iter_files(root: Path, summary: ScanSummary | None = None) -> Iterable[Path]:
    ignored = {".git", ".breakguard", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}

    def fail(error):
        raise error

    for parent, dirs, files in os.walk(root, followlinks=False, onerror=fail):
        kept = []
        for name in sorted(dirs):
            path = Path(parent) / name
            if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
                if summary:
                    summary.symlinks_skipped += 1
            elif name not in ignored and not name.endswith(".egg-info"):
                kept.append(name)
        dirs[:] = kept
        for name in sorted(files):
            path = Path(parent) / name
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or not path.resolve().is_relative_to(root.resolve()):
                if summary:
                    summary.symlinks_skipped += 1
                continue
            if stat.S_ISREG(info.st_mode):
                yield path


def _rule_applies_to_path(path: Path, rule: dict) -> bool:
    if any(part in rule.get("exclude_path_parts", []) for part in path.parts):
        return False
    if rule.get("exclude_test_files") and re.search(r"(?:^test_|_test\.|\.(?:test|spec)\.)", path.name):
        return False
    extensions = rule.get("extensions")
    return not extensions or path.suffix.lower() in {ext.lower() for ext in extensions}


def _context_matches(lines: list[str], index: int, rule: dict) -> bool:
    context_before = rule.get("context_before")
    if context_before:
        start = max(0, index - int(rule.get("context_max_lines", 12)))
        return any(context_before in candidate for candidate in lines[start:index + 1])
    return not rule.get("context") or rule["context"] in "\n".join(lines)


def _finding(rule, rel, line, auto_fix=None, review_reason=None, prefix=""):
    return Finding(rule["id"], rule["severity"], rel, line, prefix + rule["message"],
                   rule["remediation"], rule["source"], auto_fix, review_reason)


def scan_repository(root: Path, rules: list[dict]) -> ScanResult:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Repository must be an existing directory.")
    findings = []
    summary = ScanSummary()
    field_rules = [r for r in rules if r.get("auto_fix") in GRAPHQL_ACTIONS]
    for path in iter_files(root, summary):
        summary.files_seen += 1
        rel_path = path.relative_to(root)
        rel = str(rel_path)
        selected = [r for r in rules if _rule_applies_to_path(rel_path, r)]
        embedded_eligible = bool(field_rules) and path.suffix.lower() in JS_EXTENSIONS | {".rb"}
        if not selected and not embedded_eligible:
            summary.files_unsupported += 1
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            summary.non_utf8_skipped += 1
            continue
        summary.files_scanned += 1
        lines = text.splitlines()
        fields = query_fields(text) if any(r.get("auto_fix") in GRAPHQL_ACTIONS for r in selected) else None
        if fields is None and path.suffix.lower() in {".graphql", ".gql"}:
            summary.unparseable_graphql_files += 1
        for rule in selected:
            action = rule.get("auto_fix")
            if action in GRAPHQL_ACTIONS and fields is not None:
                matched = [f for f in fields if matches_action(f, action)]
                edits = plan_edits(text, {(f.line, action) for f in matched}, fields)
                matched_counts = Counter(f.line for f in matched)
                edit_counts = Counter(edit.line for edit in edits)
                for field in matched:
                    safe = edit_counts[field.line] == matched_counts[field.line]
                    findings.append(_finding(rule, rel, field.line, action if safe else None,
                        None if safe else "Ambiguous or unsupported GraphQL edit; review query and response consumers."))
                continue
            for index, line in enumerate(lines):
                if line.lstrip().startswith(("#", "//", "*", "/*")):
                    continue
                matched = re.search(rule["regex"], line) if rule.get("regex") else rule["pattern"] in line
                if not matched or not _context_matches(lines, index, rule):
                    continue
                malformed = action in GRAPHQL_ACTIONS
                findings.append(_finding(rule, rel, index + 1,
                    review_reason="Unparseable GraphQL document." if malformed else "Manual migration required; source pattern only.",
                    prefix="Potential match in an unparseable GraphQL document; confirm manually. " if malformed else ""))
        if embedded_eligible:
            for document in extract_documents(text, path.suffix.lower()):
                embedded_fields = None if document.dynamic else query_fields(document.text)
                if embedded_fields is None:
                    summary.embedded_documents_skipped += 1
                    continue
                summary.embedded_documents_scanned += 1
                for rule in field_rules:
                    for field in embedded_fields:
                        if matches_action(field, rule["auto_fix"]):
                            findings.append(_finding(rule, rel, document.first_line + field.line - 1,
                                review_reason="Embedded GraphQL is detection-only; review and edit manually.",
                                prefix="Embedded GraphQL; manual review. "))
    return ScanResult(findings, summary)


def scan(root: Path, rules: list[dict]) -> list[Finding]:
    return scan_repository(root, rules).findings
