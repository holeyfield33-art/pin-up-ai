# Privacy Policy — Pin-Up AI

**Last updated:** February 16, 2026

## Summary

Pin-Up AI is a **local-first** application. Your data stays on your machine. We do not collect, store, or transmit your snippets, tags, collections, or search queries to any server.

## What Data Stays Local

All of the following data is stored exclusively on your device:

- **Snippets** — All saved content, titles, bodies, and metadata
- **Tags & Collections** — Your organizational structure
- **Search queries** — Never leave your device
- **Settings & preferences** — Stored in local config
- **Database** — SQLite file on your filesystem
- **Backups** — Stored in your local backup directory
- **API token** — Generated locally, SHA-256 hashed, never transmitted

### Storage Locations

| Platform | Path |
|----------|------|
| macOS | `~/Library/Application Support/com.pinup-ai.app/` |
| Windows | `%APPDATA%/com.pinup-ai.app/` |
| Linux | `~/.config/com.pinup-ai.app/` |

## What We May Collect

### License Validation (Pro Users Only)

If you purchase a Pro license, the following minimal data is sent to our payment provider (Gumroad) for license validation:

- **License key** — To verify your purchase
- **Machine identifier** — A hashed, anonymous device ID for seat counting
- **No snippet content** is ever transmitted

This validation can occur:
- When you activate a license
- Periodically to verify license status (max once per 24 hours)
- You can use the app offline for up to 7 days without validation

### Crash Reporting (Opt-In Only)

If you enable crash reporting in Settings:
- Anonymous error reports may be sent
- Reports contain stack traces, OS version, and app version
- **No snippet content** is included in crash reports
- You can disable this at any time in Settings

### Update Checks

The app may check for updates via GitHub Releases:
- No personal data is sent
- Only your current app version is included in the request
- You can disable auto-update checks in Settings

## What We Never Collect

- Your snippet content
- Your search queries
- Your tags, collections, or organizational data
- Browsing history or usage patterns
- Personal identification information
- IP addresses (we have no server to log them)

## Third-Party Services

| Service | Purpose | Data Shared |
|---------|---------|-------------|
| Gumroad | License validation | License key, hashed machine ID |
| GitHub | Update checks | App version |
| Sentry | Crash reporting (opt-in) | Anonymous stack traces |

## Data Deletion

Since all data is local, you have complete control:

- **Delete all data:** Remove the application data directory listed above
- **Delete database:** Remove `pinup.db` from your data directory
- **Delete backups:** Remove the `backups/` subdirectory
- **Uninstall:** Standard OS uninstall process

## Children's Privacy

Pin-Up AI does not knowingly collect data from children under 13. The app does not collect personal data from any user.

## Changes to This Policy

We may update this privacy policy from time to time. Changes will be noted in the CHANGELOG and reflected in the "Last updated" date above.

## Contact

For privacy questions or concerns:
- GitHub: [holeyfield33-art/pin-up-ai](https://github.com/holeyfield33-art/pin-up-ai)
- Open an issue with the `privacy` label
