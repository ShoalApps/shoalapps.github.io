# shoalapps.github.io

The website for [Shoal](https://github.com/ShoalApps): open-source Android apps that take on your
wallpaper's colours with Material You.

A single static page. Colours are generated with Google's
[material-color-utilities](https://github.com/material-foundation/material-color-utilities), and the
credits are fetched live from GitHub. Pushing to `main` publishes it with GitHub Pages.

Free software under the GPL-3.0.

## Support

Shoal is free, open source and has no ads. If you'd like to help it keep going, you can [support Shoal on Liberapay](https://liberapay.com/ShoalApps).

## Trailer and motion

`assets/shoal-trailer.mp4` is a 104-second film with synthetic British English narration, original water and transition sounds, on-screen text, British English captions and an HTML transcript. It introduces all six apps and illustrates one person's journey from a standard video app through a Morphe-patched app to a separate Shoal app. Morphe is an independent project, not a partner.

Audio attribution and licensing are in `media/AUDIO-CREDITS.md`. To regenerate the narration, use `scripts/synthesise-narration.py` with the documented Piper voice model. Regenerate the finished film with `python3 scripts/build-trailer.py` on a machine with FFmpeg (libx264 and librsvg) and DejaVu fonts. The script uses the existing app screenshots and SVG icons, and writes the MP4, poster, captions and transcript together. Keep claims in step with the shipped apps.

Fish motion is in `assets/ocean.css` and `assets/ocean.js`. It honours reduced motion, includes a persistent pause control, and pauses decorative motion and video when the page is hidden. The trailer uses `preload="none"` and never autoplays.
