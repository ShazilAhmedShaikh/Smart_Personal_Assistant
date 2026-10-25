"""
J.A.R.V.I.S. Automated Backup & Archival Engine
Creates high-speed compressed backups of Shazil's Obsidian Vault and Projects,
manages archive rotation, and runs an asynchronous background backup schedule.
"""

import os
import time
import zipfile
import asyncio
from pathlib import Path
from typing import Dict, Any, List

from config import DEFAULT_PROJECTS_DIR, DEFAULT_VAULT_DIR

BACKUPS_DIR = Path(r"C:\Shazil\backups")
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

# Directories to ignore during project backups to prevent bloat
EXCLUDE_DIRS = {
    "node_modules", ".git", "__pycache__", ".pytest_cache",
    "cache_audio", ".venv", "venv", "dist", "build"
}


def create_backup(target_key: str = "vault") -> Dict[str, Any]:
    """
    Creates a timestamped zip archive of target ('vault' or 'projects').
    Automatically excludes cache and build files to optimize speed and size.
    """
    t_start = time.time()
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    target_str = target_key.lower().strip()

    if "vault" in target_str or "obsidian" in target_str:
        source_dir = Path(DEFAULT_VAULT_DIR)
        archive_name = f"vault_backup_{timestamp}.zip"
    else:
        source_dir = Path(DEFAULT_PROJECTS_DIR)
        archive_name = f"projects_backup_{timestamp}.zip"

    if not source_dir.exists():
        return {
            "success": False,
            "error": f"Source directory '{source_dir}' does not exist on this machine."
        }

    archive_path = BACKUPS_DIR / archive_name
    files_count = 0

    try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for root, dirs, files in os.walk(source_dir):
                # Filter out excluded directories in-place
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                for file in files:
                    file_path = Path(root) / file
                    # Skip temporary files
                    if file.endswith((".pyc", ".tmp", ".log")):
                        continue
                    try:
                        arcname = file_path.relative_to(source_dir)
                        zipf.write(file_path, arcname=arcname)
                        files_count += 1
                    except Exception:
                        continue

        duration = round(time.time() - t_start, 2)
        size_mb = round(archive_path.stat().st_size / (1024 * 1024), 2)

        # Archive rotation: keep only latest 10 archives per target
        rotate_backups(prefix=archive_name.split("_")[0], keep_count=10)

        return {
            "success": True,
            "target": target_key,
            "archive_name": archive_name,
            "archive_path": str(archive_path),
            "files_count": files_count,
            "size_mb": size_mb,
            "duration_seconds": duration,
            "message": f"{target_key.title()} backup complete! {files_count} files archived ({size_mb} MB) in {duration}s."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed creating backup: {str(e)}"
        }


def rotate_backups(prefix: str, keep_count: int = 10):
    """Deletes older backups if count exceeds keep_count."""
    try:
        archives = sorted(
            [f for f in BACKUPS_DIR.glob(f"{prefix}_backup_*.zip")],
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        if len(archives) > keep_count:
            for old_archive in archives[keep_count:]:
                try:
                    old_archive.unlink()
                except Exception:
                    pass
    except Exception:
        pass


def list_backups() -> List[Dict[str, Any]]:
    """Returns a list of all existing backup archives with metadata."""
    results = []
    for archive in sorted(BACKUPS_DIR.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True):
        results.append({
            "name": archive.name,
            "size_mb": round(archive.stat().st_size / (1024 * 1024), 2),
            "created": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(archive.stat().st_mtime))
        })
    return results


async def run_backup_scheduler_loop(interval_hours: int = 12):
    """
    Background worker loop that triggers automated Vault backups periodically.
    """
    while True:
        try:
            await asyncio.sleep(interval_hours * 3600)
            res = create_backup("vault")
            print(f"[AUTO-BACKUP] Scheduled Vault backup created: {res.get('archive_name')}")
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[AUTO-BACKUP ERROR] {e}")
            await asyncio.sleep(60)
