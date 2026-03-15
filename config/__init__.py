"""Configuration loader for the Para Bank UI Automation project."""
import json
import os
from pathlib import Path
from typing import Any, Dict

import pytest

# Default base URL when nothing is configured (e.g., for AWS runs)
DEFAULT_BASE_URL = "https://parabank.parasoft.com/parabank"


class Config:
    """Configuration class to load and manage environment settings."""

    def __init__(self, env: str = "dev"):
        """Initialize configuration with the specified environment.

        Args:
            env: Environment name (dev, stage, prod)
        """
        self.env = env.lower()
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from the appropriate environment file.

        Returns:
            Dict containing the configuration

        Raises:
            FileNotFoundError: If the config file doesn't exist
        """
        config_dir = Path(__file__).parent.absolute()
        config_file = config_dir / f"{self.env}.json"
        example_file = config_dir / f"{self.env}.json.example"

        if not config_file.exists():
            if example_file.exists():
                raise FileNotFoundError(
                    f"Config file {config_file} not found. "
                    f"Please copy {example_file} to {config_file} "
                    f"and update the values."
                )
            raise FileNotFoundError(
                f"Neither {config_file} nor {example_file} " f"found in {config_dir}"
            )

        with open(config_file, "r", encoding="utf-8") as f:
            config_data: Dict[str, Any] = json.load(f)
            return config_data

    def _resolve_base_url(self) -> str:
        """Resolve base_url with env override for AWS deployment.

        Priority: BASE_URL env > EXECUTION_ENV=aws + AWS_BASE_URL/PARABANK_URL > config > default.
        """
        url = os.environ.get("BASE_URL")
        if url:
            return url
        if os.environ.get("EXECUTION_ENV", "").lower() == "aws":
            url = os.environ.get("AWS_BASE_URL") or os.environ.get("PARABANK_URL")
            if url:
                return url
        return self.config.get("base_url", DEFAULT_BASE_URL)

    def __getattr__(self, name: str) -> Any:
        """Allow accessing config values as attributes."""
        if name == "base_url":
            return self._resolve_base_url()
        if name in self.config:
            return self.config[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __getitem__(self, key: str) -> Any:
        """Allow accessing config values as dictionary items."""
        return self.config[key]

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value with an optional default."""
        return self.config.get(key, default)


def pytest_addoption(parser: Any) -> None:
    """Add command line options for pytest."""
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        choices=["dev", "stage", "prod"],
        help="Environment to run tests against (dev, stage, prod)",
    )


@pytest.fixture(scope="session")
def env_config(request: Any) -> Config:
    """Pytest fixture to provide environment configuration.

    Usage:
        def test_something(env_config):
            base_url = env_config.base_url
            browser = env_config.browser
    """
    env = request.config.getoption("--env")
    return Config(env)
