# Music Recommender Simulation

## Project Summary

This project is a content-based music recommender simulation built in Python. It reads a catalog of songs from a CSV file, compares each song against a user's taste profile, and returns a ranked list of the top matches with plain-language explanations. The system is intentionally simple — no machine learning, no user history — so that every decision the algorithm makes is transparent and easy to reason about.

Real-world recommenders (Spotify, YouTube Music) rely on collaborative filtering (what listeners like you also played), neural embeddings of audio signals, and billions of data points. My version distills the same *idea* down to a handful of hand-crafted rules: award points for matching genre and mood, then add a proximity score for how close the song's energy is to what the user wants. The design prioritizes explainability over accuracy.

---

## How The System Works

### Features used per Song

Each `Song` object carries ten attributes loaded from `data/songs.csv`:

| Attribute | Type | Description |
|---|---|---|
| `id` | int | Unique catalog ID |
| `title` | str | Song title |
| `artist` | str | Artist name |
| `genre` | str | Musical genre (pop, lofi, rock, edm, …) |
| `mood` | str | Emotional vibe (happy, chill, intense, …) |
| `energy` | float 0–1 | Perceived energy / intensity |
| `tempo_bpm` | int | Beats per minute |
| `valence` | float 0–1 | Musical positivity (high = cheerful) |
| `danceability` | float 0–1 | How suitable for dancing |
| `acousticness` | float 0–1 | How acoustic (vs electronic) the track is |

### UserProfile / user_prefs

A user preference dictionary (or `UserProfile` dataclass) stores:
- `genre` — favorite genre string
- `mood` — target mood string
- `energy` — target energy level (0.0–1.0)
- Optional: `valence`, `danceability` for finer-grained matching
- `likes_acoustic` (bool, used in OOP path) — bumps acoustic songs slightly

### Algorithm Recipe (Scoring Rule)

The `score_song` function judges one song at a time using these weighted rules:

```
+2.0   Genre match          (strongest signal — genre is the user's core identity)
+1.0   Mood match           (strong contextual signal)
+0–1.0 Energy proximity     = max(0, 1.0 − |song.energy − target_energy| × 2)
+0–0.5 Valence proximity    = max(0, 0.5 − |song.valence − target_valence|)  [optional]
+0–0.5 Danceability prox.   = max(0, 0.5 − |song.danceability − target|)     [optional]
```

Genre is worth the most because it is the user's strongest stated preference. Mood is next. The numerical features use a *distance penalty* rather than a raw value — a song that matches your target energy exactly scores the full point; one that is 0.5 away scores nothing. This prevents the system from always picking the loudest or most danceable song regardless of fit.

### Ranking Rule

`recommend_songs` calls `score_song` for every song in the catalog, collects `(song, score, explanation)` tuples, and uses Python's built-in `sorted()` (returning a new list, leaving the original unchanged) to rank them highest-to-lowest. The top `k` results are returned.

### Data Flow

```
Input: user_prefs dict
       ↓
Load: data/songs.csv → list of song dicts
       ↓
Loop: for every song → score_song(user_prefs, song) → (score, reasons)
       ↓
Sort: sorted(scored, key=score, reverse=True)
       ↓
Output: top-k (song, score, explanation) tuples
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python -m src.main
   ```

### Running Tests

```bash
pytest
```

---

## Terminal Output Screenshots

### Profile 1 — High-Energy Pop

```
Profile: High-Energy Pop
Preferences: {'genre': 'pop', 'mood': 'happy', 'energy': 0.85, 'valence': 0.8, 'danceability': 0.8}
============================================================
  #1  Sunrise City by Neon Echo
       Genre: pop | Mood: happy | Energy: 0.82
       Score: 4.89
       Why:   genre match (+2.0), mood match (+1.0), energy proximity (+0.94), valence proximity (+0.46), danceability proximity (+0.49)

  #2  Gym Hero by Max Pulse
       Genre: pop | Mood: intense | Energy: 0.93
       Score: 3.73
       Why:   genre match (+2.0), energy proximity (+0.84), valence proximity (+0.47), danceability proximity (+0.42)

  #3  Rooftop Lights by Indigo Parade
       Genre: indie pop | Mood: happy | Energy: 0.76
       Score: 2.79
       Why:   mood match (+1.0), energy proximity (+0.82), valence proximity (+0.49), danceability proximity (+0.48)
```

