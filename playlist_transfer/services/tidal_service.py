from typing import Optional
import tidalapi
from ..models import MusicService, Playlist, Track


class TidalService(MusicService):
    """Tidal API implementation"""

    def __init__(self, token_type: str = "oauth"):
        """
        Initialize Tidal service

        Args:
            token_type: Either "oauth" for interactive login or "token" for existing token
        """
        self.token_type = token_type
        self.session: tidalapi.Session | None = None

    def authenticate(self) -> bool:
        """Authenticate with Tidal API"""
        try:

            print("Authenticating with Tidal...")

            self.session = tidalapi.Session()

            if self.token_type == "oauth":
                # Interactive OAuth login
                print("Please visit the URL and authorize the application...")
                if self.session:
                    self.session.login_oauth_simple()
            else:
                # Load existing session (if previously authenticated)
                # The session is automatically saved to ~/.config/tidal-api/session.json
                if self.session and not self.session.load_oauth_session():  # type: ignore
                    print("No saved session found. Starting OAuth flow...")
                    self.session.login_oauth_simple()

            # Verify authentication
            if self.session and self.session.check_login():
                print("✓ Tidal authentication successful")
                return True
            else:
                print("❌ Tidal authentication failed")
                return False

        except Exception as e:
            print(f"❌ Tidal authentication failed: {e}")
            return False

    def get_playlist(self, playlist_id: str) -> Playlist:
        """Retrieve playlist from Tidal"""
        if not self.session:
            raise RuntimeError("Not authenticated")

        try:
            # Get playlist object
            playlist = self.session.playlist(playlist_id)

            if not playlist:
                raise RuntimeError(f"Playlist {playlist_id} not found")

            # Get all tracks
            tracks = []
            playlist_tracks = playlist.tracks()

            if playlist_tracks:
                for track in playlist_tracks:
                    if track is None:
                        continue

                    # Get primary artist
                    artist = track.artist.name if track.artist else "Unknown"

                    # Build Tidal URL
                    track_url = (
                        f"https://listen.tidal.com/track/{track.id}"
                        if track.id
                        else None
                    )

                    tracks.append(
                        Track(
                            title=track.name,
                            artist=artist,
                            album=track.album.name if track.album else None,
                            isrc=track.isrc if hasattr(track, "isrc") else None,
                            duration_ms=(
                                track.duration * 1000 if track.duration else None
                            ),
                            id=str(track.id) if track.id else None,
                            url=track_url,
                        )
                    )

            # Build Tidal playlist URL
            playlist_url = (
                f"https://listen.tidal.com/playlist/{playlist.id}"
                if playlist.id
                else None
            )

            # Note: Tidal API doesn't expose public/private status directly
            # We'll default to False (private) to be safe
            return Playlist(
                name=playlist.name,
                description=playlist.description,
                tracks=tracks,
                public=False,  # Tidal API doesn't provide this info
                id=playlist.id,
                url=playlist_url,
            )

        except Exception as e:
            raise RuntimeError(f"Failed to get Tidal playlist: {e}")

    def search_track(self, track: Track) -> Optional[Track]:
        """Search for track on Tidal with three-tier strategy"""
        if not self.session:
            raise RuntimeError("Not authenticated")

        try:
            # Strategy 1: Search by artist and cleaned track name, prioritize ISRC match
            query = f"{track.artist} {track.title_no_feature}"
            print("    🔄 Searching by artist and track name with ISRC matching...")
            search_results = self.session.search(
                query, models=[tidalapi.media.Track], limit=10
            )

            if (
                search_results
                and "tracks" in search_results
                and search_results["tracks"]
            ):
                # First, try to match by ISRC if available
                if track.isrc:
                    for result in search_results["tracks"]:
                        if hasattr(result, "isrc") and result.isrc == track.isrc:
                            artist = result.artist.name if result.artist else "Unknown"
                            track_url = (
                                f"https://listen.tidal.com/track/{result.id}"
                                if result.id
                                else None
                            )
                            return Track(
                                title=result.name,
                                artist=artist,
                                album=result.album.name if result.album else None,
                                isrc=result.isrc,
                                duration_ms=(
                                    result.duration * 1000 if result.duration else None
                                ),
                                id=str(result.id) if result.id else None,
                                url=track_url,
                            )

                # Save these results for Strategy 3 fallback
                first_search_results = search_results["tracks"]
            else:
                first_search_results = []

            # Strategy 2: Search by cleaned track name only, max limit
            if track.isrc:
                print("    🔄 Searching by track name only with ISRC matching...")
                query = track.title_no_feature
                # Get maximum results and handle pagination
                search_results = self.session.search(
                    query, models=[tidalapi.media.Track], limit=300
                )

                if search_results and "tracks" in search_results:
                    all_results = search_results["tracks"]

                    # Check all results for ISRC match
                    for result in all_results:
                        if hasattr(result, "isrc") and result.isrc == track.isrc:
                            artist = result.artist.name if result.artist else "Unknown"
                            track_url = (
                                f"https://listen.tidal.com/track/{result.id}"
                                if result.id
                                else None
                            )
                            return Track(
                                title=result.name,
                                artist=artist,
                                album=result.album.name if result.album else None,
                                isrc=result.isrc,
                                duration_ms=(
                                    result.duration * 1000 if result.duration else None
                                ),
                                id=str(result.id) if result.id else None,
                                url=track_url,
                            )

            # Strategy 3: Fall back to first search results, match by artist and title
            if first_search_results:
                print("    🔄 Matching by artist and title from first search...")
                for result in first_search_results:
                    if result.artist:
                        result_artist = result.artist.name.lower()
                        search_artist = track.artist.lower()

                        # Check if artist matches
                        if (
                            search_artist in result_artist
                            or result_artist in search_artist
                        ):
                            artist = result.artist.name
                            track_url = (
                                f"https://listen.tidal.com/track/{result.id}"
                                if result.id
                                else None
                            )
                            return Track(
                                title=result.name,
                                artist=artist,
                                album=result.album.name if result.album else None,
                                isrc=result.isrc if hasattr(result, "isrc") else None,
                                duration_ms=(
                                    result.duration * 1000 if result.duration else None
                                ),
                                id=str(result.id) if result.id else None,
                                url=track_url,
                            )

                # If no artist match found, return first result as last resort
                result = first_search_results[0]
                artist = result.artist.name if result.artist else "Unknown"
                track_url = (
                    f"https://listen.tidal.com/track/{result.id}" if result.id else None
                )
                return Track(
                    title=result.name,
                    artist=artist,
                    album=result.album.name if result.album else None,
                    isrc=result.isrc if hasattr(result, "isrc") else None,
                    duration_ms=result.duration * 1000 if result.duration else None,
                    id=str(result.id) if result.id else None,
                    url=track_url,
                )

            return None

        except Exception as e:
            print(f"    Warning: Search error: {e}")
            return None

    def create_playlist(
        self, name: str, description: Optional[str] = None, public: bool = False
    ) -> Playlist:
        """Create playlist on Tidal"""
        if not self.session:
            raise RuntimeError("Not authenticated")

        try:
            # Get current user
            user = self.session.user
            if not user:
                raise RuntimeError("Could not get current user")

            # Create playlist
            playlist = user.create_playlist(name, description or "")

            # Build Tidal playlist URL
            playlist_url = (
                f"https://listen.tidal.com/playlist/{playlist.id}"
                if playlist.id
                else None
            )

            # Note: Tidal API doesn't seem to support setting public/private via the library
            # Playlists are private by default
            if public:
                print(
                    "    Note: Tidal API doesn't support setting "
                    "playlist visibility. Playlist will be private."
                )

            return Playlist(
                name=playlist.name,
                description=playlist.description,
                tracks=[],
                public=False,
                id=playlist.id,
                url=playlist_url,
            )

        except Exception as e:
            raise RuntimeError(f"Failed to create Tidal playlist: {e}")

    def add_tracks_to_playlist(self, playlist_id: str, track_ids: list[str]) -> bool:
        """Add tracks to Tidal playlist"""
        if not self.session:
            raise RuntimeError("Not authenticated")

        try:
            # Get playlist object
            playlist = self.session.playlist(playlist_id)

            if not playlist:
                raise RuntimeError(f"Playlist {playlist_id} not found")

            # Convert string IDs to integers
            track_ids_int = [int(tid) for tid in track_ids]

            # Add tracks in batches (Tidal can handle larger batches than Spotify)
            batch_size = 100
            for i in range(0, len(track_ids_int), batch_size):
                batch = track_ids_int[i : i + batch_size]
                playlist.add(batch)

            return True

        except Exception as e:
            raise RuntimeError(f"Failed to add tracks to Tidal playlist: {e}")
