# BreakGuard {{VERSION}} — free developer evaluation

An early local Python checker for three Shopify deprecation families. This
voluntary evaluation is free, with no subscription or purchase commitment.
No credentials, private source or store access are requested. Use a computer
with Python 3.10 or newer; a phone cannot run this CLI package.

## Install the exact delivery

Extract into a new folder. Open a terminal there and run:

Windows PowerShell:
```powershell
.\install_windows.cmd
.\.venv\Scripts\python.exe scripts\release_smoke.py
```

macOS / Linux:
```sh
sh install_unix.sh
.venv/bin/python scripts/release_smoke.py
```

The installer checks the delivered files before creating a local `.venv`, then
installs from the two included wheels, without downloading Python packages.
It deliberately reinstalls the build even over the same rc2 version number.
`EVALUATION_IDENTITY.json` records the exact source commit and wheel hashes;
the version number alone does not identify a build. To check delivery manually,
run `python3 verify_kit.py` (Windows: `py -3 verify_kit.py`). This checks delivered
files, excluding an installed `.venv`; SHA-256 is not a signed publisher identity.
Keep reports outside this folder and verify before changing the examples.

The smoke test uses temporary synthetic files: **3 findings → 2 guarded edits →
1 manual ScriptTag finding**, exact restore, and refusal to overwrite later edits.
It also runs the payment adapter's **offline fake**, with zero network calls and
no money. This is not a PayPal Sandbox transaction or a working live checkout.

## Scope and limits

| Family | Supported action |
| --- | --- |
| Customer Account `Customer.lastIncompleteCheckout` | Guarded removal in eligible standalone GraphQL; review response consumers |
| Admin `DraftOrderDiscountNotAppliedWarning.priceRule` | Guarded replacement in eligible standalone GraphQL; review response consumers |
| ScriptTag create/update patterns | Manual review only |

Static marked JS/TS GraphQL templates and recognized Ruby heredocs are
detection-only. Ambiguous fields, aliases and unsupported selections stay manual.
`manual_cases` has four manual findings and must receive no edits. `coverage_cases`
has a dynamic document that should be counted as skipped. Dynamic/unrecognized
queries, other languages, generated and ignored paths may be missed. Zero
findings does not certify Shopify API compatibility.

Edits validate GraphQL syntax, not Shopify schema compatibility or application
behavior. Independently confirm the actual API surface/version and response
consumers. Run the application's own tests; the CLI does not run them for you.
The dated `PUBLIC_SOURCE_NOTES.md` is read-only source evidence, not application
execution, independent developer acceptance or a commercial guarantee.

## Detect → preview → apply → verify → restore

Use a disposable clone or temporary clean Git branch. Replace `BG` below with
`.venv/bin/breakguard` or Windows `.venv\Scripts\breakguard.exe`:

```text
BG PROJECT --report ../before.json
BG PROJECT --fix-preview
BG PROJECT --apply-fixes --report ../after.json
BG PROJECT --report ../verify.json
BG PROJECT --restore BACKUP_ID
```

Use new report filenames. Exit `0`: no supported findings; `1`: findings remain;
`2`: error, stop and investigate. Review the preview before apply, compare the
diff afterwards, run the application's tests, then restore using the ID printed
during apply or `backup_id` in the report. Restore checks integrity and refuses
later edits. If refused, preserve the files and inspect manually; do not force
an overwrite. Backups contain unencrypted original source under
`.breakguard/backups` and must stay local.

## A useful independent test

Follow `TESTER_GUIDE.md` for a 30–60 minute session on code you understand.
The synthetic smoke proves only the controlled workflow. Independent Shopify
developer usefulness, real application safety and willingness to pay remain
unvalidated. Use the empty `FEEDBACK_TEMPLATE.md` for voluntary redacted feedback.
Do not send source, backups, secrets, store identifiers or unredacted paths.
No payment or paid-pilot decision is needed to complete this evaluation.