**Observation:** Sunrise City wins decisively because it matches genre, mood, and is very close in energy. Gym Hero comes in second — same genre, but the mood is "intense" not "happy", so it loses 1.0 point. Rooftop Lights lands third despite being "indie pop" (not pop) because the mood and numerical features align well. This feels correct.

### Profile 2 — Chill Lofi

```
Profile: Chill Lofi
Preferences: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.38, ...}
============================================================
  #1  Library Rain by Paper Lanterns    Score: 4.90
  #2  Midnight Coding by LoRoom         Score: 4.88
  #3  Focus Flow by LoRoom              Score: 3.95
  #4  Spacewalk Thoughts by Orbit Bloom Score: 2.54
  #5  Coffee Shop Stories by Slow Stereo Score: 1.79
```

**Observation:** The top two are separated by only 0.02 — they are both lofi/chill with nearly identical energy. Focus Flow scores lower because its mood is "focused", not "chill". Spacewalk Thoughts earns #4 via mood match even though it is ambient, not lofi.

### Profile 3 — Deep Intense Rock

```
Profile: Deep Intense Rock
Preferences: {'genre': 'rock', 'mood': 'intense', 'energy': 0.9, ...}
============================================================
  #1  Storm Runner by Voltline    Score: 4.94
  #2  Gym Hero by Max Pulse       Score: 2.39
  #3  Iron Throne by Wraith Engine Score: 1.65
```

**Observation:** Storm Runner is a near-perfect match (rock, intense, energy 0.91). The gap between #1 (4.94) and #2 (2.39) is large — no other song gets the genre+mood double bonus. This shows that with a small catalog, a specific genre can easily dominate.

### Profile 4 — Adversarial (blues/sad/high-energy)

```
Profile: Adversarial (blues/sad/high-energy)
Preferences: {'genre': 'blues', 'mood': 'sad', 'energy': 0.9, 'valence': 0.35}
============================================================
  #1  Delta Midnight by Blue Porch    Score: 3.46
       Why: genre match (+2.0), mood match (+1.0), energy proximity (+0.00), valence proximity (+0.46)
  #2  Storm Runner by Voltline        Score: 1.35
```

**Observation:** This is the most interesting result. Delta Midnight wins because it is the only blues/sad song — but it scores zero on energy because its actual energy (0.33) is nowhere near the requested 0.90. The algorithm chose the genre/mood match over the energy match, which highlights the over-weighting of categorical features. A blues/sad/high-energy combination simply does not exist in this small catalog.

---

## Experiments You Tried

### Experiment 1 — Weight Shift: Energy doubled, Genre halved

Original: genre +2.0, energy up to +1.0  
Modified: genre +1.0, energy up to +2.0

Result for the Pop/Happy profile: Gym Hero moved above Sunrise City because its energy (0.93) is closer to the target (0.85) than Sunrise City's (0.82). This shows the system is sensitive to weights and that a single parameter change can flip #1 and #2.

### Experiment 2 — Remove mood matching

Temporarily removing the mood check from `score_song` caused Gym Hero (pop/intense) to tie with Sunrise City (pop/happy) for the pop profile. Without mood differentiation, the system cannot tell "happy pop" from "workout pop" — both just become "pop."

### Experiment 3 — Adversarial profile

Requesting blues/sad/high-energy exposed a gap: the catalog has no loud blues tracks. The algorithm correctly surfaces the only blues/sad song but its energy score is 0.0 — it cannot satisfy all three preferences simultaneously. In a real system this would be an opportunity to widen the search or tell the user "no great match found."

---

## Limitations and Risks

- **Tiny catalog (20 songs):** With only 20 tracks, a single genre match can dominate. Many profiles will return the same small set of songs repeatedly.
- **No collaborative filtering:** The system ignores what other users with similar tastes have liked, which is the core strength of real recommenders.
- **Categorical features are binary:** Genre and mood are either a full match or zero — there is no notion of "rock is closer to metal than to jazz."
- **Static user profile:** The system has no way to learn from feedback or update preferences over time.
- **Dataset bias:** The original 10 songs skewed heavily toward pop and lofi. The 10 added songs improve diversity but the catalog still does not represent global music traditions.

---

## Reflection

See [model_card.md](model_card.md) and [reflection.md](reflection.md) for the full model card and personal reflection.

**Key takeaway:** Building even a toy recommender makes the trade-offs in real systems very tangible. Choosing what to weight more — genre vs. energy vs. mood — is essentially encoding a theory of what music taste *is*. That's a value judgment, not a math problem. Real systems hide this judgment inside learned parameters, making the bias harder to see but no less real.
