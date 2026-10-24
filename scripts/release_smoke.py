"""Cross-platform installed-package smoke test, using synthetic temporary files."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile


def main():
    with tempfile.TemporaryDirectory(prefix="breakguard-smoke-") as temporary:
        base = Path(temporary)
        repo = base / "project"
        repo.mkdir()
        originals = {
            "customer.graphql": b"query Buyer { customer { id lastIncompleteCheckout { id } } }\r\n",
            "warning.graphql": b"fragment D on DraftOrderDiscountNotAppliedWarning { priceRule { title } }\n",
            "legacy.js": b"const m = `mutation M($input: ScriptTagInput!) { scriptTagCreate(input: $input) { scriptTag { id } } }`;\n",
        }
        for name, content in originals.items():
            (repo / name).write_bytes(content)

        def run(*arguments, expected):
            result = subprocess.run([sys.executable, "-m", "breakguard.cli", str(repo), *map(str, arguments)],
                                    cwd=base, text=True, capture_output=True)
            assert result.returncode == expected, (result.returncode, result.stdout, result.stderr)
            return result

        initial = json.loads(run("--json", expected=1).stdout)
        assert len(initial) == 3
        preview = run("--fix-preview", expected=1)
        assert "Previewed files: 2" in preview.stdout
        assert all((repo / name).read_bytes() == data for name, data in originals.items())
        report = base / "after.json"
        assert len(json.loads(run("--apply-fixes", "--json", "--report", report, expected=1).stdout)) == 1
        record = json.loads(report.read_text())
        assert len(record["changed_files"]) == 2 and record["backup_id"]
        assert (repo / "legacy.js").read_bytes() == originals["legacy.js"]
        run("--restore", record["backup_id"], expected=1)
        assert all((repo / name).read_bytes() == data for name, data in originals.items())
        report2 = base / "second.json"
        run("--apply-fixes", "--report", report2, expected=1)
        later = b"# developer's later edit\n" + (repo / "customer.graphql").read_bytes()
        (repo / "customer.graphql").write_bytes(later)
        run("--restore", json.loads(report2.read_text())["backup_id"], expected=2)
        assert (repo / "customer.graphql").read_bytes() == later
        simulation = subprocess.run([sys.executable, "-m", "breakguard.pilot_payments", "--simulate"],
                                    cwd=base, text=True, capture_output=True, check=True)
        payment = json.loads(simulation.stdout)
        assert payment["mode"] == "OFFLINE_SIMULATION" and payment["network_calls"] == 0
        print(json.dumps({"installed_cli": "passed", "initial_findings": 3,
                          "previewed_and_changed_files": 2, "remaining_manual_findings": 1,
                          "exact_restore": True, "later_edit_protected": True,
                          "payment_simulation": "offline only"}, indent=2))


if __name__ == "__main__":
    main()
