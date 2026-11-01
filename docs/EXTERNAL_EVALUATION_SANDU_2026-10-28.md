# External evaluation evidence — Sandu — October 28, 2026

## Evaluator profile and limits

Sandu completed a guided evaluation on Windows and explicitly stated that he
does not specialise in Shopify projects. This is useful evidence about basic
installation, CLI usability and the clarity of the demonstration, but it is
not an independent Shopify-domain review and does not satisfy the specialist
validation gate in `PILOT_READINESS.md`.

## Initial friction

The evaluator initially reported that the Windows installer and subsequent
commands were not recognised. The command transcript showed commands being
entered in a way that caused PowerShell to interpret paths such as
`.venv\Scripts\python.exe` as module names. This is evidence of an
onboarding/documentation friction point, not proof of a product-code defect.
The evaluator later completed the demo workflow successfully.

## Successful demonstration reported by evaluator

The evaluator supplied output from:

```powershell
.\.venv\Scripts\breakguard.exe demo_project --restore
```

The reported output included:

- Three findings across three scanned files:
  - `Customer.lastIncompleteCheckout` in a Customer Account GraphQL query.
  - Potential ScriptTag create/update usage, explicitly marked for manual review.
  - Removed `DraftOrderDiscountNotAppliedWarning.priceRule` field.
- Official Shopify migration/changelog references for the findings.
- A coverage limitation warning: no finding is not a Shopify API compatibility
  certificate.
- `Restored files: 2` after the restore command.

The evaluator's earlier test messages also document that he progressed through
installation, preview/apply and restoration steps. This report records the
specific final restore output and findings that were supplied by email; it
does not claim a separate observation of his machine or independently reproduce
his run.

## What this evidence establishes

- A non-specialist Windows evaluator was able to get past the initial command
  invocation problem and complete the supplied synthetic demonstration.
- The demonstration communicated three narrow findings, official guidance,
  the manual ScriptTag boundary and the coverage limitation.
- The restore command reported restoration of two files.

## What it does not establish

- Shopify specialist approval or correctness across real applications.
- That the findings saved meaningful time on a live developer task.
- Compatibility with arbitrary Shopify repositories or complete API coverage.
- Willingness to pay, commercial demand, deployment readiness or revenue.
- That the fresh integrated candidate ZIP has been independently installed;
  the run above must not be conflated with a new package acceptance test.

## Product and documentation actions

1. Keep the Windows quick-start commands explicit about opening PowerShell in
   the extracted package directory before running relative paths.
2. Present one command per step and show the expected output before continuing.
3. Include a short PowerShell-specific troubleshooting note for
   `CommandNotFoundException` and path/module interpretation errors.
4. Preserve the three-rule scope and clearly label ScriptTag as manual review.
5. Seek a Shopify specialist to review at least one real, consented project
   before making a paid-pilot readiness claim.

No additional external contact, public release, payment or commercial
commitment is authorised by this evidence note.
