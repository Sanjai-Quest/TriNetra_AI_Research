from __future__ import annotations

import ast
from pathlib import Path
import pytest
from trinetra_link.config import REPO_ROOT


def get_core_method_python_files() -> list[Path]:
    core_dirs = [
        REPO_ROOT / "trinetra_link" / "quality",
        REPO_ROOT / "trinetra_link" / "reconcile",
        REPO_ROOT / "trinetra_link" / "attribution",
    ]
    py_files: list[Path] = []
    for d in core_dirs:
        py_files.extend(list(d.glob("*.py")))
    return py_files


def test_import_boundary_no_leakage_from_eval_or_staging():
    """
    Non-negotiable Rule 3:
    quality/, reconcile/ and attribution/ must not import from eval/ or staging/,
    or open data/restricted/.
    """
    py_files = get_core_method_python_files()
    assert len(py_files) >= 6, "Expected at least 6 core method python files to inspect"

    forbidden_modules = {"eval", "staging", "trinetra_link.eval", "trinetra_link.staging"}

    for fpath in py_files:
        with open(fpath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(fpath))

        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for forbidden in forbidden_modules:
                        assert not alias.name.startswith(forbidden), (
                            f"LEAKAGE VIOLATION in {fpath.name}: imports forbidden '{alias.name}'"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for forbidden in forbidden_modules:
                        assert not node.module.startswith(forbidden), (
                            f"LEAKAGE VIOLATION in {fpath.name}: imports from forbidden '{node.module}'"
                        )

            # Check string literals for data/restricted references
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value.lower()
                assert "data/restricted" not in val, (
                    f"LEAKAGE VIOLATION in {fpath.name}: references forbidden 'data/restricted'"
                )
