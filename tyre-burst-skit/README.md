# Tyre Don Burst! (Lagos Road Safety, Ep. 3)

An animated road-safety comedy skit, about 1:32 long. Femi is enjoying a clear Oshodi expressway when his tyre bursts at 60 km/h. Officer Ngozi, an FRSC-inspired cartoon officer, appears and walks him through what to do.

## Output
- `output/tyre-don-burst_9x16.mp4`: vertical 1080×1920 for TikTok, Reels, Shorts and Status
- `output/tyre-don-burst_16x9.mp4`: landscape 1920×1080 for YouTube, X and Facebook

## Cast
| Character | Voice (ElevenLabs) |
|---|---|
| Femi, the driver | Will |
| Officer Ngozi | Amanda |

The officer's uniform is *inspired* by FRSC (ash shirt, navy beret, reflective vest) but uses no real logo or insignia. The end card says "Not an official FRSC message."

## Safety advice in the video
1. Hold the steering with both hands and keep the car straight. Don't slam the brake.
2. Ease off the accelerator gradually and let the car slow down by itself.
3. Turn on your hazard lights.
4. Once you've slowed down, move gently to the side and park far from the road.

Also covered:
- Use your spare tyre or call a vulcanizer, and stand away from the road.
- At night, use full headlights only when the road is empty, and dip them for oncoming cars.
- If the tyre bursts somewhere dark and isolated, don't stop there. Drive slowly to a well-lit place such as a filling station.
- Carry a spare tyre, jack, C-caution and fire extinguisher, and check your tyre pressure regularly. FRSC's list of required items also includes a first aid kit and wheel spanner.

## How to rebuild
1. Run `python3 build_audio.py`. It writes `timeline.json` and `mix.wav`.
2. Run `node render.js $PWD 1080 1920 out_9x16.mp4` and `node render.js $PWD 1920 1080 out_16x9.mp4`.

The voice takes are in `audio/`, and `audio/sessions.json` maps each line to its ElevenLabs session. This uses the same engine as `../ac-fuel-skit` and `../full-tank-skit`.
