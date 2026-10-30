"""Lay out the skit timeline and mix the soundtrack.

Reads script.json + voice takes (audio/Lxx.mp3), trims silence, places each
line on the timeline, synthesises music/ambience/SFX with numpy and writes:
  timeline.json  - cue timings + lip-sync envelopes for the renderer
  mix.wav        - final stereo soundtrack
Missing voice takes get a silent placeholder so visuals can be previewed.
"""
import json, os, subprocess, sys, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = sys.argv[1] if len(sys.argv) > 1 else HERE
AUDIO = os.path.join(WORK, "audio")
SR = 44100
FPS = 30
TEMPO = float(os.environ.get("TEMPO", "1.08"))  # speed-up applied to dialogue

INTRO = 2.3   # bridge establishing shot before the first line
GAP = 0.18    # breath between lines
SCENE_GAP = 0.32  # extra pause when the scene changes
OUTRO = 2.4

script = json.load(open(os.path.join(HERE, "script.json")))
rng = np.random.default_rng(7)


def load_voice(lid):
    src = os.path.join(AUDIO, f"{lid}.mp3")
    if not os.path.exists(src):
        return None
    af = ("silenceremove=start_periods=1:start_threshold=-42dB,areverse,"
          "silenceremove=start_periods=1:start_threshold=-42dB,areverse")
    if TEMPO != 1.0:
        af += f",atempo={TEMPO}"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-af", af, "-ac", "1",
                          "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def envelope(x):
    hop = SR // FPS
    n = len(x) // hop + 1
    rms = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2) + 1e-9) for i in range(n)])
    ref = np.percentile(rms, 92) + 1e-6
    e = np.clip((rms / ref - 0.12) / 0.88, 0, 1)
    return [round(float(v), 3) for v in e]


def fake_env(dur):
    """Syllable-like mouth movement for lines whose voice take is still missing."""
    k = np.arange(int(dur * FPS) + 1) / FPS
    e = np.clip(0.55 + 0.45 * np.sin(2 * np.pi * 4.2 * k) * np.sin(2 * np.pi * 0.9 * k + 1), 0, 1)
    return [round(float(v), 3) for v in e]


# ---------- timeline ----------
cues, voices = [], []
t = INTRO
prev_scene = None
for ln in script["lines"]:
    if prev_scene and ln["scene"] != prev_scene:
        t += SCENE_GAP
    x = load_voice(ln["id"])
    placeholder = x is None
    if placeholder:
        x = np.zeros(int(SR * len(ln["text"]) / 13.5 / TEMPO), np.float32)
    dur = len(x) / SR
    cues.append(dict(ln, start=round(t, 3), dur=round(dur, 3), placeholder=placeholder,
                     env=fake_env(dur) if placeholder else envelope(x)))
    voices.append((t, x))
    t += dur + GAP
    prev_scene = ln["scene"]
total = t - GAP + OUTRO
N = int(total * SR)
tt = np.arange(N) / SR


def at(s):
    return int(s * SR)


def cue(i):
    return cues[i]


# ---------- helpers ----------
def smooth(x, w):
    w = max(1, int(w))
    c = np.cumsum(np.concatenate([[0], x]))
    y = (c[w:] - c[:-w]) / w
    return np.concatenate([y, np.full(len(x) - len(y), y[-1] if len(y) else 0)])


def band(x, lo_w, hi_w):
    """Crude band-pass: difference of two moving averages (window sizes in samples)."""
    return smooth(x, hi_w) - smooth(x, lo_w)


