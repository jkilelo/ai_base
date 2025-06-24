#!/usr/bin/env python3
"""
AI Base Project v1 - Development Server Startup Script
Starts the FastAPI backend using UV for Python and package management
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path


def run_command(cmd, capture_output=True, check=True, timeout=30):
    """Run a command and return the result."""
    try:
        if isinstance(cmd, str):
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                check=check,
            )
        else:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                check=check,
            )
        return result
    except subprocess.CalledProcessError as e:
        if not check:
            return e
        raise
    except subprocess.TimeoutExpired:
        print(f"⚠️  Command timed out: {cmd}")
        return None


def check_uv_installed():
    """Check if UV is installed."""
    try:
        result = run_command("uv --version", check=False)
        if result.returncode == 0:
            print(f"✅ UV is installed: {result.stdout.strip()}")
            return True
        return False
    except:
        return False


def find_python():
    """Find available Python installations."""
    python_options = []

    # Check for Python 3.12+ first (preferred)
    for version in ["3.12", "3.13", "3.14", "3.15"]:
        try:
            result = run_command(f"py -{version} --version", check=False)
            if result.returncode == 0:
                version_info = result.stdout.strip()
                python_options.append((f"py -{version}", version_info, True))
                print(f"✅ Found {version_info} via Python Launcher")
        except:
            continue

    # Check default python
    try:
        result = run_command("python --version", check=False)
        if result.returncode == 0:
            version_info = result.stdout.strip()
            # Extract version numbers
            if "Python 3." in version_info:
                version_parts = version_info.replace("Python ", "").split(".")
                if len(version_parts) >= 2:
                    major, minor = int(version_parts[0]), int(version_parts[1])
                    is_312_plus = major > 3 or (major == 3 and minor >= 12)
                    python_options.append(("python", version_info, is_312_plus))
                    status = "✅" if is_312_plus else "⚠️ "
                    print(f"{status} Found {version_info} as default python")
    except:
        pass

    # Check py -3 (any Python 3.x)
    try:
        result = run_command("py -3 --version", check=False)
        if result.returncode == 0:
            version_info = result.stdout.strip()
            if "Python 3." in version_info:
                version_parts = version_info.replace("Python ", "").split(".")
                if len(version_parts) >= 2:
                    major, minor = int(version_parts[0]), int(version_parts[1])
                    is_312_plus = major > 3 or (major == 3 and minor >= 12)
                    # Only add if not already found
                    if not any(opt[1] == version_info for opt in python_options):
                        python_options.append(("py -3", version_info, is_312_plus))
                        status = "✅" if is_312_plus else "⚠️ "
                        print(f"{status} Found {version_info} via Python Launcher")
    except:
        pass

    return python_options


def install_uv(python_cmd):
    """Install UV using the specified Python command."""
    print(f"🔧 Installing UV using {python_cmd}...")

    try:
        result = run_command(f"{python_cmd} -m pip install uv")
        print("✅ UV installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install UV: {e}")
        return False


def install_python_with_uv(version="3.12"):
    """Install Python using UV."""
    print(f"🔧 Installing Python {version} using UV...")

    try:
        result = run_command(f"uv python install {version}")
        print(f"✅ Python {version} installed via UV")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python {version} with UV: {e}")
        return False


def setup_virtual_environment():
    """Set up virtual environment using UV."""
    venv_path = Path(".venv")

    if venv_path.exists():
        print("🔍 Found existing UV virtual environment, checking Python version...")

        # Check Python version in existing .venv
        venv_python = venv_path / "Scripts" / "python.exe"
        if venv_python.exists():
            try:
                result = run_command(
                    f'"{venv_python}" -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)"',
                    check=False,
                )
                if result.returncode == 0:
                    # Get version info
                    version_result = run_command(f'"{venv_python}" --version')
                    print(
                        f"✅ Existing .venv has compatible Python: {version_result.stdout.strip()}"
                    )
                    return True
                else:
                    print("⚠️  Existing .venv does not have Python 3.12+")
                    print("🔄 Removing incompatible virtual environment...")
                    shutil.rmtree(venv_path)
                    print("✅ Old virtual environment removed")
            except Exception as e:
                print(f"⚠️  Error checking .venv: {e}, removing...")
                shutil.rmtree(venv_path)
                print("✅ Invalid virtual environment removed")
        else:
            print("⚠️  Invalid .venv directory found, removing...")
            shutil.rmtree(venv_path)
            print("✅ Invalid .venv directory removed")

    # Create new virtual environment with UV
    print("🔧 Creating virtual environment with UV (Python 3.12+)...")
    try:
        result = run_command("uv venv --python 3.12")
        print("✅ Virtual environment created with UV")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment with UV: {e}")
        return False


def install_dependencies():
    """Install dependencies using UV."""
    print("🔧 Installing dependencies with UV...")

    try:
        result = run_command("uv pip install -r requirements.txt")
        print("✅ Dependencies installed with UV")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies with UV: {e}")
        return False


def create_database_directory():
    """Create database directory if it doesn't exist."""
    db_dir = Path("../../databases")
    if not db_dir.exists():
        db_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created database directory: {db_dir.absolute()}")
    else:
        print(f"✅ Database directory exists: {db_dir.absolute()}")


