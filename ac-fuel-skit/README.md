# AC Dey Drink Fuel? (Lagos ride-hailing skit)

An animated comedy skit (about 72 seconds). It debunks the idea that "AC dey drink fuel": the AC does use some fuel, but only a small amount. It is not an excuse to leave ride-hailing passengers sweating.

## Output
- `output/ac-dey-drink-fuel_9x16.mp4`: vertical 1080×1920 for TikTok, Reels, Shorts and Status
- `output/ac-dey-drink-fuel_16x9.mp4`: landscape 1920×1080 for YouTube, X and Facebook

All 12 lines are voiced with ElevenLabs. The takes are in `audio/`.

## Cast
| Character | Who | Voice (ElevenLabs) |
|---|---|---|
| Ada | Passenger, melting in the back seat | Rho |
| Kunle | Ride-hailing driver, protecting his fuel | Terna Gabriel |
| Baba Mechanic | The voice of reason | Chris D Razor |

The full script is in `script.json`.

## Facts used (estimates)
- The AC compressor runs off the engine's accessory belt. With the AC off, its clutch disengages and the pulley spins freely. With the AC on, the compressor adds a small load on the engine.
- In typical driving the AC adds about 5–10% fuel use. When idling in traffic it adds about 0.3–0.5 L/hour.
- Petrol was about ₦1,369/L at NNPC Lagos in late Oct 2026, so the AC costs roughly ₦400–₦700 per hour of go-slow.
- At expressway speeds, driving with the windows down adds drag, which also costs fuel.

## How to rebuild
1. Put voice takes in `audio/Lxx.mp3`, named by the line ids in `script.json`.
2. Run `python3 build_audio.py`. It trims silence, lays out the timeline, synthesizes the music, ambience and SFX, and writes `timeline.json` and `mix.wav`.
3. Run `node render.js $PWD 1080 1920 out_9x16.mp4` and `node render.js $PWD 1920 1080 out_16x9.mp4`.

Visuals are drawn in code (`scene.html`, canvas). Mouths are lip-synced to each voice track's loudness. Requires ffmpeg, numpy and Playwright with Chromium.

Fonts: Bangers and Baloo 2 (SIL Open Font License, see `fonts/`).
