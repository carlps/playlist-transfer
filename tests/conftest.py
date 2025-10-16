"""
Fixtures and test utilities shared across test modules
"""

import pytest
from playlist_transfer.models import Track, Playlist, MusicService
from typing import Optional, List


class MockMusicService(MusicService):
    """Mock music service for testing"""

    def __init__(self, name: str = "mock", should_fail: bool = False):
        self.name = name
        self.should_fail = should_fail
        self.authenticated = False
        self.created_playlists = []
        self.added_tracks = {}
        self.search_results = {}

    def authenticate(self) -> bool:
        if self.should_fail:
            return False
        self.authenticated = True
        return True

    def get_playlist(self, playlist_id: str) -> Playlist:
        if not self.authenticated:
            raise RuntimeError("Not authenticated")
        if self.should_fail:
            raise RuntimeError("Failed to get playlist")

        # Return a mock playlist
        return Playlist(
            name=f"Test Playlist {playlist_id}",
            description="Test description",
            tracks=[
                Track(
                    title="Test Song 1",
                    artist="Test Artist 1",
                    album="Test Album 1",
                    isrc="USTEST1234567",
                    duration_ms=180000,
                    id=f"{self.name}_track_1",
                    url=f"https://{self.name}.com/track/1",
                ),
                Track(
                    title="Test Song 2 (feat. Guest)",
                    artist="Test Artist 2",
                    album="Test Album 2",
                    isrc="USTEST7654321",
                    duration_ms=200000,
                    id=f"{self.name}_track_2",
                    url=f"https://{self.name}.com/track/2",
                ),
                Track(
                    title="Song Without ISRC",
                    artist="Test Artist 3",
                    album="Test Album 3",
                    isrc=None,
                    duration_ms=150000,
                    id=f"{self.name}_track_3",
                    url=f"https://{self.name}.com/track/3",
                ),
            ],
            public=False,
            id=playlist_id,
            url=f"https://{self.name}.com/playlist/{playlist_id}",
        )

    def search_track(self, track: Track) -> Optional[Track]:
        if not self.authenticated:
            raise RuntimeError("Not authenticated")

        # Check if we have a predefined result for this track
        search_key = f"{track.artist}_{track.title}"
        if search_key in self.search_results:
            return self.search_results[search_key]

        # Default behavior: return a mock track with the service's ID
        if self.should_fail or track.title == "Not Found Track":
            return None

        return Track(
            title=track.title,
            artist=track.artist,
            album=track.album,
            isrc=track.isrc,
            duration_ms=track.duration_ms,
            id=f"{self.name}_{track.title.replace(' ', '_').lower()}",
            url=f"https://{self.name}.com/track/{track.title.replace(' ', '_').lower()}",
        )

    def create_playlist(
        self, name: str, description: Optional[str] = None, public: bool = False
    ) -> Playlist:
        if not self.authenticated:
            raise RuntimeError("Not authenticated")
        if self.should_fail:
            raise RuntimeError("Failed to create playlist")

        playlist = Playlist(
            name=name,
            description=description,
            tracks=[],
            public=public,
            id=f"{self.name}_playlist_{len(self.created_playlists)}",
            url=f"https://{self.name}.com/playlist/{len(self.created_playlists)}",
        )
        self.created_playlists.append(playlist)
        return playlist

    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> bool:
        if not self.authenticated:
            raise RuntimeError("Not authenticated")
        if self.should_fail:
            raise RuntimeError("Failed to add tracks")

        self.added_tracks[playlist_id] = track_ids
        return True


@pytest.fixture
def mock_source_service():
    """Fixture providing a mock source service"""
    return MockMusicService(name="source")


@pytest.fixture
def mock_destination_service():
    """Fixture providing a mock destination service"""
    return MockMusicService(name="destination")


@pytest.fixture
def sample_track():
    """Fixture providing a sample track"""
    return Track(
        title="Sample Song",
        artist="Sample Artist",
        album="Sample Album",
        isrc="USSAMPLE123",
        duration_ms=180000,
        id="sample_track_123",
        url="https://example.com/track/123",
    )


@pytest.fixture
def sample_playlist():
    """Fixture providing a sample playlist"""
    return Playlist(
        name="Sample Playlist",
        description="A test playlist",
        tracks=[
            Track(
                title="Song 1",
                artist="Artist 1",
                album="Album 1",
                isrc="US1234567890",
                duration_ms=180000,
                id="track_1",
                url="https://example.com/track/1",
            ),
            Track(
                title="Song 2",
                artist="Artist 2",
                album="Album 2",
                isrc="US0987654321",
                duration_ms=200000,
                id="track_2",
                url="https://example.com/track/2",
            ),
        ],
        public=True,
        id="playlist_123",
        url="https://example.com/playlist/123",
    )


@pytest.fixture
def track_with_features():
    """Fixture providing a track with featured artists in various formats"""
    return Track(
        title="Main Song (feat. Guest Artist)",
        artist="Main Artist",
        album="Test Album",
        isrc="USTEST999",
        duration_ms=190000,
    )