def start_server():
    """Start the FastAPI development server."""
    print("\n🚀 Starting FastAPI development server...")
    print("   Backend API: http://127.0.0.1:8000")
    print("   API Docs: http://127.0.0.1:8000/docs")
    print("   Health Check: http://127.0.0.1:8000/api/v1/health")
    print("   Detailed Health: http://127.0.0.1:8000/api/v1/health/detailed")
    print("\n   Press Ctrl+C to stop the server")
    print("-" * 60)

    # Try different ports if needed
    ports = [8000, 8001, 8002]

    for port in ports:
        try:
            print(f"[INFO] Attempting to start server on port {port}...")
            subprocess.run(
                [
                    "python",
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--reload",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                ],
                check=True,
            )
            return True
        except KeyboardInterrupt:
            print(f"\n\n🛑 Server stopped by user")
            return True
        except subprocess.CalledProcessError:
            if port == ports[-1]:  # Last port
                print(f"\n❌ Could not start server on ports {ports[0]}-{ports[-1]}")
                print("Please check if another service is using these ports")
                return False
            else:
                print(f"[WARNING] Port {port} is busy, trying next port...")
                continue
        except FileNotFoundError:
            print(
                "\n❌ Uvicorn not found. Dependencies may not be installed correctly."
            )
            return False


def main():
    """Main startup script."""
    print("=" * 60)
    print("   AI Base Project v1 - FastAPI Backend")
    print("=" * 60)

    # Change to backend directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Check if UV is installed
    if not check_uv_installed():
        print("⚠️  UV not found, setting up UV...")

        # Find available Python
        python_options = find_python()

        if not python_options:
            print("❌ No Python 3.x installation found!")
            print("\nPython Installation Required:")
            print("   1. Download Python 3.12+ from: https://www.python.org/downloads/")
            print("   2. Install with 'Add Python to PATH' checked")
            print("   3. Restart your terminal/command prompt")
            print("   4. Try running this script again")
            sys.exit(1)

        # Use the first Python 3.12+ if available, otherwise use any Python 3.x
        python_312_plus = [opt for opt in python_options if opt[2]]
        if python_312_plus:
            python_cmd = python_312_plus[0][0]
            print(f"✅ Using {python_312_plus[0][1]} to install UV")
            need_python_install = False
        else:
            python_cmd = python_options[0][0]
            print(f"⚠️  Using {python_options[0][1]} to install UV")
            print("   Will install Python 3.12+ via UV afterwards")
            need_python_install = True

        # Install UV
        if not install_uv(python_cmd):
            sys.exit(1)

        # Install Python 3.12+ if needed
        if need_python_install:
            if not install_python_with_uv("3.12"):
                sys.exit(1)

    # Set up virtual environment
    if not setup_virtual_environment():
        sys.exit(1)

    # Create database directory
    create_database_directory()

    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed")
        sys.exit(1)

    # Start server
    print("\n" + "=" * 60)
    print("   Ready to start FastAPI server")
    print("=" * 60)

    if start_server():
        print("\n✅ Server startup completed")
    else:
        print("\n❌ Server startup failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
