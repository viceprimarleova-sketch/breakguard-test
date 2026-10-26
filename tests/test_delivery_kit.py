"""Delivery regressions: source identity, private-file exclusion and integrity."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_script(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_script("delivery_builder", ROOT / "scripts/build_pilot_kit.py")
verifier = load_script("delivery_verifier", ROOT / "evaluation/verify_kit.py")


def commit(repo):
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run([
        "git", "-c", "user.name=Delivery Test", "-c", "user.email=delivery@example.invalid",
        "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false", "commit", "-qm", "fixture",
    ], cwd=repo, check=True, capture_output=True)


def rewrite_wheel(path, replacements):
    with zipfile.ZipFile(path) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    files.update(replacements)
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)


@pytest.fixture
def inputs(tmp_path):
    repo, wheels = tmp_path / "source", tmp_path / "wheels"
    repo.mkdir()
    wheels.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=repo, check=True)
    (repo / "breakguard/rules").mkdir(parents=True)
    (repo / "breakguard/__init__.py").write_bytes(b'__version__ = "0.1.0rc2"\n')
    (repo / "breakguard/scanner.py").write_bytes(b"# current reviewed code\n")
    (repo / "breakguard/rules/current.json").write_bytes(b'{"rules": []}\n')
    shutil.copytree(ROOT / "evaluation", repo / "evaluation", ignore=shutil.ignore_patterns("__pycache__"))
    for source in builder.TECHNICAL_FILES:
        target = repo / source
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)
    # These deliberately committed files must never enter the delivery allowlist.
    (repo / "docs/PRIVATE_SELLER_INTAKE.md").write_text("PRIVATE-SELLER-SENTINEL")
    (repo / "docs/PILOT_TERMS_DRAFT.md").write_text("PRIVATE-TERMS-SENTINEL")
    dependency = wheels / "graphql_core-3.2.13-py3-none-any.whl"
    with zipfile.ZipFile(dependency, "w") as archive:
        archive.writestr("graphql_core-3.2.13.dist-info/licenses/LICENSE", "MIT test fixture")
    lock_path = repo / "evaluation/DEPENDENCY_LOCK.json"
    lock = json.loads(lock_path.read_text())
    lock["sha256"] = hashlib.sha256(dependency.read_bytes()).hexdigest()
    lock_path.write_text(json.dumps(lock), encoding="utf-8")
    wheel = wheels / "breakguard-0.1.0rc2-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        for path in sorted((repo / "breakguard").rglob("*")):
            if path.is_file():
                archive.writestr(path.relative_to(repo).as_posix(), path.read_bytes())
        prefix = "breakguard-0.1.0rc2.dist-info/"
        for name, data in {
            "METADATA": "Metadata-Version: 2.4\nName: breakguard\nVersion: 0.1.0rc2\n",
            "WHEEL": "Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
            "entry_points.txt": "[console_scripts]\nbreakguard = breakguard.cli:main\n",
            "top_level.txt": "breakguard\n", "RECORD": "",
        }.items():
            archive.writestr(prefix + name, data)
    commit(repo)
    return repo, wheels, wheel, tmp_path


def unpack(result, destination):
    with zipfile.ZipFile(result["archive"]) as archive:
        archive.extractall(destination)
    return next(destination.iterdir())


def test_delivery_is_repeatable_pins_runtime_and_excludes_internal_files(inputs):
    repo, wheels, _, base = inputs
    first = builder.build_kit(repo, wheels, base / "first")
    second = builder.build_kit(repo, wheels, base / "second")
    assert Path(first["archive"]).read_bytes() == Path(second["archive"]).read_bytes()
    kit = unpack(first, base / "extracted")
    identity = json.loads((kit / "EVALUATION_IDENTITY.json").read_text())
    assert identity["source_commit"] == builder.git(repo, "rev-parse", "HEAD").decode().strip()
    assert identity["payment_required"] is False
    assert identity["runtime_sha256"]["breakguard/scanner.py"] == hashlib.sha256(
        (repo / "breakguard/scanner.py").read_bytes()).hexdigest()
    assert not (kit / "docs/PRIVATE_SELLER_INTAKE.md").exists()
    assert not (kit / "docs/PILOT_TERMS_DRAFT.md").exists()
    assert all(b"PRIVATE-" not in path.read_bytes() for path in kit.rglob("*") if path.is_file())
    assert verifier.verify(kit)["delivered_files_checked"] == first["manifest_files"]


@pytest.mark.parametrize("source", ["breakguard/scanner.py", "breakguard/rules/current.json"])
def test_old_same_version_code_or_rules_cannot_be_packaged(inputs, source):
    repo, wheels, _, base = inputs
    (repo / source).write_bytes(b"# new reviewed content\n")
    commit(repo)
    with pytest.raises(ValueError, match="Wheel source mismatch"):
        builder.build_kit(repo, wheels, base / "out")
    assert not (base / "out").exists()


def test_unexpected_installed_payload_is_not_delivered(inputs):
    repo, wheels, wheel, base = inputs
    rewrite_wheel(wheel, {"unexpected.pth": b"import unexpected\n"})
    with pytest.raises(ValueError, match="payload differs"):
        builder.build_kit(repo, wheels, base / "out")


def test_changed_dependency_is_refused_before_delivery(inputs):
    repo, wheels, _, base = inputs
    (wheels / "graphql_core-3.2.13-py3-none-any.whl").write_bytes(b"changed dependency")
    with pytest.raises(ValueError, match="Dependency wheel checksum mismatch"):
        builder.build_kit(repo, wheels, base / "out")


@pytest.mark.parametrize("name", ["TESTER_GUIDE.md", "untracked.txt"])
def test_uncommitted_input_is_refused(inputs, name):
    repo, wheels, _, base = inputs
    (repo / name).write_text("unreviewed change", encoding="utf-8")
    with pytest.raises(ValueError, match="Commit the reviewed local changes"):
        builder.build_kit(repo, wheels, base / "out")


def test_existing_archive_is_never_overwritten_or_removed(inputs):
    repo, wheels, _, base = inputs
    first = builder.build_kit(repo, wheels, base / "out")
    original = Path(first["archive"]).read_bytes()
    with pytest.raises(FileExistsError):
        builder.build_kit(repo, wheels, base / "out")
    assert Path(first["archive"]).read_bytes() == original


@pytest.mark.parametrize("change", ["changed", "missing", "additional"])
def test_delivery_verifier_refuses_changed_missing_or_additional_files(inputs, change):
    repo, wheels, _, base = inputs
    kit = unpack(builder.build_kit(repo, wheels, base / "out"), base / "extracted")
    if change == "changed":
        (kit / "README_EN.md").write_text("changed")
    elif change == "missing":
        (kit / "wheels/breakguard-0.1.0rc2-py3-none-any.whl").unlink()
    else:
        (kit / "INTERNAL_NOTE.md").write_text("should not be delivered")
    with pytest.raises(ValueError, match="Checksum mismatch|Missing or additional"):
        verifier.verify(kit)


def test_delivery_verifier_refuses_source_symlinks(inputs):
    repo, wheels, _, base = inputs
    kit = unpack(builder.build_kit(repo, wheels, base / "out"), base / "extracted")
    link = kit / "linked.txt"
    try:
        link.symlink_to(kit / "README_EN.md")
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks requires OS permissions")
    with pytest.raises(ValueError, match="symbolic link"):
        verifier.verify(kit)
