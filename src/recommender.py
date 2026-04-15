import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """Represents a song and its audio/metadata attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """Represents a user's taste preferences for music recommendations."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """OOP wrapper around the scoring logic for use in tests and alternate UIs."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs ranked by score for the given user profile."""
        def _score(song: Song) -> float:
            score = 0.0
            if song.genre == user.favorite_genre:
                score += 2.0
            if song.mood == user.favorite_mood:
                score += 1.0
            energy_gap = abs(song.energy - user.target_energy)
            score += max(0.0, 1.0 - energy_gap * 2.0)
            if user.likes_acoustic:
                score += song.acousticness * 0.5
            return score

        return sorted(self.songs, key=_score, reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a song was recommended."""
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre match ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood match ({song.mood})")
        energy_gap = abs(song.energy - user.target_energy)
        energy_score = max(0.0, 1.0 - energy_gap * 2.0)
        reasons.append(f"energy score {energy_score:.2f}")
        if user.likes_acoustic and song.acousticness > 0.5:
            reasons.append(f"acoustic match ({song.acousticness:.2f})")
        return "; ".join(reasons) if reasons else "general recommendation"


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dicts with typed values."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = int(float(row["tempo_bpm"]))
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Score a single song against user preferences.

    Returns a (score, reasons) tuple where score is a float and reasons is a
    list of strings explaining which features contributed to the score.

    Scoring recipe:
      +2.0  genre match
      +1.0  mood match
      +0–1  energy proximity  (1.0 - gap*2, capped at 0)
      +0–0.5 valence proximity (if user provides target_valence)
      +0–0.5 danceability proximity (if user provides target_danceability)
    """
    score = 0.0
    reasons = []

    # Genre match: strongest signal (+2.0)
    if song["genre"].lower() == user_prefs.get("genre", "").lower():
        score += 2.0
        reasons.append("genre match (+2.0)")

    # Mood match: strong contextual signal (+1.0)
    if song["mood"].lower() == user_prefs.get("mood", "").lower():
        score += 1.0
        reasons.append("mood match (+1.0)")

    # Energy proximity: rewards closeness to target (up to +1.0)
    if "energy" in user_prefs:
        energy_gap = abs(song["energy"] - user_prefs["energy"])
        energy_score = round(max(0.0, 1.0 - energy_gap * 2.0), 2)
        score += energy_score
        reasons.append(f"energy proximity ({energy_score:+.2f})")

    # Valence (positivity) proximity: optional secondary signal (up to +0.5)
    if "valence" in user_prefs:
        valence_gap = abs(song["valence"] - user_prefs["valence"])
        valence_score = round(max(0.0, 0.5 - valence_gap), 2)
        score += valence_score
        reasons.append(f"valence proximity ({valence_score:+.2f})")

    # Danceability proximity: optional secondary signal (up to +0.5)
    if "danceability" in user_prefs:
        dance_gap = abs(song["danceability"] - user_prefs["danceability"])
        dance_score = round(max(0.0, 0.5 - dance_gap), 2)
        score += dance_score
        reasons.append(f"danceability proximity ({dance_score:+.2f})")

    return round(score, 2), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Score every song and return the top k results sorted by score descending.

    Each item in the returned list is a (song_dict, score, explanation) tuple.
    """
    scored = []
    for song in songs:
        song_score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons) if reasons else "no strong match"
        scored.append((song, song_score, explanation))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
