#!/usr/bin/env python3
"""
Snake 2.0 - Setup & Launcher
Just run this file and everything installs + starts automatically!
"""

import subprocess
import sys
import os
import importlib.util

GAME_FILE = "Snake.py"
REQUIREMENTS_FILE = "requirements.txt"

def print_header():
    print("=" * 50)
    print("   Snake 2.0 - Ultimate Edition")
    print("   Setup & Launcher")
    print("=" * 50)
    print()

def check_python():
    print(f"[1/3] Python detected: {sys.version.split()[0]}")
    print()

def install_dependencies():
    print("[2/3] Checking / installing Pygame...")
    spec = importlib.util.find_spec("pygame")
    if spec is not None:
        print("   ✅ Pygame is already installed.")
        print()
        return True

    print("   ⏳ Pygame not found. Installing now...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("   ✅ Pygame installed successfully!")
    except Exception:
        print("   ⏳ Trying direct pip install...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "pygame"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("   ✅ Pygame installed successfully!")
        except Exception as e:
            print(f"   ❌ Failed to install Pygame: {e}")
            print("   Please run: pip install pygame")
            input("\nPress Enter to exit...")
            sys.exit(1)
    print()

def launch_game():
    print("[3/3] Starting the game...")
    print()
    print("=" * 50)
    print("   Have fun! Press ESC for the menu.")
    print("=" * 50)
    print()

    game_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), GAME_FILE)

    if not os.path.exists(game_path):
        print(f"❌ ERROR: '{GAME_FILE}' not found in this folder!")
        print(f"   Make sure '{GAME_FILE}' is in the same directory as this script.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    try:
        subprocess.run([sys.executable, game_path])
    except Exception as e:
        print(f"❌ Failed to start game: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    print_header()
    check_python()
    install_dependencies()
    launch_game()
