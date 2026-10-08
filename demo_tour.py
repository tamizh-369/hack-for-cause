"""Demo Tour Runner — Public Health Claim Watchdog.

Launches the automated interactive tour in the browser for screen recording.
The tour explains each UI element with an animated glassmorphic dialogue box,
spotlights elements, types into input fields character-by-character,
clicks buttons, toggles datasets, and switches tabs automatically.

Usage:
    python demo_tour.py
"""

import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import webbrowser

BASE_DIR = Path(__file__).resolve().parent
STREAMLIT_URL = "http://localhost:8501/?tour=true"

# Common browser executable locations on Windows
BROWSER_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
]


def is_streamlit_running(url="http://localhost:8501") -> bool:
    """Check if the Streamlit app is responding."""
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            return resp.status in (200, 304)
    except Exception:
        return False


def start_streamlit_if_needed():
    """Ensure Streamlit is running before launching the browser."""
    if is_streamlit_running():
        print("  [+] Streamlit server is already running on http://localhost:8501")
        return None

    print("  [*] Starting Streamlit server in background...")
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(BASE_DIR / "src" / "app.py"),
            "--server.headless",
            "true",
            "--server.port",
            "8501",
        ],
        cwd=str(BASE_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for server to bind
    for _ in range(25):
        time.sleep(0.5)
        if is_streamlit_running():
            print("  [+] Streamlit server started successfully!")
            return proc

    print("  [!] Server took longer than expected, opening browser anyway...")
    return proc


def find_browser():
    """Find the best browser executable on the current system."""
    for path in BROWSER_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def print_banner():
    """Display an attractive terminal guide for recording."""
    print("=" * 72)
    print("  🛡️  PUBLIC HEALTH CLAIM WATCHDOG — AUTOMATED DEMO TOUR")
    print("=" * 72)
    print("  This script launches an autonomous interactive guide in your browser.")
    print("  It will:")
    print("    • Display floating glassmorphic dialogue boxes with typewriter narration")
    print("    • Spotlight and scroll smoothly to every critical element")
    print("    • Toggle releases (Release 1 -> Release 2) to demonstrate revision drift")
    print("    • Sign off on the reviewer console and log to the session audit trail")
    print("    • Switch through tabs (Verify -> Compare -> Parser -> Data -> Audit)")
    print("    • Type sample claims character-by-character into the input box on its own")
    print("=" * 72)
    print("  🎬 SCREEN RECORDING INSTRUCTIONS:")
    print("    • Windows shortcut to record screen: [Win + Alt + R] (Xbox Game Bar)")
    print("    • Or open OBS Studio / Loom / Clipchamp / Snagit")
    print("    • You can Pause [⏸️], Resume [▶️], or Skip [⏭️] anytime via the on-screen HUD")
    print("=" * 72)


def main():
    print_banner()

    # Step 1: Ensure Streamlit is running
    server_proc = start_streamlit_if_needed()

    # Step 2: Launch browser in maximized window
    browser_exe = find_browser()
    print(f"\n  [*] Opening automated tour at: {STREAMLIT_URL}")

    if browser_exe:
        print(f"  [*] Launching browser: {browser_exe}")
        try:
            subprocess.Popen([
                browser_exe,
                "--start-maximized",
                STREAMLIT_URL,
            ])
        except Exception as e:
            print(f"  [!] Direct launch failed ({e}), falling back to default browser...")
            webbrowser.open(STREAMLIT_URL)
    else:
        webbrowser.open(STREAMLIT_URL)

    print("\n  [✓] Browser launched! Ready to record your video.")
    print("  Press Ctrl+C in this terminal when finished to exit.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  [*] Tour session ended. Goodbye!")


if __name__ == "__main__":
    main()
