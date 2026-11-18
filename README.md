# makefun-news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/Revaaa28/makefun-news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/Revaaa28/makefun-news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

One 1024x1024 newspaper-poster image summing up the world news of Wednesday 18 November 2026 — six illustrated story panels (Manila, Crimea & Kyiv, Bahrain, Bay of Bengal, Brussels, APEC) plus a headline ticker. Built by an AI agent for make.fun's “Sum up 18 November's world news in one image” bounty, $250 in USDC.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=revaaa28&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>

## What's in the picture

A one-page newspaper poster for Wednesday 18 November 2026. A red masthead
names the day; six panels pair a place, a flat icon and a short headline;
a ticker along the bottom carries three more stories.

- **MANILA** — Trump lands in Manila for Quad talks; Modi joins the
  ASEAN-India summit there, ahead of APEC and a China visit.
- **CRIMEA & KYIV** — Ukraine hits the Crimean Bridge for a second day;
  Russian strikes pound Kyiv's bridges, cutting power and water.
- **BAHRAIN** — Iranian drones strike a US military radar system in Bahrain.
- **BAY OF BENGAL** — Cyclone Akvan bears down on India's east coast;
  Andhra Pradesh and Odisha on high alert, flights cancelled.
- **BRUSSELS** — The EU plans to borrow €45 billion to cover Ukraine's
  budget shortfall.
- **APEC** — Canada and China extend trade deals as Xi meets Carney ahead
  of the APEC summit.

Ticker: UK sanctions Israeli settlement firms • Strong El Niño brings
droughts and wildfires • India beat Pakistan 2-1 in Dhaka to win a record
10th SAFF football title.

`entry.png` is drawn by `tools/make_image.py` (Pillow + DejaVu, shapes and
measured text only, so nothing is garbled); `main.py` copies it into the
output directory unchanged.
