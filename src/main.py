"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:
    python -m src.main
"""

import os
import sys

# Allow running as both `python -m src.main` and `python src/main.py`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recommender import load_songs, recommend_songs


def print_recommendations(label: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print a formatted recommendation block for one user profile."""
    print("=" * 60)
    print(f"Profile: {label}")
    print(f"Preferences: {user_prefs}")
    print("=" * 60)

    recommendations = recommend_songs(user_prefs, songs, k=k)
    if not recommendations:
        print("  No recommendations generated.\n")
        return

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"  #{rank}  {song['title']} by {song['artist']}")
        print(f"       Genre: {song['genre']} | Mood: {song['mood']} | Energy: {song['energy']}")
        print(f"       Score: {score:.2f}")
        print(f"       Why:   {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs from catalog.\n")

    # --- Profile 1: High-Energy Pop ---
    pop_profile = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "valence": 0.80,
        "danceability": 0.80,
    }

    # --- Profile 2: Chill Lofi ---
    lofi_profile = {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "valence": 0.58,
        "danceability": 0.60,
    }

    # --- Profile 3: Deep Intense Rock ---
    rock_profile = {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.90,
        "valence": 0.45,
        "danceability": 0.65,
    }

    # --- Profile 4 (adversarial): Conflicting preferences ---
    # High energy but sad mood — tests whether the system handles contradictions
    adversarial_profile = {
        "genre": "blues",
        "mood": "sad",
        "energy": 0.90,
        "valence": 0.35,
    }

    print_recommendations("High-Energy Pop",    pop_profile,         songs)
    print_recommendations("Chill Lofi",         lofi_profile,        songs)
    print_recommendations("Deep Intense Rock",  rock_profile,        songs)
    print_recommendations("Adversarial (blues/sad/high-energy)", adversarial_profile, songs)


if __name__ == "__main__":
    main()
