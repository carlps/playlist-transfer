"""
Tests for CLI main.py functionality
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from playlist_transfer.main import (
    load_config,
    load_env_file,
    get_credential,
    expand_template,
)


class TestConfigLoading:
    """Test configuration file loading"""

    def test_load_config_from_specified_path(self):
        """Test loading config from a specified path"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            config_data = {"spotify": {"client_id": "test_id"}}
            json.dump(config_data, tmp)
            tmp.flush()
            config_path = tmp.name

        try:
            config = load_config(config_path)
            assert config == config_data
        finally:
            Path(config_path).unlink()

    def test_load_config_from_current_directory(self):
        """Test loading config.json from current directory"""
        # Create a temporary config in current directory
        config_path = Path("config.json")
        original_exists = config_path.exists()
        original_content = None

        if original_exists:
            # Backup original
            with open(config_path) as f:
                original_content = f.read()

        try:
            # Write test config
            test_config = {"test": "data"}
            with open(config_path, "w") as f:
                json.dump(test_config, f)

            config = load_config()
            assert config == test_config

        finally:
            # Restore or remove
            if original_exists and original_content:
                with open(config_path, "w") as f:
                    f.write(original_content)
            elif config_path.exists():
                config_path.unlink()

    def test_load_config_invalid_json(self, capsys):
        """Test handling of invalid JSON in config file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp.write("{invalid json")
            tmp.flush()
            config_path = tmp.name

        try:
            config = load_config(config_path)
            assert config == {}
            captured = capsys.readouterr()
            assert "Invalid JSON" in captured.out
        finally:
            Path(config_path).unlink()

    def test_load_config_nonexistent_file(self):
        """Test loading config when file doesn't exist"""
        config = load_config("/nonexistent/path/config.json")
        assert config == {}


class TestEnvFileLoading:
    """Test environment file loading"""

    def test_load_env_from_current_directory(self):
        """Test loading .env from current directory"""
        env_path = Path(".env")
        original_exists = env_path.exists()
        original_content = None

        if original_exists:
            with open(env_path) as f:
                original_content = f.read()

        try:
            with open(env_path, "w") as f:
                f.write("TEST_VAR=test_value\n")

            result = load_env_file()
            # We can't easily test if the env var was loaded in this context,
            # but we can verify the function returned True
            assert result is True

        finally:
            if original_exists and original_content:
                with open(env_path, "w") as f:
                    f.write(original_content)
            elif env_path.exists():
                env_path.unlink()

    def test_load_env_nonexistent_file(self):
        """Test loading env file when it doesn't exist"""
        result = load_env_file("/nonexistent/path/.env")
        # Should return False but not crash
        assert result is False


class TestCredentialRetrieval:
    """Test credential priority and retrieval"""

    def test_credential_from_cli_arg(self, capsys):
        """Test that CLI argument has highest priority"""
        result = get_credential(
            cli_arg="cli_value",
            env_var="ENV_VAR",
            config_value="config_value",
            credential_name="Test Credential",
        )

        assert result == "cli_value"
        captured = capsys.readouterr()
        assert "CLI argument" in captured.out

    def test_credential_from_env_var(self, capsys, monkeypatch):
        """Test that env var is used when CLI arg not provided"""
        monkeypatch.setenv("TEST_ENV_VAR", "env_value")

        result = get_credential(
            cli_arg=None,
            env_var="TEST_ENV_VAR",
            config_value="config_value",
            credential_name="Test Credential",
        )

        assert result == "env_value"
        captured = capsys.readouterr()
        assert "environment variable" in captured.out

    def test_credential_from_config(self, capsys):
        """Test that config value is used as last resort"""
        result = get_credential(
            cli_arg=None,
            env_var="NONEXISTENT_VAR",
            config_value="config_value",
            credential_name="Test Credential",
        )

        assert result == "config_value"
        captured = capsys.readouterr()
        assert "config file" in captured.out

    def test_credential_not_found(self):
        """Test when no credential is provided"""
        result = get_credential(
            cli_arg=None,
            env_var="NONEXISTENT_VAR",
            config_value=None,
            credential_name="Test Credential",
        )

        assert result is None


class TestTemplateExpansion:
    """Test template variable expansion"""

    def test_expand_date_template(self):
        """Test {date} template expansion"""
        result = expand_template("playlist_{date}")
        # Should be in format playlist_YYYYMMDD
        assert result.startswith("playlist_")
        assert len(result) == len("playlist_20231231")

    def test_expand_datetime_template(self):
        """Test {datetime} template expansion"""
        result = expand_template("playlist_{datetime}")
        # Should be in format playlist_YYYYMMDD_HHMMSS
        assert result.startswith("playlist_")
        assert "_" in result

    def test_expand_timestamp_template(self):
        """Test {timestamp} template expansion"""
        result = expand_template("playlist_{timestamp}")
        # Should be in format playlist_<unix_timestamp>
        assert result.startswith("playlist_")
        # The timestamp part should be numeric
        timestamp_part = result.split("_")[1]
        assert timestamp_part.isdigit()

    def test_expand_playlist_id_template(self):
        """Test {playlist_id} template expansion"""
        result = expand_template("backup_{playlist_id}", playlist_id="abc123")
        assert result == "backup_abc123"

    def test_expand_multiple_templates(self):
        """Test multiple template variables in one string"""
        result = expand_template("{playlist_id}_{date}", playlist_id="test_id")
        assert result.startswith("test_id_")
        assert len(result) > len("test_id_")

    def test_expand_no_templates(self):
        """Test string with no templates"""
        result = expand_template("plain_string")
        assert result == "plain_string"

    def test_expand_none_value(self):
        """Test expansion with None value"""
        result = expand_template(None)
        assert result is None

    def test_expand_non_string_value(self):
        """Test expansion with non-string value"""
        result = expand_template(123)
        assert result == 123
