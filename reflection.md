# Reflection

## Profile Comparisons

### High-Energy Pop vs. Chill Lofi

These two profiles produced completely non-overlapping top-5 lists, which is exactly what you'd hope for. The pop profile surfaced Sunrise City and Gym Hero — both high-BPM, bright, danceable tracks. The lofi profile returned Library Rain and Midnight Coding — low-energy, high-acousticness, subdued songs built for focus or background listening.

What changed: the genre and energy weights moved the entire ranking. When genre flips from "pop" to "lofi" and the target energy drops from 0.85 to 0.38, the algorithm's sense of "good" completely reverses. A song like Gym Hero (energy 0.93) that was #2 for the pop profile doesn't appear at all in the lofi top-5.

This makes sense. A "chill lofi" listener and a "high-energy pop" listener want fundamentally different things from music, and the algorithm correctly treats them as separate audiences.

### Deep Intense Rock vs. High-Energy Pop

Both profiles ask for high energy (0.85 and 0.90 respectively), but different genres and moods. The overlap in their top-5 is minimal: Gym Hero appears in both because its energy and danceability match both profiles' numerical targets, but Storm Runner only appears for the rock profile.

What changed: the genre string flips from "pop" to "rock", which redistributes the +2.0 genre bonus entirely. This is the most important variable in the scoring system. Because genre is worth 2 points and the total score for most songs is 3–5 points, changing the genre preference effectively reshuffles the entire leaderboard.

What it tells us: the algorithm is highly genre-sensitive. Mood and energy are tiebreakers within a genre, not independent signals. If you are outside the user's stated genre, you need near-perfect energy and mood alignment to compete.

### Deep Intense Rock vs. Adversarial (blues/sad/high-energy)

Both profiles want high energy. The rock profile gets a fully satisfying top result (Storm Runner, score 4.94). The adversarial profile gets Delta Midnight (score 3.46) — a low-energy blues track that happens to match genre and mood, but completely fails on the energy dimension.

What changed: requesting an underrepresented genre (blues) with a contradictory mood/energy combination (sad + high-energy) exposed the catalog's coverage gap. The algorithm surfaced the only blues/sad entry regardless of its energy score being 0.0. This is the system prioritizing categorical match over numerical fit, which can feel wrong.

This comparison is the clearest demonstration of the system's core bias: **categorical features dominate.** A perfect genre+mood match will almost always beat a song that fits your energy profile better but is in a different genre. In a 20-song catalog, this means some profiles are essentially pre-determined — whoever holds the matching genre/mood pair wins.

## Summary

The recommender works well when the user's preferences align with a cluster of similar songs in the catalog. It struggles when preferences are contradictory, the desired genre is underrepresented, or the user values a numerical feature (energy, tempo) more than a categorical one (genre, mood). The weights I chose reflect one reasonable theory of music taste; someone else might weight mood more heavily than genre, or add tempo as a primary signal. That choice is not obvious from the code — it's a hidden design decision with real consequences for who the system serves well.
