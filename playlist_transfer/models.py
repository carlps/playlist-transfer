from abc import ABC, abstractmethod
from dataclasses import dataclass
import re
from typing import List, Optional


@dataclass
class Track:
    """Represents a music track with search-relevant metadata"""

    title: str
    artist: str
    album: Optional[str] = None
    isrc: Optional[str] = None  # International Standard Recording Code
    duration_ms: Optional[int] = None
    id: Optional[str] = None  # Track ID in the service
    url: Optional[str] = None  # Link to track

    def __str__(self):
        return f"{self.artist} - {self.title}"

    @property
    def title_no_feature(self) -> str:
        """
        Some services search better without including the featured artist in
        the title, so offer this as a chance to better find it.
        """
        # Patterns to match featured artist notations
        # Using word boundaries and optional punctuation
        patterns = [
            r"\s*[\(\[]feat\.?\s+[^\)\]]+[\)\]]",  # (feat. ...) or [feat. ...]
            r"\s*[\(\[]ft\.?\s+[^\)\]]+[\)\]]",  # (ft. ...) or [ft. ...]
            r"\s*[\(\[]featuring\s+[^\)\]]+[\)\]]",  # (featuring ...)
            r"\s*[\(\[]with\s+[^\)\]]+[\)\]]",  # (with ...)
        ]

        cleaned = self.title
        for pattern in patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        # Clean up any extra whitespace and trailing punctuation
        cleaned = cleaned.strip()
        cleaned = re.sub(r"\s+", " ", cleaned)  # Multiple spaces to single space

        return cleaned


@dataclass
class Playlist:
    """Represents a playlist with metadata"""

    name: str
    description: Optional[str]
    tracks: List[Track]
    public: bool = False
    id: Optional[str] = None  # Playlist ID in the service
    url: Optional[str] = None  # Link to playlist

    def __str__(self):
        visibility = "public" if self.public else "private"
        return f"{self.name} ({len(self.tracks)} tracks, {visibility})"


class MusicService(ABC):
    """Abstract base class for music streaming services"""

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the service. Returns True if successful."""
        pass

    @abstractmethod
    def get_playlist(self, playlist_id: str) -> Playlist:
        """Retrieve a playlist by ID"""
        pass

    @abstractmethod
    def search_track(self, track: Track) -> Optional[Track]:
        """
        Search for a track and return a Track object with the service's ID and URL.
        Returns None if not found.
        """
        pass

    @abstractmethod
    def create_playlist(
        self, name: str, description: Optional[str] = None, public: bool = False
    ) -> Playlist:
        """Create a new playlist and return a Playlist object with ID and URL"""
        pass

    @abstractmethod
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> bool:
        """Add tracks to a playlist. Returns True if successful."""
        pass
