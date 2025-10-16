"""
Tests for data models (Track and Playlist)
"""

import pytest
from playlist_transfer.models import Track, Playlist


class TestTrack:
    """Test Track model functionality"""

    def test_track_creation(self, sample_track):
        """Test basic track creation"""
        assert sample_track.title == "Sample Song"
        assert sample_track.artist == "Sample Artist"
        assert sample_track.album == "Sample Album"
        assert sample_track.isrc == "USSAMPLE123"
        assert sample_track.duration_ms == 180000

    def test_track_string_representation(self, sample_track):
        """Test track __str__ method"""
        assert str(sample_track) == "Sample Artist - Sample Song"

    def test_track_without_optional_fields(self):
        """Test track creation with only required fields"""
        track = Track(title="Test", artist="Artist")
        assert track.title == "Test"
        assert track.artist == "Artist"
        assert track.album is None
        assert track.isrc is None
        assert track.duration_ms is None

    def test_title_no_feature_with_feat(self):
        """Test removal of 'feat.' from track title"""
        track = Track(title="Song Name (feat. Guest Artist)", artist="Main Artist")
        assert track.title_no_feature == "Song Name"

    def test_title_no_feature_with_ft(self):
        """Test removal of 'ft.' from track title"""
        track = Track(title="Song Name (ft. Guest)", artist="Main Artist")
        assert track.title_no_feature == "Song Name"

    def test_title_no_feature_with_featuring(self):
        """Test removal of 'featuring' from track title"""
        track = Track(title="Song Name (featuring Someone)", artist="Main Artist")
        assert track.title_no_feature == "Song Name"

    def test_title_no_feature_with_with(self):
        """Test removal of 'with' from track title"""
        track = Track(title="Song Name (with Someone)", artist="Main Artist")
        assert track.title_no_feature == "Song Name"

    def test_title_no_feature_with_brackets(self):
        """Test removal of featured artists in brackets"""
        track = Track(title="Song Name [feat. Guest]", artist="Main Artist")
        assert track.title_no_feature == "Song Name"

    def test_title_no_feature_no_feature(self):
        """Test that clean titles remain unchanged"""
        track = Track(title="Clean Song Name", artist="Main Artist")
        assert track.title_no_feature == "Clean Song Name"

    def test_title_no_feature_multiple_spaces(self):
        """Test that extra whitespace is cleaned up"""
        track = Track(title="Song  Name   (feat. Guest)", artist="Main Artist")
        assert track.title_no_feature == "Song Name"

    def test_title_no_feature_case_insensitive(self):
        """Test that feature removal is case insensitive"""
        track = Track(title="Song (FEAT. Guest)", artist="Main Artist")
        assert track.title_no_feature == "Song"

        track2 = Track(title="Song (FT. Guest)", artist="Main Artist")
        assert track2.title_no_feature == "Song"


class TestPlaylist:
    """Test Playlist model functionality"""

    def test_playlist_creation(self, sample_playlist):
        """Test basic playlist creation"""
        assert sample_playlist.name == "Sample Playlist"
        assert sample_playlist.description == "A test playlist"
        assert len(sample_playlist.tracks) == 2
        assert sample_playlist.public is True
        assert sample_playlist.id == "playlist_123"

    def test_playlist_string_representation(self, sample_playlist):
        """Test playlist __str__ method"""
        result = str(sample_playlist)
        assert "Sample Playlist" in result
        assert "2 tracks" in result
        assert "public" in result

    def test_private_playlist_string(self):
        """Test string representation for private playlist"""
        playlist = Playlist(name="Private", description=None, tracks=[], public=False)
        result = str(playlist)
        assert "private" in result

    def test_empty_playlist(self):
        """Test playlist with no tracks"""
        playlist = Playlist(name="Empty", description=None, tracks=[], public=False)
        assert len(playlist.tracks) == 0
        assert "0 tracks" in str(playlist)

    def test_playlist_without_optional_fields(self):
        """Test playlist creation with minimal fields"""
        playlist = Playlist(name="Test", description=None, tracks=[])
        assert playlist.name == "Test"
        assert playlist.description is None
        assert playlist.tracks == []
        assert playlist.public is False
        assert playlist.id is None
        assert playlist.url is None
