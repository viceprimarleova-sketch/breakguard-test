# Backup ignore follow-up — prepared for approval

Base: published Draft PR #6 at `19dcd421ba62fc7d28d9225f69a2147e65921c1e`.
The six hosted checks passed on that base. This small follow-up is local and has
not been published or integrated; its hosted checks are still pending.

## Reproduced issue

When a project already had `.breakguard/.gitignore` with no ignore pattern (or
with rules re-including backups), the earlier candidate preserved that file but
did not independently protect new snapshots. `git ls-files --others
--exclude-standard -- .breakguard/backups` listed the saved original source and
manifest. This was reproduced using synthetic temporary files, with no upload,
staging of originals or observed private-source disclosure.

## Correction

Each newly created snapshot now gets its own `.gitignore` containing `*` before
any original is copied. The project's existing configuration is left unchanged.
The two regression cases failed on the published base and pass with the fix;
restoring the original source remains verified. The protection covers ordinary
Git staging candidates, not an explicit forced add or files already tracked.
Older snapshots and existing Git history are unchanged; check those locally
before staging if the earlier build was used with custom ignore settings.

## Validation

- 77 tests passed against a separately installed wheel with isolated imports on
  Linux / Python 3.12, including both new regression cases.
- The full installed-package synthetic smoke passed: scan/preview/apply/report,
  exact restore, later-edit protection and offline payment demonstration.
- All installed Python module and rule bytes match the reviewed source.
- The wheel/hash record is `backup-ignore-review-2026-10-25.json`.

No new rule families, payment functionality or application compatibility claims
are introduced. The Founder must approve publication before this follow-up is
added to the public review branch. Final integration is a separate approval.
