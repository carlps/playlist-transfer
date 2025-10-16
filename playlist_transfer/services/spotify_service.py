from typing import Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ..models import MusicService, Playlist, Track


class SpotifyService(MusicService):
    """Spotify API implementation"""

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.sp: spotipy.Spotify | None = None

    def authenticate(self) -> bool:
        """Authenticate with Spotify API"""
        try:

            print("Authenticating with Spotify...")

            # Use OAuth with user authorization
            # This will open a browser for the user to authorize
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri="http://127.0.0.1:8888/callback",
                scope="playlist-read-private playlist-modify-public playlist-modify-private",
            )

            self.sp = spotipy.Spotify(auth_manager=auth_manager)

            # Test authentication
            if self.sp:
                self.sp.current_user()
            print("✓ Spotify authentication successful")
            return True

        except Exception as e:
            print(f"❌ Spotify authentication failed: {e}")
            return False

    def get_playlist(self, playlist_id: str) -> Playlist:
        """Retrieve playlist from Spotify"""
        if not self.sp:
            raise RuntimeError("Not authenticated")

        try:
            # Get playlist details
            playlist = self.sp.playlist(playlist_id)

            # Extract all tracks (handle pagination)
            tracks = []
            results = playlist["tracks"]

            while results:
                for item in results["items"]:
                    if item["track"] is None:
                        continue  # Skip if track was removed

                    track_data = item["track"]

                    # Get primary artist
                    artist = (
                        track_data["artists"][0]["name"]
                        if track_data["artists"]
                        else "Unknown"
                    )

                    # Get ISRC if available
                    isrc = track_data.get("external_ids", {}).get("isrc")

                    tracks.append(
                        Track(
                            title=track_data["name"],
                            artist=artist,
                            album=track_data["album"]["name"],
                            isrc=isrc,
                            duration_ms=track_data["duration_ms"],
                            id=track_data["id"],
                            url=track_data["external_urls"].get("spotify"),
                        )
                    )

                # Get next page if it exists
                results = self.sp.next(results) if results["next"] else None

            return Playlist(
                name=playlist["name"],
                description=playlist.get("description"),
                tracks=tracks,
                public=playlist.get("public", False),
                id=playlist["id"],
                url=playlist["external_urls"].get("spotify"),
            )

        except Exception as e:
            raise RuntimeError(f"Failed to get Spotify playlist: {e}")

    def search_track(self, track: Track) -> Optional[Track]:
        """Search for track on Spotify"""
        if not self.sp:
            raise RuntimeError("Not authenticated")

        try:
            # Strategy 1: Search by ISRC (most accurate)
            if track.isrc:
                results = self.sp.search(q=f"isrc:{track.isrc}", type="track", limit=1)
                if results["tracks"]["items"]:
                    item = results["tracks"]["items"][0]
                    return Track(
                        title=item["name"],
                        artist=(
                            item["artists"][0]["name"] if item["artists"] else "Unknown"
                        ),
                        album=item["album"]["name"],
                        isrc=item.get("external_ids", {}).get("isrc"),
                        duration_ms=item["duration_ms"],
                        id=item["id"],
                        url=item["external_urls"].get("spotify"),
                    )

            # Strategy 2: Search by track name and artist
            query = f"track:{track.title} artist:{track.artist}"
            results = self.sp.search(q=query, type="track", limit=5)

            if not results["tracks"]["items"]:
                return None

            # Try to find best match
            for item in results["tracks"]["items"]:
                # Check if artist matches (case-insensitive)
                item_artists = [a["name"].lower() for a in item["artists"]]
                if track.artist.lower() in item_artists or any(
                    track.artist.lower() in a for a in item_artists
                ):
                    return Track(
                        title=item["name"],
                        artist=(
                            item["artists"][0]["name"] if item["artists"] else "Unknown"
                        ),
                        album=item["album"]["name"],
                        isrc=item.get("external_ids", {}).get("isrc"),
                        duration_ms=item["duration_ms"],
                        id=item["id"],
                        url=item["external_urls"].get("spotify"),
                    )

            # If no exact artist match, return first result
            item = results["tracks"]["items"][0]
            return Track(
                title=item["name"],
                artist=item["artists"][0]["name"] if item["artists"] else "Unknown",
                album=item["album"]["name"],
                isrc=item.get("external_ids", {}).get("isrc"),
                duration_ms=item["duration_ms"],
                id=item["id"],
                url=item["external_urls"].get("spotify"),
            )

        except Exception as e:
            print(f"    Warning: Search error: {e}")
            return None

    def create_playlist(
        self, name: str, description: Optional[str] = None, public: bool = False
    ) -> Playlist:
        """Create playlist on Spotify"""
        if not self.sp:
            raise RuntimeError("Not authenticated")

        try:
            user_id = self.sp.current_user()["id"]
            playlist = self.sp.user_playlist_create(
                user=user_id, name=name, public=public, description=description or ""
            )
            return Playlist(
                name=playlist["name"],
                description=playlist.get("description"),
                tracks=[],
                public=playlist.get("public", False),
                id=playlist["id"],
                url=playlist["external_urls"].get("spotify"),
            )

        except Exception as e:
            raise RuntimeError(f"Failed to create Spotify playlist: {e}")

    def add_tracks_to_playlist(self, playlist_id: str, track_ids: list[str]) -> bool:
        """Add tracks to Spotify playlist"""
        if not self.sp:
            raise RuntimeError("Not authenticated")

        try:
            # Spotify allows max 100 tracks per request
            batch_size = 100
            for i in range(0, len(track_ids), batch_size):
                batch = track_ids[i : i + batch_size]
                self.sp.playlist_add_items(playlist_id, batch)

            return True

        except Exception as e:
            raise RuntimeError(f"Failed to add tracks to Spotify playlist: {e}")
