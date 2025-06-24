#!/usr/bin/env python3
"""
Python Environment Checker and Cleaner
Checks for Python 3.12+ and removes old environments
"""

import sys
import subprocess
import shutil
import os
from pathlib import Path


def check_python_version(python_cmd="python"):
    """Check if the Python version is 3.12+"""
    try:
        result = subprocess.run(
            [python_cmd, "--version"], capture_output=True, text=True, check=True
        )
        version_str = result.stdout.strip()

        # Parse version
        if "Python" in version_str:
            version_part = version_str.split()[1]
            major, minor, patch = map(int, version_part.split("."))

            if major == 3 and minor >= 12:
                return True, version_str
            else:
                return False, version_str

        return False, version_str

    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return False, "Not found"


def find_valid_python():
    """Find a valid Python 3.12+ installation"""
    python_commands = ["python3.12", "python3.13", "python3.14", "python", "py"]

    for cmd in python_commands:
        is_valid, version = check_python_version(cmd)
        if is_valid:
            return cmd, version

    return None, None


def remove_old_venv():
    """Remove old virtual environment if it exists and uses old Python"""
    venv_path = Path(".venv")

    if not venv_path.exists():
        print("No existing virtual environment found")
        return True

    # Check Python version in existing venv
    if sys.platform == "win32":
        venv_python = venv_path / "Scripts" / "python.exe"
    else:
        venv_python = venv_path / "bin" / "python"

    if venv_python.exists():
        is_valid, version = check_python_version(str(venv_python))
        if is_valid:
            print(f"✓ Existing virtual environment uses {version}, keeping it")
            return False  # Don't need to recreate
        else:
            print(
                f"⚠ Existing virtual environment uses {version} (< 3.12), removing it"
            )
    else:
        print("⚠ Existing virtual environment is broken, removing it")

    # Remove the old environment
    try:
        shutil.rmtree(venv_path)
        print("✓ Old virtual environment removed")
        return True
    except Exception as e:
        print(f"✗ Failed to remove old virtual environment: {e}")
        return False


def main():
    """Main function"""
    print("=" * 50)
    print("AI Base Platform - Python Environment Checker")
    print("=" * 50)

    # Check for valid Python
    python_cmd, version = find_valid_python()

    if python_cmd is None:
        print("✗ Python 3.12+ not found!")
        print("\nPlease install Python 3.12+ from https://python.org")
        print("Make sure to add Python to your PATH during installation")
        sys.exit(1)

    print(f"✓ Found valid Python: {version}")

    # Check and remove old virtual environment
    need_new_venv = remove_old_venv()

    if need_new_venv:
        print(f"\nRecommendation: Create new virtual environment with:")
        print(f"  uv venv .venv --python {python_cmd}")

    print(f"\nPython command to use: {python_cmd}")
    print("✓ Environment check completed")


if __name__ == "__main__":
    main()
