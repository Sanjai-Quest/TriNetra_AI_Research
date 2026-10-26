from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml

# Base repository root (relative, machine-independent)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Standard data directories
DATA_DIR = REPO_ROOT / "data"
PUBLIC_DATA_DIR = DATA_DIR / "public"
DERIVED_DATA_DIR = DATA_DIR / "derived"
RESTRICTED_DATA_DIR = DATA_DIR / "restricted"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
RESULTS_DIR = REPO_ROOT / "results"
CONFIG_DIR = REPO_ROOT / "config"
DOCS_DIR = REPO_ROOT / "docs"

# Quality config path
DEFAULT_QUALITY_CONFIG_PATH = CONFIG_DIR / "quality.yaml"

# Load environment variables if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass


def load_quality_config(config_path: Path | str | None = None) -> Dict[str, Any]:
    """Load quality gate configuration YAML safely."""
    path = Path(config_path) if config_path else DEFAULT_QUALITY_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Quality configuration not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}