def add(buf, start, sig, gain=1.0, pan=0.0):
    i = at(start)
    if i >= N:
        return
    sig = sig[: N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[0, i:i + len(sig)] += sig * gain * l * 1.414
    buf[1, i:i + len(sig)] += sig * gain * r * 1.414


def adsr(n, a=0.005, d=0.1, sr=SR):
    k = np.arange(n) / sr
    return np.minimum(1, k / a) * np.exp(-k / d)


def tone(freq, dur, kind="sine"):
    k = np.arange(int(dur * SR)) / SR
    ph = 2 * np.pi * np.cumsum(np.broadcast_to(freq, k.shape)) / SR if np.ndim(freq) else 2 * np.pi * freq * k
    if kind == "sine":
        return np.sin(ph)
    if kind == "horn":  # brassy: several harmonics
        return sum(np.sin(ph * h) / h ** 0.8 for h in range(1, 8))
    raise ValueError(kind)


# ---------- music (light afrobeats groove, 102 bpm) ----------
music = np.zeros((2, N), np.float32)
bpm = 102
beat = 60 / bpm
step = beat / 4
kick = tone(np.linspace(140, 45, int(0.25 * SR)), 0.25) * adsr(int(0.25 * SR), 0.002, 0.09)
shk = band(rng.standard_normal(int(0.06 * SR)), 3, 1) * adsr(int(0.06 * SR), 0.003, 0.018)
rim = (band(rng.standard_normal(int(0.08 * SR)), 12, 2) * 0.6 + tone(820, 0.08) * 0.4) * adsr(int(0.08 * SR), 0.001, 0.02)
chords = [[220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7], [164.8, 207.7, 246.9]]  # Am F G E
bassline = [55.0, 43.65, 49.0, 41.2]
kick_steps = {0, 6, 8, 11}
rim_steps = {4, 12, 14}
shk_gain = [1, .4, .7, .4] * 4
music_end = cues[-1]["start"] + cues[-1]["dur"] + OUTRO
s = 0
while s * step < music_end:
    st = s * step
    bar = int(s // 16)
    k16 = s % 16
    ch = chords[bar % 4]
    if k16 in kick_steps:
        add(music, st, kick, 0.55)
    if k16 in rim_steps:
        add(music, st, rim, 0.25, pan=0.3)
    add(music, st, shk, 0.10 * shk_gain[k16], pan=-0.35)
    if k16 in (0, 3, 7, 10, 14):  # log-drum style bass
        b = bassline[bar % 4] * (2 if k16 == 14 else 1)
        f = np.linspace(b * 1.5, b, int(0.32 * SR)) if k16 in (0, 10) else b
        add(music, st, tone(f, 0.32) * adsr(int(0.32 * SR), 0.003, 0.14), 0.45)
    if k16 in (2, 6, 10):  # marimba-ish chord stabs on the off-beats
        for j, fr in enumerate(ch):
            sig = (tone(fr * 2, 0.22) + 0.3 * tone(fr * 8, 0.22)) * adsr(int(0.22 * SR), 0.002, 0.05)
            add(music, st, sig, 0.06, pan=(j - 1) * 0.4)
    s += 1
# music: full in intro, ducked under dialogue, swells at end card
mgain = np.full(N, 0.30, np.float32)
mgain[: at(INTRO)] = 0.75
for c in cues:
    a, b = at(c["start"] - 0.1), at(c["start"] + c["dur"] + 0.1)
    mgain[a:b] = 0.16
end_start = cues[-1]["start"]
mgain[at(end_start):] = np.maximum(mgain[at(end_start):], 0.30)
mgain[at(end_start + cues[-1]["dur"]):] = 0.7
mgain = smooth(mgain, int(0.15 * SR)).astype(np.float32)
fade = np.clip((total - tt) / 1.2, 0, 1)
music *= mgain * fade

# ---------- ambience: Lagos traffic ----------
amb = np.zeros((2, N), np.float32)

noise = rng.standard_normal((2, N)).astype(np.float32)
rumble = np.stack([band(noise[0], 300, 30), band(noise[1], 300, 30)]) * 1.4
engine = (0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * tt)) * np.sin(2 * np.pi * 38 * tt) * 0.25
amb += rumble + engine
# horns sprinkled through, more in the bridge intro
horn_times = [0.3, 0.9, 1.7, 2.4] + list(np.sort(rng.uniform(4, total - 4, 16)))
for ht in horn_times:
    f = rng.choice([370, 415, 466, 523])
    d = rng.uniform(0.18, 0.45)
    sig = tone(f, d, "horn") * np.minimum(1, np.minimum(np.arange(int(d * SR)), int(d * SR) - np.arange(int(d * SR))) / 400)
    add(amb, ht, sig, 0.05 if ht > INTRO else 0.09, pan=rng.uniform(-0.9, 0.9))
# scene-dependent ambience level: outdoor/open-window loud, AC on = muffled
alev = np.full(N, 0.9, np.float32)
for c in cues:
    a, b = at(c["start"] - SCENE_GAP), at(c["start"] + c["dur"] + GAP)
    lvl = {"engine": 0.15, "facts": 0.15, "baba": 0.4, "window": 1.0, "acOn": 0.25, "end": 0.0}.get(c["scene"], 0.8)
    alev[a:b] = lvl
alev[at(cues[-1]["start"] - SCENE_GAP):] = 0.0
alev = smooth(alev, int(0.3 * SR)).astype(np.float32)
amb *= alev * 0.30

# ---------- SFX ----------
sfx = np.zeros((2, N), np.float32)


def whoosh(d=0.45, up=True):
    n = int(d * SR)
    k = np.linspace(0, 1, n)
    env = np.sin(np.pi * k) ** 2
    return band(rng.standard_normal(n), 40, 4) * env * 1.5


def pop():
    return tone(np.linspace(300, 1100, int(0.12 * SR)), 0.12) * adsr(int(0.12 * SR), 0.002, 0.05)


def ding(f=1320):
    n = int(0.9 * SR)
    return (tone(f, 0.9) + 0.4 * tone(f * 2.76, 0.9)) * adsr(n, 0.002, 0.25)


def thump():
    n = int(0.35 * SR)
    return (tone(np.linspace(110, 50, n), 0.35) + band(rng.standard_normal(n), 60, 2) * 0.5) * adsr(n, 0.002, 0.08)


by_id = {c["id"]: c for c in cues}
add(sfx, by_id["L01"]["start"] - 0.55, thump(), 0.7)                      # car door
prev = None
for c in cues:                                                              # scene whooshes
    if prev and c["scene"] != prev:
        add(sfx, c["start"] - SCENE_GAP * 0.8, whoosh(), 0.35)
    prev = c["scene"]
add(sfx, by_id["L05"]["start"] - 0.25, pop(), 0.5)                         # Baba pops in
L06, L07 = by_id["L06"], by_id["L07"]
for fr in (0.36, 0.62):
    add(sfx, L06["start"] + L06["dur"] * fr, ding(990), 0.25)
for fr in (0.25, 0.52, 0.82):                                               # fact-card stamps
    add(sfx, L07["start"] + L07["dur"] * fr, thump(), 0.45)
    add(sfx, L07["start"] + L07["dur"] * fr, ding(1480), 0.12)
L11, L12 = by_id["L11"], by_id["L12"]
add(sfx, L11["start"] + L11["dur"] * 0.55, ding(1320), 0.3)                # phone ping
add(sfx, L11["start"] + L11["dur"] * 0.55 + 0.12, ding(1760), 0.3)
add(sfx, L12["start"] + L12["dur"] * 0.32, band(rng.standard_normal(1200), 4, 1) * adsr(1200, 0.0005, 0.004), 0.8)  # AC click
n = int(3.2 * SR)                                                           # cold air rush
add(sfx, L12["start"] + L12["dur"] * 0.33, band(rng.standard_normal(n), 25, 3) * np.minimum(1, np.arange(n) / (0.4 * SR)) * np.exp(-np.arange(n) / (2.0 * SR)), 0.5)
L13 = by_id["L13"]
for j, fr in enumerate([523.3, 659.3, 784.0, 1046.5]):                      # end sting
    add(sfx, L13["start"] + L13["dur"] + 0.1 + j * 0.09, ding(fr), 0.18)

# ---------- dialogue ----------
dia = np.zeros((2, N), np.float32)
for start, x in voices:
    add(dia, start, x, 1.0)

mix = dia * 1.0 + music * 0.55 + amb + sfx * 0.8
peak = np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix / peak * 1.3) * 0.93
pcm = (mix.T * 32767).astype(np.int16)
with wave.open(os.path.join(WORK, "mix.wav"), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())

json.dump({"total": round(total, 3), "fps": FPS, "intro": INTRO, "cast": script["cast"], "cues": cues},
          open(os.path.join(WORK, "timeline.json"), "w"))
missing = [c["id"] for c in cues if c["placeholder"]]
print(f"total {total:.2f}s  lines {len(cues)}  missing {missing}")
for c in cues:
    print(f'{c["id"]} {c["start"]:6.2f} +{c["dur"]:.2f} {c["scene"]}')
