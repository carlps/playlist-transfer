"""Tests for PlaylistTransfer class"""

import tempfile
import csv
from pathlib import Path
from playlist_transfer.playlist_transfer import PlaylistTransfer
from playlist_transfer.models import Playlist
from tests.conftest import MockMusicService


class TestPlaylistTransfer:
    """Test PlaylistTransfer functionality"""

    def test_successful_transfer(
        self, mock_source_service, mock_destination_service, capsys
    ):
        """Test successful playlist transfer"""
        transfer = PlaylistTransfer(mock_source_service, mock_destination_service)

        result = transfer.transfer("test_playlist_123")

        assert result is True
        assert mock_source_service.authenticated
        assert mock_destination_service.authenticated
        assert len(mock_destination_service.created_playlists) == 1
        assert mock_destination_service.created_playlists[0].name.endswith(
            "(transferred)"
        )

    def test_transfer_with_custom_name(
        self, mock_source_service, mock_destination_service
    ):
        """Test transfer with custom playlist name"""
        transfer = PlaylistTransfer(mock_source_service, mock_destination_service)

        result = transfer.transfer("test_playlist_123", destination_name="Custom Name")

        assert result is True
        assert mock_destination_service.created_playlists[0].name == "Custom Name"

    def test_source_authentication_failure(self, mock_destination_service, capsys):
        """Test handling of source authentication failure"""
        failing_source = MockMusicService(name="source", should_fail=True)
        transfer = PlaylistTransfer(failing_source, mock_destination_service)

        result = transfer.transfer("test_playlist_123")

        assert result is False
        captured = capsys.readouterr()
        assert "Failed to authenticate with source service" in captured.out

    def test_destination_authentication_failure(self, mock_source_service, capsys):
        """Test handling of destination authentication failure"""
        failing_destination = MockMusicService(name="destination", should_fail=True)
        transfer = PlaylistTransfer(mock_source_service, failing_destination)

        result = transfer.transfer("test_playlist_123")

        assert result is False
        captured = capsys.readouterr()
        assert "Failed to authenticate with destination service" in captured.out

    def test_get_playlist_failure(self, mock_destination_service, capsys):
        """Test handling of playlist retrieval failure"""

        # Create a source that will fail on get_playlist
        class FailingSource(MockMusicService):
            def get_playlist(self, playlist_id: str) -> Playlist:
                if not self.authenticated:
                    raise RuntimeError("Not authenticated")
                raise RuntimeError("Failed to get playlist")

        failing_source = FailingSource(name="source")
        transfer = PlaylistTransfer(failing_source, mock_destination_service)

        result = transfer.transfer("test_playlist_123")

        assert result is False
        captured = capsys.readouterr()
        assert "Failed to get playlist" in captured.out

    def test_create_playlist_failure(self, mock_source_service, capsys):
        """Test handling of playlist creation failure"""

        # Create a destination that will fail on create_playlist
        class FailingDestination(MockMusicService):
            def create_playlist(
                self, name: str, description=None, public=False
            ) -> Playlist:
                if not self.authenticated:
                    raise RuntimeError("Not authenticated")
                raise RuntimeError("Failed to create playlist")

        failing_destination = FailingDestination(name="destination")
        transfer = PlaylistTransfer(mock_source_service, failing_destination)

        result = transfer.transfer("test_playlist_123")

        assert result is False
        captured = capsys.readouterr()
        assert "Failed to create playlist" in captured.out

    def test_tracks_found_and_added(
        self, mock_source_service, mock_destination_service
    ):
        """Test that found tracks are added to destination playlist"""
        transfer = PlaylistTransfer(mock_source_service, mock_destination_service)

        result = transfer.transfer("test_playlist_123")

        assert result is True
        # Check that tracks were added
        playlist_id = mock_destination_service.created_playlists[0].id
        assert playlist_id in mock_destination_service.added_tracks
        assert len(mock_destination_service.added_tracks[playlist_id]) == 3

    def test_track_not_found(self, mock_source_service, mock_destination_service):
        """Test handling when some tracks are not found"""
        # Set up destination to not find certain tracks
        mock_destination_service.search_results[
            "Test Artist 2_Test Song 2 (feat. Guest)"
        ] = None

        transfer = PlaylistTransfer(mock_source_service, mock_destination_service)
        result = transfer.transfer("test_playlist_123")

        # Transfer should still succeed
        assert result is True
        # Only 2 tracks should be added (3rd one not found)
        playlist_id = mock_destination_service.created_playlists[0].id
        assert len(mock_destination_service.added_tracks[playlist_id]) == 2

    def test_detail_log_file_creation(
        self, mock_source_service, mock_destination_service
    ):
        """Test that detail log file is created correctly"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            log_file = tmp.name

        try:
            transfer = PlaylistTransfer(mock_source_service, mock_destination_service)
            result = transfer.transfer("test_playlist_123", detail_log_file=log_file)

            assert result is True
            assert Path(log_file).exists()

            # Read and verify log contents
            with open(log_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)

                # Check header information
                assert rows[0][0] == "Playlist Transfer Log"
                assert any("Source Playlist:" in str(row) for row in rows if row)
                assert any("Destination Playlist:" in str(row) for row in rows if row)

                # Find track details section
                track_header_idx = None
                for i, row in enumerate(rows):
                    if row and len(row) > 0 and row[0] == "Status":
                        track_header_idx = i
                        break

                assert track_header_idx is not None
                # Should have 3 tracks
                track_rows = [
                    r for r in rows[track_header_idx + 1 :] if r and len(r) > 0
                ]
                assert len(track_rows) == 3

        finally:
            # Cleanup
            if Path(log_file).exists():
                Path(log_file).unlink()

    def test_detail_log_with_not_found_tracks(
        self, mock_source_service, mock_destination_service
    ):
        """Test that detail log correctly shows not found tracks"""
        # Make second track not findable
        mock_destination_service.search_results[
            "Test Artist 2_Test Song 2 (feat. Guest)"
        ] = None

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            log_file = tmp.name

        try:
            transfer = PlaylistTransfer(mock_source_service, mock_destination_service)
            result = transfer.transfer("test_playlist_123", detail_log_file=log_file)

            assert result is True

            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                # Check for "Not Found" status
                assert "✗ Not Found" in content
                assert "✓ Found" in content

        finally:
            if Path(log_file).exists():
                Path(log_file).unlink()

    def test_detail_log_directory_creation(
        self, mock_source_service, mock_destination_service
    ):
        """Test that log file directories are created if they don't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "subdir1" / "subdir2" / "transfer.csv"

            transfer = PlaylistTransfer(mock_source_service, mock_destination_service)
            result = transfer.transfer(
                "test_playlist_123", detail_log_file=str(log_file)
            )

            assert result is True
            assert log_file.exists()
            assert log_file.parent.exists()

    def test_empty_playlist_transfer(self, mock_destination_service):
        """Test transferring an empty playlist"""
        empty_source = MockMusicService(name="source")
        # Override to return empty playlist
        original_get = empty_source.get_playlist

        def get_empty_playlist(playlist_id):
            playlist = original_get(playlist_id)
            playlist.tracks = []
            return playlist

        empty_source.get_playlist = get_empty_playlist

        transfer = PlaylistTransfer(empty_source, mock_destination_service)
        result = transfer.transfer("test_playlist_123")

        assert result is True
        # Playlist should be created even if empty
        assert len(mock_destination_service.created_playlists) == 1
        # No tracks should be added
        playlist_id = mock_destination_service.created_playlists[0].id
        assert playlist_id not in mock_destination_service.added_tracks

    def test_playlist_visibility_preserved(
        self, mock_source_service, mock_destination_service
    ):
        """Test that playlist public/private status is preserved"""
        # Make source playlist public
        original_get = mock_source_service.get_playlist

        def get_public_playlist(playlist_id):
            playlist = original_get(playlist_id)
            playlist.public = True
            return playlist

        mock_source_service.get_playlist = get_public_playlist

        transfer = PlaylistTransfer(mock_source_service, mock_destination_service)
        result = transfer.transfer("test_playlist_123")

        assert result is True
        created_playlist = mock_destination_service.created_playlists[0]
        assert created_playlist.public is True
