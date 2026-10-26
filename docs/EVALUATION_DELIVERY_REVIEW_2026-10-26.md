# Evaluation delivery review — October 26, 2026

Base: integrated product commit `a711aad687018cc25b8a5919a30c25d1c2929824`.
Branch: `work/evaluation-delivery-2026-10-26`. This is a prepared local change,
not an integrated or distributed release. The previously sent free kit is frozen.

## Concrete problem and change

The existing builder compared every new wheel with a historical 75-test wheel
hash, so it refused the current GBP 42 build. Its generated text still described
an unmerged source, EUR 49, pending platform checks and a private commercial
review bundle. The delivered free kit had been assembled separately, making
future delivery difficult to reproduce from the repository.

The builder now compares every wheel runtime/rule file with the exact committed
source and pins the dependency by SHA-256. It builds only an explicit technical
allowlist with EN/RO instructions, actual offline installers, integrity verifier,
synthetic examples and an empty independent feedback record. It includes no
seller intake, invoice, recipient record, commercial terms or internal patch.
Archives carry the source prefix, have repeatable bytes from identical inputs
and cannot overwrite an existing file.

The tester protocol now asks about independent usefulness without putting a
price question into the free evaluation. The README/readiness record separate
the integrated 88-test source from the earlier delivered 85-test wheel.

## Verification and limits

Twelve packaging/integrity regression tests passed; the complete local suite
passed **100 tests** on Linux/Python 3.12. The new actual-installer protocol builds
and extracts a ZIP outside the checkout, checks installed runtime hashes, then
checks scan → preview → apply → rescan → restore, later-edit refusal, manual
findings and skipped dynamic coverage. Record its actual output separately.

The existing hosted external-install job is extended to run that protocol on
Ubuntu/macOS/Windows. Those new steps have not run on GitHub at preparation time.
The local Linux result must not be presented as a new Windows/macOS result.
Scanner/edit/backup/payment runtime code and the three rules are unchanged.

No Shopify application has been executed by this packaging review. No independent
Shopify developer has completed the usefulness protocol. No actual Sandbox
transaction, payment activation, revenue, publication or external message is
established by these changes. Seller eligibility and commercial terms remain
separate gates. The private web prototype remains private.

## Proposed review and integration

1. Review the exact patch, allowlisted delivery and local evidence.
2. With Founder approval, publish the branch/PR and require the six exact-head
   GitHub checks, including the new offline installer step on all three OSes.
3. Integrate only the approved passing head; verify the resulting product checks.
4. Rebuild from that integrated commit before any separately approved delivery.
5. Complete the 30–60 minute independent Shopify test and record usefulness,
   application test outcomes and unsupported cases before making paid promises.
