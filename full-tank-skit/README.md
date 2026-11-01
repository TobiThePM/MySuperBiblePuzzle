# Full Tank Dey Burn Slow? (Baba Mechanic Explains, Ep. 2)

An animated comedy skit, about 67 seconds long. Dayo tops up ₦10,000 at a time, and Tobi fills his tank because he thinks a full tank "no dey dry off." Baba Mechanic, back from episode 1, explains what's really going on.

## Output
- `output/full-tank-dey-burn-slow_9x16.mp4`: vertical 1080×1920 for TikTok, Reels, Shorts and Status
- `output/full-tank-dey-burn-slow_16x9.mp4`: landscape 1920×1080 for YouTube, X and Facebook

## Cast
| Character | Who | Voice (ElevenLabs) |
|---|---|---|
| Dayo | Tops up ₦10k at a time | Timmy Adubi |
| Tobi | Fills his tank, for the wrong reason | Kingsley |
| Baba Mechanic | The voice of reason (same voice as Ep. 1) | Chris D Razor |

The full script is in `script.json`, and the voice takes are in `audio/`.

## Facts used
- **Tank level doesn't change fuel use.** Fuel burns in the engine at a rate set by driving and load, not by how full the tank is. The tank is sealed, so fuel doesn't "dry off" from the air gap. A full tank is about 30–40 kg heavier, which makes consumption marginally worse, but the difference is negligible.
- **₦10,000 is about 7.3 L** at roughly ₦1,369/L (NNPC Lagos, late Oct 2026). That's about 60–90 km in city traffic.
- **Fuel gauges aren't linear.** They often sit on "Full" for a long time, then fall quickly near the bottom.
- **Real benefits of filling up:** fewer trips and queues, and protection for the in-tank fuel pump. The pump is cooled by the fuel around it, so habitually running near empty can shorten its life.
- **Buy from trusted stations,** and check that the meter starts at ₦0.

## How to rebuild
1. Run `python3 build_audio.py`. It writes `timeline.json` and `mix.wav`.
2. Run `node render.js $PWD 1080 1920 out_9x16.mp4` and `node render.js $PWD 1920 1080 out_16x9.mp4`.

This uses the same engine as `../ac-fuel-skit`. Fonts: Bangers and Baloo 2 (SIL OFL).
