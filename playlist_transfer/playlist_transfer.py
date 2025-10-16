from typing import Optional
from .models import MusicService, Playlist


class PlaylistTransfer:
    """Main class for transferring playlists between services"""

    def __init__(self, source: MusicService, destination: MusicService):
        self.source = source
        self.destination = destination

    def transfer(
        self,
        source_playlist_id: str,
        destination_name: Optional[str] = None,
        detail_log_file: Optional[str] = None,
    ) -> bool:
        """Transfer a playlist from source to destination"""
        print("\n🎵 Starting playlist transfer...")

        # Authenticate both services
        if not self.source.authenticate():
            print("❌ Failed to authenticate with source service")
            return False

        if not self.destination.authenticate():
            print("❌ Failed to authenticate with destination service")
            return False

        # Get source playlist
        print("\n📥 Fetching playlist from source...")
        try:
            source_playlist = self.source.get_playlist(source_playlist_id)
            print(f"✓ Found playlist: {source_playlist}")
        except Exception as e:
            print(f"❌ Failed to get playlist: {e}")
            return False

        # Create destination playlist
        if not destination_name:
            dest_name = f"{source_playlist.name} (transferred)"
            print(f"no destincation name provided, so using {dest_name}")
        else:
            dest_name = destination_name
            print(f"using provided desitnation name {dest_name}")
        print(f"\n📤 Creating playlist on destination: {dest_name}")
        print(f"   Visibility: {'public' if source_playlist.public else 'private'}")
        try:
            dest_playlist = self.destination.create_playlist(
                dest_name, source_playlist.description, source_playlist.public
            )
            print(f"✓ Created playlist with ID: {dest_playlist.id}")
        except Exception as e:
            print(f"❌ Failed to create playlist: {e}")
            return False

        # Search and add tracks
        print(f"\n🔍 Searching for {len(source_playlist.tracks)} tracks...")
        found_tracks = []
        track_mapping = []  # For detailed logging

        for i, source_track in enumerate(source_playlist.tracks, 1):
            print(f"  [{i}/{len(source_playlist.tracks)}] Searching: {source_track}")
            try:
                dest_track = self.destination.search_track(source_track)
                if dest_track and dest_track.id:
                    found_tracks.append(dest_track.id)
                    track_mapping.append(
                        {
                            "source": source_track,
                            "destination": dest_track,
                            "found": True,
                        }
                    )
                    print("    ✓ Found")
                else:
                    track_mapping.append(
                        {"source": source_track, "destination": None, "found": False}
                    )
                    print("    ✗ Not found")
            except Exception as e:
                print(f"    ✗ Error: {e}")
                track_mapping.append(
                    {"source": source_track, "destination": None, "found": False}
                )

        # Add found tracks to playlist
        if found_tracks:
            print(f"\n➕ Adding {len(found_tracks)} tracks to playlist...")
            try:
                # Ensure playlist_id and track_ids are not None
                if dest_playlist.id:
                    self.destination.add_tracks_to_playlist(
                        dest_playlist.id, found_tracks
                    )
                    print("✓ Successfully added tracks")
            except Exception as e:
                print(f"❌ Failed to add tracks: {e}")
                return False

        # Generate detailed log if requested
        if detail_log_file:
            print(f"\n📝 Writing detailed log to {detail_log_file}...")
            try:
                self._write_detail_log(
                    detail_log_file, source_playlist, dest_playlist, track_mapping
                )
                print("✓ Log file written successfully")
            except Exception as e:
                print(f"⚠️  Warning: Failed to write log file: {e}")

        # Summary
        not_found_count = len([m for m in track_mapping if not m["found"]])
        print("\n✅ Transfer complete!")
        print(f"   Tracks found: {len(found_tracks)}/{len(source_playlist.tracks)}")
        if not_found_count > 0:
            print(f"   ⚠️  Tracks not found: {not_found_count}")
            not_found = [m["source"] for m in track_mapping if not m["found"]]
            for track in not_found[:5]:  # Show first 5
                print(f"      - {track}")
            if len(not_found) > 5:
                print(f"      ... and {len(not_found) - 5} more")

        return True

    def _write_detail_log(
        self,
        filename: str,
        source_playlist: Playlist,
        dest_playlist: Playlist,
        track_mapping: list[dict],
    ):
        """Write detailed CSV log of the transfer"""
        import csv
        from pathlib import Path

        # Create parent directories if they don't exist
        log_path = Path(filename)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Header section
            writer.writerow(["Playlist Transfer Log"])
            writer.writerow([])
            writer.writerow(["Source Playlist:", source_playlist.name])
            writer.writerow(["Source URL:", source_playlist.url or "N/A"])
            writer.writerow(["Destination Playlist:", dest_playlist.name])
            writer.writerow(["Destination URL:", dest_playlist.url or "N/A"])
            writer.writerow([])

            # Track details header
            writer.writerow(
                [
                    "Status",
                    "Source Title",
                    "Source Artist",
                    "Source Album",
                    "Source ISRC",
                    "Source URL",
                    "Destination Title",
                    "Destination Artist",
                    "Destination Album",
                    "Destination ISRC",
                    "Destination URL",
                ]
            )

            # Track details
            for mapping in track_mapping:
                source = mapping["source"]
                dest = mapping.get("destination")
                status = "✓ Found" if mapping["found"] else "✗ Not Found"

                writer.writerow(
                    [
                        status,
                        source.title,
                        source.artist,
                        source.album or "",
                        source.isrc or "",
                        source.url or "",
                        dest.title if dest else "",
                        dest.artist if dest else "",
                        dest.album if dest else "",
                        dest.isrc if dest else "",
                        dest.url if dest else "",
                    ]
                )
