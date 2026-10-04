# BreakGuard V0.1 Release Candidate Checklist

Status: **0.1.0rc1 — ready for controlled external testing**

## Completed

- [x] installable CLI
- [x] packaged rules
- [x] scan-only mode
- [x] JSON output
- [x] non-destructive fix preview
- [x] conservative autofix
- [x] official-source metadata for current Shopify rules
- [x] false-positive reduction by source extension and nearby context
- [x] Git safety guards
- [x] automated verification before Draft PR creation
- [x] Draft PR generated end-to-end by GitHub Actions
- [x] Ubuntu external install smoke test
- [x] macOS external install smoke test
- [x] Windows external install smoke test
- [x] Python 3.10 / 3.11 / 3.12 CI matrix
- [x] external tester guide
- [x] fresh release-candidate end-to-end Draft PR validation (PR #5)

## Before final 0.1.0

- [ ] test against at least one real external Shopify repository or anonymized representative repository
- [ ] review tester feedback for false positives / missed detections
- [ ] decide whether to publish a public package or distribute through GitHub first
- [ ] final legal/product wording review before public commercial launch

No automatic merge is permitted in V0.1.
