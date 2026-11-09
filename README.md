# Dialed site

Public site for Dialed, served by GitHub Pages at https://dialed.frusoft.dev (custom domain in `CNAME`).

| Path | What |
|---|---|
| `/` , `/es/` | Landing page (English, Spanish). Shared `site.css` / `site.js`, screenshots in `img/`. |
| `/get/?src=<source>` | One link for bios and ads: sends phones to the right store with campaign attribution. |
| `/ig/`, `/tt/`, `/yt/` | Short links that forward to `/get/?src=ig|tiktok|yt`. |
| `/get/m/#…` | Opens shared machine/grinder/setup QR codes in the app. |
| `/privacy/`, `/support/` | Store-required pages (use the older `style.css`). |
| `/guides/`, `/es/guides/` | SEO guides. Edit markdown in `tools/guides-src/{en,es}/`, then `python3 tools/build-guides.py` (writes the HTML and regenerates `sitemap.xml`). Needs Nico's review before merge. |
| `_og/` | Sources of the social share images (`og.jpg`, `og-es.jpg`). |

Screenshots in `img/` are the App Store ones (`ios/fastlane/screenshots/en-US`) resized to 660 px WebP.
The Spanish page is generated: edit `index.html`, add the Spanish strings to `tools/translate-es.py`, then run
`python3 tools/translate-es.py index.html > es/index.html` (it fails on any English string it can't translate).

To regenerate a share image: serve the folder (`python3 -m http.server`) and screenshot `_og/og.html` at 1200×630
with headless Chrome, then save as JPEG.
