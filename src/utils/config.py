"""
Configuration loader and shared utilities.
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config(config_path: str = None) -> dict:
    """Load the project configuration from config.yaml."""
    if config_path is None:
        config_path = PROJECT_ROOT / "config.yaml"
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    return config


def load_env():
    """Load environment variables from .env file."""
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("Loaded environment variables from .env")
    else:
        logger.warning(
            "No .env file found. Copy .env.example to .env and add your API keys."
        )


def get_api_key(name: str) -> str:
    """Get an API key from environment variables."""
    load_env()
    key = os.getenv(name)
    if not key or key.startswith("your_"):
        logger.warning(f"API key '{name}' not configured. Check your .env file.")
        return None
    return key


def setup_logging(config: dict = None):
    """Configure loguru logging based on config."""
    if config is None:
        config = load_config()
    
    log_config = config.get("logging", {})
    level = log_config.get("level", "INFO")
    log_file = log_config.get("file")
    
    # Remove default handler
    logger.remove()
    
    # Console handler
    logger.add(
        lambda msg: print(msg, end=""),
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    )
    
    # File handler
    if log_file:
        log_path = PROJECT_ROOT / log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_path),
            level=level,
            rotation="10 MB",
            retention="1 month",
        )
    
    return logger


def get_data_path(subdir: str = "raw") -> Path:
    """Get the path to a data subdirectory."""
    path = PROJECT_ROOT / "data" / subdir
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_output_path(subdir: str = "figures") -> Path:
    """Get the path to an output subdirectory."""
    path = PROJECT_ROOT / "output" / subdir
    path.mkdir(parents=True, exist_ok=True)
    return path
