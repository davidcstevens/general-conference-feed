# General Conference Podcast Feed

Creates an updatable RSS podcast feed for audio from [General Conference](https://www.churchofjesuschrist.org/study/general-conference?lang=eng) of The Church of Jesus Christ of Latter-day Saints.

## Quick start

1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

2. Set your hosted feed URL (optional for local generation)
   ```bash
   export FEED_SELF_LINK="https://yourusername.github.io/conference-feed/feed.xml"
   export ITUNES_IMAGE="https://yourusername.github.io/conference-feed/cover.jpg"  # optional
   ```

3. Generate feed
   ```bash
   python generate.py
   ```

4. Test `feed.xml` in a podcast app or validator (Podba.se, W3C Feed Validator)

## Hosting

- Commit this repo to GitHub.
- Enable GitHub Pages (Settings → Pages) deploying from `main` (root).
- Update `FEED_SELF_LINK` in `.github/workflows/update-feed.yml` to your Pages URL.
- The workflow runs every 6 months (April 1 and October 1) and can be triggered manually.
- Add a podcast cover image as `cover.jpg` and set `ITUNES_IMAGE`.

## Notes

- Feed uses MP3 URLs as GUIDs so episodes remain stable across regenerations.
- If the Church site changes structure, the selectors include fallbacks for `.mp3` links.
- Each MP3 found on a session page becomes an episode; multiple parts are numbered.
