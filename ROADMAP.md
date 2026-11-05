# Shoal roadmap

Squill is Shoal’s flagship. This roadmap groups the work across the apps by priority. Items are planned unless marked as shipped or in development.

## Shipped

- **Squill** — Markdown notes and folders, a link graph with drag-to-link, a welcome tour with Squilly, encrypted notes, desktop sync, painting layer groups, rulers and perspective guides, and custom brushes and palettes.
- **Shoal** — First-run setup for background updates and per-app controls to keep an installed version.
- **Angelfish** — Local playlists, adaptive video buffering, and optional offline downloads based on subscriptions.
- **Butterflyfish** — Offline drafts, including replies, an upstream compatibility screen, mu-style code formatting, explanations for unavailable quotes, larger photo galleries, pinned posts on profiles, and text limits that count emoji correctly.

## Next

| Project | Work | Status |
| --- | --- | --- |
| [Squill](https://github.com/ShoalApps/squill) | Test stylus pressure, palm rejection and graph linking on real hardware. Cover zoomed graphs and nearby drop targets. | Planned |
| [Squill](https://github.com/ShoalApps/squill) | Test device sync, encrypted note recovery and reminder delivery across real devices and reboots. | Planned |
| [Shoal](https://github.com/ShoalApps/shoal) | Add an update history showing installs, updates and failures. | In development |
| [Shoal](https://github.com/ShoalApps/shoal) | Offer stable, beta and nightly release channels, each with its own Material 3 icon. | Planned |
| [Shared library](https://github.com/ShoalApps/shoal-common) | Adopt shared language handling and release notes across the apps. | In development |
| [Shared library](https://github.com/ShoalApps/shoal-common) | Move settings components, shapes, error reporting and update helpers into the library, so one update reaches every app. | Planned |
| [Angelfish](https://github.com/ShoalApps/angelfish) | Verify playback, queue transitions and offline audio on real devices across network conditions. | Planned |
| [Butterflyfish](https://github.com/ShoalApps/butterflyfish) | Polish existing Bluesky features before adding new ones: consistent likes, reposts and follows, reply restrictions, staying signed in through network failures, marking notifications as read, safer profile editing, and clear loading errors. | In development |
| [Butterflyfish](https://github.com/ShoalApps/butterflyfish) | Verify reply drafts and moderation against live Bluesky accounts. | Planned |
| [Butterflyfish](https://github.com/ShoalApps/butterflyfish) | Support multiple Bluesky and multiple X accounts. | Planned |
| [Butterflyfish](https://github.com/ShoalApps/butterflyfish) | Make X faster and as native as Bluesky, and keep following upstream changes to both services. | Planned |

## Later

- **Squill painting** — Work towards Krita’s full feature set: filter masks and other non-destructive tools, vector layers, an animation timeline, CMYK and high bit depth, and plugins.
- **Squill documents** — Improve document and slide round trips using real files. Explore optional Google Drive and Slides integration while keeping local editing available.
- **Squill imports** — Check real Google Keep, Evernote and Notion exports, including attachments and links.
- **Butterflyfish networks** — Add the Fediverse and other Twitter-like networks.
- **Butterflyfish features** — After the polish, add the Bluesky features still missing, such as bookmarks, deleting your own posts, quote posts and threads.

Clownfish, Pufferfish and Anglerfish are on hold. The [Shoal website](https://shoalapps.github.io/) lists them in its archive section. If they return, Clownfish would bring Shorts, Reels and TikTok into one feed with reliable sign-in, and Pufferfish would become a full music app with recommendations on its home page and colours from your wallpaper.

For bugs or feature requests, use the relevant app’s GitHub issue tracker.
