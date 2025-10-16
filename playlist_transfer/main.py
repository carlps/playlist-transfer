"""
Main CLI entry point with config file and environment variable support
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv


def load_config(config_path=None):
    """
    Load configuration from JSON file.
    Searches in default locations if no path specified.
    """
    if config_path is None:
        # Check default locations in order of preference
        config_locations = [
            Path("config.json"),  # Current directory
            Path.home() / ".config" / "playlist-transfer" / "config.json",
            Path.home() / ".playlist-transfer.json",
        ]

        for location in config_locations:
            if location.exists():
                config_path = location
                print(f"📄 Using config file: {config_path}")
                break

    if config_path and Path(config_path).exists():
        try:
            with open(config_path) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠️  Warning: Invalid JSON in config file: {e}")
            return {}

    return {}


def load_env_file(env_path=None):
    """
    Load environment variables from .env file.
    Searches in default locations if no path specified.
    """
    if env_path is None:
        # Check default locations
        env_locations = [
            Path(".env"),  # Current directory
            Path.home() / ".config" / "playlist-transfer" / ".env",
            Path.home() / ".playlist-transfer.env",
        ]

        for location in env_locations:
            if location.exists():
                env_path = location
                break

    if env_path and Path(env_path).exists():
        load_dotenv(env_path)
        print(f"🔐 Loaded secrets from: {env_path}")
        return True

    # Try to load from default location anyway
    load_dotenv()
    return False


def get_credential(cli_arg, env_var, config_value, credential_name):
    """
    Get credential with priority: CLI arg > env var > config file
    """
    value = cli_arg or os.getenv(env_var) or config_value

    if not value:
        return None

    # Don't log full credentials, just indicate source
    if cli_arg:
        source = "CLI argument"
    elif os.getenv(env_var):
        source = "environment variable"
    else:
        source = "config file"

    print(f"  ✓ {credential_name}: from {source}")
    return value


def expand_template(value, playlist_id=None):
    """Expand template variables in strings"""
    if not value or not isinstance(value, str):
        return value

    replacements = {
        "{date}": datetime.now().strftime("%Y%m%d"),
        "{datetime}": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "{timestamp}": str(int(datetime.now().timestamp())),
    }

    if playlist_id:
        replacements["{playlist_id}"] = playlist_id

    for key, val in replacements.items():
        value = value.replace(key, val)

    return value


def main():
    parser = argparse.ArgumentParser(
        description="Transfer playlists between music streaming platforms",
        epilog="""
Examples:
  # Use config files (searches default locations)
  playlist-transfer spotify tidal PLAYLIST_ID
  
  # Specify custom config location
  playlist-transfer spotify tidal PLAYLIST_ID --config my-config.json
  
  # Override with CLI arguments
  playlist-transfer spotify tidal PLAYLIST_ID --name "My Playlist" --detail_log_file transfer.csv
        """,
    )

    # Config file arguments
    parser.add_argument("--config", help="Path to config file (JSON)")
    parser.add_argument("--env-file", help="Path to .env file with secrets")

    # Required arguments
    parser.add_argument("source", choices=["spotify", "tidal"], help="Source platform")
    parser.add_argument(
        "destination", choices=["spotify", "tidal"], help="Destination platform"
    )
    parser.add_argument("playlist_id", help="Source playlist ID")

    # Optional arguments
    parser.add_argument("--name", help="Name for destination playlist (optional)")
    parser.add_argument(
        "--detail_log_file", help="Path to write detailed CSV log file (optional)"
    )

    # Credentials (can also be set via .env or config)
    parser.add_argument("--spotify-client-id", help="Spotify client ID")
    parser.add_argument("--spotify-client-secret", help="Spotify client secret")

    args = parser.parse_args()

    print("🎵 Playlist Transfer Tool\n")

    # Load environment variables (secrets)
    load_env_file(args.env_file)

    # Load config file (non-secret settings)
    config = load_config(args.config)

    # Get credentials with priority: CLI > env > config
    print("\n🔍 Loading credentials...")
    spotify_client_id = get_credential(
        args.spotify_client_id,
        "SPOTIFY_CLIENT_ID",
        config.get("spotify", {}).get("client_id"),
        "Spotify Client ID",
    )

    spotify_client_secret = get_credential(
        args.spotify_client_secret,
        "SPOTIFY_CLIENT_SECRET",
        config.get("spotify", {}).get("client_secret"),
        "Spotify Client Secret",
    )

    # Get other settings with priority: CLI > config
    destination_name = args.name or config.get("defaults", {}).get(
        "playlist_name_template"
    )
    detail_log_file = args.detail_log_file or config.get("defaults", {}).get(
        "detail_log_file"
    )

    # Expand templates
    if destination_name:
        destination_name = expand_template(destination_name, args.playlist_id)

    if detail_log_file:
        detail_log_file = expand_template(detail_log_file, args.playlist_id)
        # Create directory if it doesn't exist
        log_dir = Path(detail_log_file).parent
        if log_dir != Path("."):
            log_dir.mkdir(parents=True, exist_ok=True)

    # Validate source != destination
    if args.source == args.destination:
        print("\n❌ Error: Source and destination must be different platforms")
        sys.exit(1)

    # Initialize services
    print(f"\n🔧 Initializing services...")
    services = {}

    if args.source == "spotify" or args.destination == "spotify":
        if not spotify_client_id or not spotify_client_secret:
            print("\n❌ Error: Spotify credentials not found!")
            print("   Set them via:")
            print("   1. CLI: --spotify-client-id and --spotify-client-secret")
            print("   2. .env: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
            print("   3. config.json: spotify.client_id and spotify.client_secret")
            sys.exit(1)

        from playlist_transfer.services.spotify_service import SpotifyService

        services["spotify"] = SpotifyService(spotify_client_id, spotify_client_secret)
        print("  ✓ Spotify service initialized")

    if args.source == "tidal" or args.destination == "tidal":
        from playlist_transfer.services.tidal_service import TidalService

        services["tidal"] = TidalService(token_type="oauth")
        print("  ✓ Tidal service initialized")

    # Create transfer and execute
    from playlist_transfer.playlist_transfer import PlaylistTransfer

    transfer = PlaylistTransfer(services[args.source], services[args.destination])
    success = transfer.transfer(args.playlist_id, destination_name, detail_log_file)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
