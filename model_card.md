# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder 1.0 suggests up to five songs from a 20-song catalog based on a user's stated genre preference, target mood, and desired energy level. It is designed for a classroom simulation — not for real music products or commercial use.

It assumes the user knows what they want and can express it as a simple preference dictionary. It is **not** intended for:
- Cold-start discovery (when a user has no stated preferences)
- Personalization based on listening history
- Production use in any streaming or media platform

---

## 3. How the Model Works

Imagine handing a librarian a short note that says "I want something pop, happy, and energetic." The librarian walks through every shelf (every song in the catalog) and gives each book a score based on how well it matches your note.

VibeFinder does exactly that:

1. **Genre check** — if the song's genre matches what you asked for, it earns 2 points. Genre is the biggest signal because it is the user's most direct self-described preference.
2. **Mood check** — if the mood matches (happy, chill, intense, etc.), the song earns 1 more point. Mood is next because it captures context — working out vs. winding down.
3. **Energy closeness** — rather than rewarding the loudest song, the system rewards songs that are *closest* to the user's requested energy level. A perfect energy match is worth 1 point; a song 0.5 away from the target earns nothing.
4. **Optional: Valence and Danceability** — if the user provides these preferences, the same closeness rule applies (up to 0.5 points each).

After every song gets a score, the list is sorted highest-to-lowest and the top five are returned along with a plain-English explanation of what drove each score.

---

## 4. Data

- **Catalog size:** 20 songs
- **Original starter:** 10 songs spanning pop, lofi, rock, ambient, jazz, synthwave, and indie pop
- **Added songs:** 10 new tracks covering edm, hip-hop, country, classical, metal, r&b, folk, reggae, blues, and trap — chosen to maximize genre and mood diversity
- **Features per song:** id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness
- **Numeric features** are on a 0.0–1.0 scale (except tempo_bpm which is raw BPM)
- **Missing from the dataset:** non-Western music traditions (K-pop, Afrobeats, Bollywood, Latin), spoken word, podcasts, classical sub-genres, mood states like "nostalgic" or "focused" are underrepresented

---

## 5. Strengths

- **Explainable by design.** Every recommendation comes with a sentence-level reason. Users can see exactly why a song was chosen.
- **Transparent weights.** The scoring constants (+2.0, +1.0) are in plain Python — no hidden neural layers, no opaque embeddings.
- **Works well for clear profiles.** When a user's requested genre is present in the catalog and a few songs match on multiple features, the top result is typically intuitive. The "Chill Lofi" and "Deep Intense Rock" profiles both returned results that matched human musical intuition.
- **Easy to extend.** Adding a new feature (tempo range preference, acousticness) requires only a few lines in `score_song`.

---

## 6. Limitations and Bias

**Filter bubble via genre weight.** The genre match is worth +2.0 points — twice the mood match and more than the entire energy score. This means a song that perfectly matches the user's energy and mood but is in a different genre will almost always lose to any song that matches genre, regardless of how much better it fits numerically. For large, diverse catalogs this is acceptable; for a 20-song catalog it means the top result is often predetermined.

**Pop overrepresentation.** Even with the expanded dataset, pop and lofi have more entries than niche genres like blues or reggae. A user requesting "blues/sad" will get Delta Midnight as the only genre+mood match, even if its energy profile is completely wrong.

**Binary categorical matching.** The system treats "rock" and "metal" as completely different genres — it earns zero points for a near-miss. Real users would likely consider an intense metal track a reasonable substitute for intense rock. There is no semantic distance between categories.

**No diversity enforcement.** The ranking algorithm always returns the closest matches. If three songs are almost identical (same genre, similar energy), all three will appear in the top five, starving the user of variety.

**Cold-start only.** The system has no memory. It cannot learn that a user always skips Gym Hero, or that they played Storm Runner 40 times in a row.

---

## 7. Evaluation

Four user profiles were tested against the full 20-song catalog:

| Profile | Top Result | Score | Matched Intuition? |
|---|---|---|---|
| High-Energy Pop (happy, energy 0.85) | Sunrise City | 4.89 | Yes — pop/happy/high-energy is a perfect fit |
| Chill Lofi (chill, energy 0.38) | Library Rain | 4.90 | Yes — lofi/chill songs ranked 1–3 |
| Deep Intense Rock (intense, energy 0.90) | Storm Runner | 4.94 | Yes — only rock/intense song in catalog |
| Adversarial: blues/sad/energy 0.90 | Delta Midnight | 3.46 | Partially — correct genre/mood, but energy was 0.33, not 0.90 |

**Surprises:**
- The adversarial profile revealed that the scoring system happily returns Delta Midnight despite a near-zero energy score, because the categorical bonuses (+2.0 genre, +1.0 mood) outweigh the numerical penalty. This is the system's biggest bias: it will always return the closest categorical match even when that match fails on every numeric dimension.
- Rooftop Lights (genre: indie pop) consistently placed #3 for the pop profile despite not technically matching the "pop" genre string. This is because mood and energy proximity are strong enough when the categorical match is close.

**Weight experiment:** Halving the genre weight from 2.0 to 1.0 and doubling the energy weight to 2.0 caused Gym Hero to overtake Sunrise City for the pop/happy profile, because Gym Hero's energy (0.93) is slightly closer to the target (0.85) than Sunrise City's (0.82). A 0.03 energy difference was enough to flip the top result.

---

## 8. Future Work

1. **Add semantic genre similarity.** Instead of binary genre matching, build a small distance matrix (rock→metal: 0.2, rock→jazz: 0.8) so near-genre songs can still earn partial credit.
2. **Enforce result diversity.** After ranking, apply a post-processing step that penalizes songs too similar to already-selected results (Maximal Marginal Relevance).
3. **Incorporate user feedback.** After each recommendation session, let the user mark thumbs up/down, then adjust the feature weights automatically using those signals.
4. **Expand and balance the catalog.** A real simulation should have at least 50–100 songs distributed evenly across genres and moods so that every profile has real competition.
5. **Add tempo preference.** BPM is already in the dataset but unused. A user who runs at 160 BPM would benefit from tempo matching.

---

## 9. Personal Reflection

Building VibeFinder 1.0 made the hidden assumptions in real recommenders very concrete. The moment I had to assign a number to "how much should genre matter vs. mood?" I realized there is no objectively correct answer — it is a design decision that encodes a theory of what music taste is. Real systems learn these weights from data (what users actually play), which is more accurate but also harder to inspect or challenge.

The adversarial profile was the most instructive test. A user asking for blues/sad/high-energy is expressing something real — think late-night electric blues — but my catalog and scoring logic cannot serve that. In a production system, this would be a "no result" failure mode that the team would only discover through user complaints, not unit tests.

The biggest shift in how I think about recommendation apps: every time Spotify or YouTube serves me a song, someone (or some gradient descent run) decided how much to weight genre vs. mood vs. listening history vs. what's trending. That's not neutral. It shapes taste, not just reflects it.
