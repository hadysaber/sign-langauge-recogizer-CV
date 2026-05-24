"""
Project reset utility for the Sign Language Recognition system.

Safely removes all generated artifacts (training data, models, reports)
so the project is ready for a fresh data collection and retraining cycle.

Usage:
    python src/reset_project.py
    python src/reset_project.py --yes
"""

import argparse
import logging
import shutil
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Directories whose contents will be deleted. The folders are recreated empty.
CLEANUP_TARGETS = [
    PROJECT_ROOT / "data" / "extracted",
    PROJECT_ROOT / "data" / "raw",
    PROJECT_ROOT / "models",
    PROJECT_ROOT / "reports",
]


def _get_size_str(path: Path) -> str:
    """Returns a human-readable size of a directory tree."""
    total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    if total < 1024:
        return f"{total} B"
    if total < 1024 ** 2:
        return f"{total / 1024:.1f} KB"
    return f"{total / 1024 ** 2:.1f} MB"


def _count_files(path: Path) -> int:
    """Counts all files recursively inside a directory."""
    return sum(1 for f in path.rglob('*') if f.is_file())


def preview() -> bool:
    """Shows what will be deleted and returns True if there is anything to clean."""
    has_content = False

    logger.info("=" * 55)
    logger.info("  Project Reset - Preview")
    logger.info("=" * 55)

    for target in CLEANUP_TARGETS:
        relative = target.relative_to(PROJECT_ROOT)
        if target.exists() and any(target.iterdir()):
            files = _count_files(target)
            size = _get_size_str(target)
            logger.info(f"  DELETE  {relative}/  ({files} files, {size})")
            has_content = True
        else:
            logger.info(f"  OK      {relative}/  (already empty)")

    logger.info("-" * 55)
    return has_content


def reset() -> None:
    """Deletes all generated artifacts and recreates empty directories."""
    for target in CLEANUP_TARGETS:
        if target.exists():
            shutil.rmtree(target)
            logger.info(f"  Deleted: {target.relative_to(PROJECT_ROOT)}/")

    required_dirs = [
        PROJECT_ROOT / "data" / "raw",
        PROJECT_ROOT / "data" / "extracted",
        PROJECT_ROOT / "models",
        PROJECT_ROOT / "models" / "Logs",
        PROJECT_ROOT / "reports",
        PROJECT_ROOT / "reports" / "plots",
        PROJECT_ROOT / "reports" / "metrics",
    ]
    for directory in required_dirs:
        directory.mkdir(parents=True, exist_ok=True)

    logger.info("-" * 55)
    logger.info("Reset complete. Project is ready for fresh data collection.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove generated data, models, and reports."
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the confirmation prompt and reset immediately."
    )
    args = parser.parse_args()

    has_content = preview()

    if not has_content:
        logger.info("Nothing to clean - project is already in a fresh state.")
        return

    if args.yes:
        logger.info("")
        reset()
        return

    try:
        answer = input("\nDelete all listed artifacts? (yes/no): ").strip().lower()
    except EOFError:
        logger.info("Reset cancelled because no confirmation was provided.")
        return

    if answer in ("yes", "y"):
        logger.info("")
        reset()
    else:
        logger.info("Reset cancelled. No files were deleted.")


if __name__ == '__main__':
    main()
