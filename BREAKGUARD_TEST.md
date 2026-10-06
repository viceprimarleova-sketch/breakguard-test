# BreakGuard E2E Fixture

This branch intentionally contains Shopify API patterns that BreakGuard should flag.

Expected findings:
- Customer.lastIncompleteCheckout
- DraftOrderDiscountNotAppliedWarning.priceRule
- legacy ScriptTag usage

The first two are intended to be auto-fixable in BreakGuard V0.1.
ScriptTag should remain manual review.
