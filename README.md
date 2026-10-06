# CEE Tender Intelligence Free v0.4.0

Free Render release with Prozorro and TED, UA/PL/EN UI, dynamic country selector, current tenders by default, readable localized tender cards, completed-tender winner analytics, supplier profiles, market share, trend-ready monthly aggregation, and Excel export.

## Deploy
Push the project to GitHub, create a Render Blueprint, provide ADMIN_EMAIL and ADMIN_PASSWORD, and apply. The service uses in-memory storage, no database, disk, or cron job.

## Notes
- Current-only filter is enabled by default and can be disabled in the dashboard.
- Country values are rebuilt from imported data after each refresh.
- TED multilingual values are selected by connector fallbacks; statuses and interface labels are localized. Original source text stays available in the tender card.
- Winner analysis requires winner/award fields returned by the source API.
