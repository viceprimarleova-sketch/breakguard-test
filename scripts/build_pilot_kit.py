"""Build a private review/delivery ZIP from reviewed local artifacts; no upload."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import zipfile

VERSION = "0.1.0rc2"
BASE = "788c3b6e3f805a0d39e0593d08bef9fcf7ca6eba"

START_RO = r"""# BreakGuard V0.1 — pachet pentru revizuire și testare

Versiune: **0.1.0rc2**. Candidat funcțional; lansarea comercială nu este aprobată.
Codul nou este într-o ramură locală, fără integrare sau publicare pe GitHub.

## Ce este în pachet

- Programul instalabil și dependența sa, pentru instalare fără descărcări pip.
- Exemple sintetice, ghid pentru un dezvoltator Shopify și formular de feedback.
- Raport de acoperire, previzualizare, aplicare și revenire cu protecția editărilor ulterioare.
- Oferta propusă: **49 EUR, o singură dată**, un repository, maximum 1.000 de fișiere eligibile,
  două schimburi de suport în șapte zile. Prețul, suportul și tratamentul taxelor așteaptă aprobarea Fondatorului.
- Condiții comerciale/confidențialitate în variantă de lucru, nu contract final.
- Simulare de plată locală și adaptor PayPal exclusiv Sandbox, fără plăți reale.
- Modificările complete în `review/changes.patch` și identificatorul codului în `CANDIDATE.json`.

## Instalare Windows

Ai nevoie de Python 3.10 sau mai nou. Această variantă a fost verificată local pe Linux/Python 3.12;
verificările Windows/macOS pentru noul cod sunt încă de rulat. Dezarhivează într-un folder nou.
În PowerShell, deschide acel folder și execută:

```powershell
.\install_windows.cmd
.\.venv\Scripts\breakguard.exe --version
```

Installerul creează doar mediul `.venv` din acest folder și folosește roțile din `wheels`.
Nu cere Git, parole, cod privat sau acces la magazine. Nu trebuie activat mediul PowerShell.

## Test demonstrativ Windows

```powershell
.\.venv\Scripts\breakguard.exe demo_project --report before.json
.\.venv\Scripts\breakguard.exe demo_project --fix-preview
.\.venv\Scripts\breakguard.exe demo_project --apply-fixes --report after.json
```

Așteptat: **3 constatări → 2 fișiere modificate → 1 caz ScriptTag manual**.
Programul afișează identificatorul copiei de siguranță. Copiază-l în locul textului BACKUP_ID:

```powershell
.\.venv\Scripts\breakguard.exe demo_project --restore BACKUP_ID
```

După revenire apar din nou cele 3 constatări. Codul de ieșire **1** este normal când există constatări;
**2** înseamnă eroare. Rapoartele cer nume noi și nu suprascriu fișiere existente.
Nu modifica simultan sursele și copiile de siguranță. O editare ulterioară produce refuzul revenirii,
ca să fie păstrată munca dezvoltatorului. Copiile din `.breakguard` conțin surse și rămân locale.

`manual_cases` are 3 cazuri exclusiv manuale: customer cu o singură selecție, o interogare TypeScript
și un fragment Ruby. `coverage_cases` are o interogare dinamică ce trebuie raportată ca neverificată.

Testul automat complet al pachetului folosește numai fișiere temporare sintetice:

```powershell
.\.venv\Scripts\python.exe scripts\release_smoke.py
.\.venv\Scripts\python.exe -m breakguard.pilot_payments --simulate
```

Ultima comandă este o **simulare fără rețea și fără bani**. Nu este o tranzacție PayPal Sandbox.
Pentru Linux/macOS: `sh install_unix.sh`, apoi folosește `.venv/bin/breakguard` și `.venv/bin/python`.

## Ce mai trebuie confirmat

1. Rularea CI pe codul nou și evaluarea unui dezvoltator Shopify pe un caz relevant, cu testele propriei aplicații.
2. O tranzacție Sandbox reală, după configurarea sigură a accesului de test de către proprietar.
3. Identitatea și jurisdicția vânzătorului, condițiile/prețul total și aprobarea publicării/integrării.
4. Implementarea/aprobarea unui checkout real și obținerea unui client care acceptă oferta.

