# Shoal roadmap

Squill is Shoal’s flagship. This roadmap groups the work across the apps by priority. Items are planned unless marked as shipped or in development.

## Shipped

- **Squill** — Markdown notes and folders, a link graph with drag-to-link, a welcome tour with Squilly, encrypted notes, desktop sync, painting layer groups, rulers and perspective guides, and custom brushes and palettes.
- **Shoal** — First-run setup for background updates and per-app controls to keep an installed version, in-app release notes with expandable history, an update history of installs, updates and failures, and Stable, Beta and Nightly release channels.
- **Shared library** — The support card, app language, What's New, error reports, Expressive shapes and settings tiles are shared by Shoal, Angelfish and Butterflyfish, along with the self-updater in Angelfish and Butterflyfish, so one library update reaches each of them.
- **Angelfish** — Local playlists, adaptive video buffering, and optional offline downloads based on subscriptions.
- **Butterflyfish** — Offline drafts, including replies, an upstream compatibility screen, mu-style code formatting, explanations for unavailable quotes, larger photo galleries, pinned posts on profiles, text limits that count emoji correctly, private local follows, an NSFW-only filter, optional break reminders, and polished likes, reposts and follows, staying signed in through network failures, safer profile editing, clearer loading errors, and switching between several Bluesky and X accounts.

## Next

| Project | Work | Status |
| --- | --- | --- |
| [Squill](https://github.com/ShoalApps/squill) | Test stylus pressure, palm rejection and graph linking on real hardware. Cover zoomed graphs and nearby drop targets. | Planned |
| [Squill](https://github.com/ShoalApps/squill) | Test device sync, encrypted note recovery and reminder delivery across real devices and reboots. | Planned |
| [Angelfish](https://github.com/ShoalApps/angelfish) | Verify playback, queue transitions and offline audio on real devices across network conditions. | Planned |
| [Butterflyfish](https://github.com/ShoalApps/butterflyfish) | Verify reply drafts and moderation against live Bluesky accounts. | Planned |
| [Butterflyfish](https://github.com/ShoalApps/butterflyfish) | Make X faster and as native as Bluesky, and keep following upstream changes to both services. | In development |

## Butterflyfish parity

Follow the [feature parity tracker](https://github.com/ShoalApps/butterflyfish/blob/main/compat/FEATURES.md) for Bluesky and X coverage.

- **Search** — Independent Posts and People loading, Top and Latest sorting, automatic paging, and retry. NSFW-only paging scans through pages without matches. People search also loads more automatically and keeps its scroll position when switching tabs.
- **Notifications** — Filter the inbox by activity type and mark notifications as read from All.
- **Post management** — Delete your own Bluesky posts from the post menu. Replies respect Bluesky’s restrictions, including when reopening drafts.
- **Next Bluesky features** — private bookmarks, notification grouping, and quote composition. Then tackle chat, starter packs, and feed and list management.
- **X** — Profiles, posts and searches open without reloading X's website, and likes, reposts and follows are pressed in place when the post or profile is already showing. Verify access and account requirements for each native feature before implementing it. Track bookmarks, lists, media, notifications, and messaging individually.
- **Quality** — Test account isolation, cancellation, slow-network recovery, and pagination. Measure startup, first feed item, and scrolling on a real device. Review opt-in Sentry reports by app and release.

## Later

- **Squill painting** — Work towards Krita’s full feature set: filter masks and other non-destructive tools, vector layers, an animation timeline, CMYK and high bit depth, and plugins.
- **Squill documents** — Improve document and slide round trips using real files. Explore optional Google Drive and Slides integration while keeping local editing available.
- **Squill imports** — Check real Google Keep, Evernote and Notion exports, including attachments and links.
- **Butterflyfish networks** — Add the Fediverse and other Twitter-like networks.

Clownfish, Pufferfish and Anglerfish are on hold. The [Shoal website](https://shoalapps.github.io/) lists them in its archive section. If they return, Clownfish would bring Shorts, Reels and TikTok into one feed with reliable sign-in, and Pufferfish would become a full music app with recommendations on its home page and colours from your wallpaper.

For bugs or feature requests, use the relevant app’s GitHub issue tracker.
