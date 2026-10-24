"""Local edit snapshots and conflict-aware restoration, never networked."""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(root: Path, relative: str, must_exist=True) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or ".." in rel.parts:
        raise ValueError("Refusing a path outside the repository.")
    path = root
    for part in rel.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("Refusing to follow a symbolic link.")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Refusing a path outside the repository.")
    if must_exist and not path.is_file():
        raise ValueError("Expected a regular repository file.")
    return path


def atomic_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=".breakguard-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _save_manifest(directory: Path, manifest: dict):
    atomic_write(directory / "manifest.json", (json.dumps(manifest, indent=2) + "\n").encode())


def save_and_apply(root: Path, changes: dict[str, tuple[bytes, bytes]]) -> str:
    root = root.resolve(strict=True)
    base = safe_path(root, ".breakguard/backups", must_exist=False)
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    # Backups contain original source. Keep them out of accidental git adds.
    ignore = root / ".breakguard" / ".gitignore"
    if ignore.is_symlink():
        raise ValueError("Refusing a symlink in the backup directory.")
    if not ignore.exists():
        with ignore.open("x", encoding="utf-8") as stream:
            stream.write("*\n")
    backup_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid4().hex[:12]
    directory = base / backup_id
    directory.mkdir(mode=0o700)
    manifest = {"schema_version": 1, "repository": str(root), "state": "prepared", "files": []}
    for relative, (original, updated) in changes.items():
        path = safe_path(root, relative)
        if path.read_bytes() != original:
            raise ValueError("A source file changed while preparing edits; no edits applied.")
        copy = directory / "files" / relative
        copy.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with copy.open("xb") as stream:
            stream.write(original)
        os.chmod(copy, 0o600)
        manifest["files"].append({"path": relative, "before": digest(original),
                                  "after": digest(updated), "mode": stat.S_IMODE(path.stat().st_mode)})
    _save_manifest(directory, manifest)
    applied = []
    try:
        for entry in manifest["files"]:
            relative = entry["path"]
            path = safe_path(root, relative)
            if digest(path.read_bytes()) != entry["before"]:
                raise ValueError("A source file changed before writing; edit aborted.")
            atomic_write(path, changes[relative][1], entry["mode"])
            applied.append(entry)
        manifest["state"] = "applied"
        _save_manifest(directory, manifest)
    except (OSError, ValueError):
        for entry in reversed(applied):
            path = safe_path(root, entry["path"])
            if digest(path.read_bytes()) == entry["after"]:
                atomic_write(path, changes[entry["path"]][0], entry["mode"])
        manifest["state"] = "failed"
        _save_manifest(directory, manifest)
        raise
    return backup_id


def restore_backup(root: Path, backup_id: str) -> list[str]:
    root = root.resolve(strict=True)
    if not re.fullmatch(r"\d{8}T\d{6}Z-[a-f0-9]{12}", backup_id):
        raise ValueError("Use the backup identifier printed by --apply-fixes.")
    directory = safe_path(root, ".breakguard/backups/" + backup_id, must_exist=False)
    manifest_path = safe_path(directory, "manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("repository") != str(root):
        raise ValueError("Backup does not belong to this repository.")
    if manifest.get("state") != "applied":
        raise ValueError("Backup is not in the applied state; review it manually.")
    entries = manifest.get("files")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Invalid backup manifest.")
    ready = []
    for entry in entries:
        path = safe_path(root, entry["path"])
        original = safe_path(directory / "files", entry["path"]).read_bytes()
        if digest(original) != entry["before"]:
            raise ValueError("Backup content failed its integrity check.")
        if digest(path.read_bytes()) != entry["after"]:
            raise ValueError("A file was edited after BreakGuard; restore refused to preserve later work.")
        ready.append((path, original, path.read_bytes(), entry["mode"]))
    restored = []
    try:
        for path, original, current, mode in ready:
            if path.read_bytes() != current:
                raise ValueError("A file changed during restore; refusing to overwrite it.")
            atomic_write(path, original, mode)
            restored.append((path, current, mode))
        manifest["state"] = "restored"
        _save_manifest(directory, manifest)
    except (OSError, ValueError):
        for path, current, mode in reversed(restored):
            original = next(original for candidate, original, _, _ in ready if candidate == path)
            if path.read_bytes() == original:
                atomic_write(path, current, mode)
        raise
    return [entry["path"] for entry in entries]