Cele 75 de teste locale și exemplele publice sunt dovezi tehnice. Utilitatea comercială,
acceptarea prețului și veniturile nu sunt încă validate. Site-ul demonstrativ privat rămâne separat.
"""

WINDOWS_INSTALL = r"""@echo off
setlocal
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip --disable-pip-version-check install --no-index --find-links "wheels" breakguard==0.1.0rc2
if errorlevel 1 exit /b 1
".venv\Scripts\breakguard.exe" --version
"""

UNIX_INSTALL = """#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
python3 -m venv .venv
.venv/bin/python -m pip --disable-pip-version-check install --no-index --find-links wheels breakguard==0.1.0rc2
.venv/bin/breakguard --version
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]

    def git(*arguments):
        return subprocess.run(["git", *arguments], cwd=repo, check=True, text=True, capture_output=True).stdout.strip()

    if git("status", "--porcelain"):
        raise SystemExit("Commit the reviewed changes locally before building the kit.")
    candidate = git("rev-parse", "HEAD")
    evidence = json.loads((repo / "docs/audit-results-2026-10-25.json").read_text())
    wheel = args.wheel_dir / f"breakguard-{VERSION}-py3-none-any.whl"
    if hashlib.sha256(wheel.read_bytes()).hexdigest() != evidence["wheel_sha256"]:
        raise SystemExit("The wheel differs from the audited candidate.")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    kit = args.out_dir / f"BreakGuard_V01_{VERSION}"
    kit.mkdir()
    (kit / "wheels").mkdir()
    for name in (wheel.name, "graphql_core-3.2.13-py3-none-any.whl"):
        shutil.copy2(args.wheel_dir / name, kit / "wheels" / name)
    (kit / "docs").mkdir()
    for name in ("PILOT_READINESS.md", "PILOT_OFFER_DRAFT.md", "PILOT_TERMS_DRAFT.md", "PAYMENT_TESTING.md",
                 "FEEDBACK_TEMPLATE.md", "AUDIT_2026-10-25.md", "audit-results-2026-10-25.json"):
        shutil.copy2(repo / "docs" / name, kit / "docs" / name)
    shutil.copy2(repo / "README.md", kit / "README_EN.md")
    shutil.copy2(repo / "TESTER_GUIDE.md", kit / "TESTER_GUIDE.md")
    shutil.copy2(repo / "RELEASE_CANDIDATE.md", kit / "RELEASE_CANDIDATE.md")
    (kit / "scripts").mkdir()
    shutil.copy2(repo / "scripts/release_smoke.py", kit / "scripts/release_smoke.py")
    (kit / "START_HERE_RO.md").write_text(START_RO, encoding="utf-8")
    (kit / "install_windows.cmd").write_bytes(WINDOWS_INSTALL.replace("\n", "\r\n").encode())
    (kit / "install_unix.sh").write_text(UNIX_INSTALL, encoding="utf-8")
    examples = {
        "demo_project/customer.graphql": "query Buyer { customer { id lastIncompleteCheckout { id } } }\n",
        "demo_project/warning.graphql": "fragment Discount on DraftOrderDiscountNotAppliedWarning { priceRule { title } }\n",
        "demo_project/legacy.js": "// Synthetic query string; never sent to a store.\nconst m = `mutation Demo($input: ScriptTagInput!) { scriptTagCreate(input: $input) { scriptTag { id } } }`;\n",
        "manual_cases/customer_only.graphql": "query Buyer { customer { lastIncompleteCheckout { id } } }\n",
        "manual_cases/customer.ts": "const q = `#graphql\nquery Buyer { customer { id lastIncompleteCheckout { id } } }`;\n",
        "manual_cases/discount.rb": "QUERY = <<~QUERY\nfragment Discount on DraftOrderDiscountNotAppliedWarning { priceRule { title } }\nQUERY\n",
        "coverage_cases/dynamic.ts": "const q = `#graphql\nquery Buyer { customer { ${selection} } }`;\n",
        "coverage_cases/notes.txt": "Unsupported file type; not examined by these source rules.\n",
    }
    for name, text in examples.items():
        path = kit / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    (kit / "review").mkdir()
    patch = subprocess.run(["git", "diff", "--binary", BASE, candidate], cwd=repo, check=True, capture_output=True).stdout
    (kit / "review/changes.patch").write_bytes(patch)
    (kit / "review/PR_DESCRIPTION.md").write_text(
        "# Prepare rc2 pilot workflow with coverage and local restore\n\n"
        "Adds detection-only embedded GraphQL coverage, explicit error/report behavior, local snapshots and "
        "conflict-aware restore. Protects existing review branches. Prepares a bounded pilot offer and "
        "test-only payment adapter.\n\n"
        "Validation: 75 installed-wheel tests on Linux/Python 3.12; clean offline installation and full "
        "synthetic workflow; two pinned public Shopify snapshots scanned read-only. Hosted rc2 platform "
        "checks, developer usefulness, actual PayPal Sandbox and commercial approvals remain open.\n\n"
        "Based on PR #6's correction commit; integrate that review series in order after approval. "
        "No automatic merge, publication, outreach, live payments or web-visibility change.\n", encoding="utf-8")
    identity = {"version": VERSION, "source_commit": candidate, "base_commit": BASE,
                "branch": git("branch", "--show-current"), "publication": "local review only",
                "commercial_launch": False, "actual_paypal_sandbox_tested": False,
                "wheel_sha256": evidence["wheel_sha256"]}
    (kit / "CANDIDATE.json").write_text(json.dumps(identity, indent=2) + "\n")
    with zipfile.ZipFile(args.wheel_dir / "graphql_core-3.2.13-py3-none-any.whl") as dependency:
        license_name = next(name for name in dependency.namelist() if name.endswith("/licenses/LICENSE"))
        (kit / "GRAPHQL_CORE_LICENSE.txt").write_bytes(dependency.read(license_name))
    checksums = []
    for path in sorted(kit.rglob("*")):
        if path.is_file():
            checksums.append(hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.relative_to(kit).as_posix())
    (kit / "SHA256SUMS.txt").write_text("\n".join(checksums) + "\n")
    archive = args.out_dir / f"BreakGuard_V01_Pilot_Review_{VERSION}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(kit.rglob("*")):
            if path.is_file():
                bundle.write(path, kit.name + "/" + path.relative_to(kit).as_posix())
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
    print(json.dumps({"archive": str(archive.resolve()), "bytes": archive.stat().st_size,
                      "candidate": candidate, "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
