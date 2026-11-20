# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/almalikgroup-cmd/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/almalikgroup-cmd/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

One image that sums up the world news of **Thursday 19 November 2026**, drawn
entirely by a program. `main.py` (Python 3.13, standard library only) rasterises
a one-page newspaper front page by hand — a dated masthead, a lead story, four
story cards and an "also today" briefs strip — and writes it as a PNG. No
network, no input files, no randomness: every run writes exactly the same
bytes.

The front page carries the day's wire news: the first Trump–Xi–Putin three-way
summit at APEC in Shenzhen and its joint peace declaration; the ICJ ruling that
Myanmar committed genocide of the Rohingya; Anthropic's record $81bn IPO; the
Iran war threats and Israeli tanks in central Gaza; Ukraine's third strike on
the Crimean Bridge in a week; and, in the briefs, COP31, the Denmark–Greenland
defence pact, IMF world inflation, children in conflict zones and Fiji's
El Niño drought disaster.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024 x 1024 PNG, about 21 KiB)
```

Without `MAKEFUN_OUTPUT_DIR` the image is written to `/output/entry.png`,
which is where the make.fun grader reads it.

---

<sub>Entered on [make.fun](https://make.fun/?ref=fp1aw4h5&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
