"""Configuration loader for the Para Bank UI Automation project."""
import json
from pathlib import Path
from typing import Any, Dict

import pytest


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

    def __getattr__(self, name: str) -> Any:
        """Allow accessing config values as attributes."""
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
