# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/tidy-marten-51/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/tidy-marten-51/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A newspaper front page summing up the world news of **Friday, 20 November 2026** — one image, 1024×1024.

## The stories on the page

- **Lead — Cyclone Akvan.** A severe cyclonic storm making landfall on India's east coast (Odisha, between Puri and Gopalpur) on Friday afternoon. More than 120,000 people evacuated, 300+ rescue teams deployed, about 60 trains cancelled.
- **Shenzhen summit.** US President Trump, Chinese President Xi and Russian President Putin held a rare three-way summit in China and issued a "Declaration Towards Peace", calling for UN reform and talks to reduce nuclear risks. No breakthrough on Ukraine; Putin vowed to hit back hard after Ukraine struck the Crimea Bridge a third time in a week.
- **GTA VI.** Launched 19 November to near-perfect reviews (99 on Metacritic). Research firm Sensor Tower put launch-day sales near 19 million copies and $1.84 billion by Thursday afternoon; about 6 million people watched livestreams, and one in five salaried US workers had planned time off for launch day.
- **The Hague.** The International Court of Justice ruled Myanmar committed genocide against the Rohingya in its 2017 crackdown.
- **Also today:** Anthropic's record ~$2 trillion Nasdaq debut, shares ebbing as Wall Street fell; Meta re-evaluating its 2030 net-zero target amid its AI buildout; the US auctioned its first-ever deep-sea mining leases; Somalia expelled the UAE ambassador; South Korea's top court overturned former PM Han Duck-soo's conviction; Fiji declared a national disaster over El Niño drought; NASA's Voyager 1 reached one light-day from Earth.

## How the picture is made

`draw_frontpage.py` (build-time tool, needs Pillow) lays out the front page: a navy nameplate carrying the date, the lead cyclone story with its photograph, the Shenzhen summit and the GTA VI launch side by side, the Hague ruling, a strip of the day's other stories, and the date again in the footer. The three photographs in `assets/` were generated for this entry: the summit, the cyclone landfall, and a neon Vice City street.

Rebuild the picture:

```sh
python3 draw_frontpage.py   # writes entry.png (1024x1024, under 1 MiB)
```

The script is deterministic — fixed layout, no randomness, no network — so re-running it writes byte-identical output.

## How to run the entry

`main.py` is the submitted entrypoint (Python 3.13, standard library only). It validates `entry.png` — a whole PNG with good chunk CRCs, at most 1 MiB and at most 1024×1024 — and copies it byte for byte to the output directory:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Without `MAKEFUN_OUTPUT_DIR` it writes to `/output/entry.png`, as the grader does. Running it twice produces identical bytes.
