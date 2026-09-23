"""
Buddy Agent — App Control
Handles: open/close/switch applications, build app index, fuzzy match.
"""

import os
import subprocess
import time
import threading
import winreg

# ── Critical process safety blacklist ───────────────────────
CRITICAL_PROCESS_BLACKLIST = {
    "system", "smss", "csrss", "wininit", "winlogon", "services", "lsass",
    "svchost", "explorer", "dwm", "taskmgr", "fontdrvhost",
    "sihost", "ctfmon", "rundll32", "dllhost", "conhost",
}

# ── Hardcoded special apps ──────────────────────────────────
SPECIAL_APPS = {
    "file explorer": ("explorer.exe", "File Explorer"),
    "explorer": ("explorer.exe", "File Explorer"),
    "files": ("explorer.exe", "File Explorer"),
    "this pc": ("explorer.exe", "File Explorer"),
    "settings": ("ms-settings:", "Settings"),
    "windows settings": ("ms-settings:", "Settings"),
    "control panel": ("control.exe", "Control Panel"),
    "command prompt": ("cmd.exe", "Command Prompt"),
    "cmd": ("cmd.exe", "Command Prompt"),
    "powershell": ("powershell.exe", "PowerShell"),
    "terminal": ("wt.exe", "Windows Terminal"),
    "windows terminal": ("wt.exe", "Windows Terminal"),
    "calculator": ("calc.exe", "Calculator"),
    "calc": ("calc.exe", "Calculator"),
    "notepad": ("notepad.exe", "Notepad"),
    "paint": ("mspaint.exe", "Paint"),
    "task manager": ("taskmgr.exe", "Task Manager"),
    "spotify": ("spotify.exe", "Spotify"),
    "chrome": ("chrome.exe", "Google Chrome"),
    "google chrome": ("chrome.exe", "Google Chrome"),
    "firefox": ("firefox.exe", "Mozilla Firefox"),
    "edge": ("msedge.exe", "Microsoft Edge"),
    "microsoft edge": ("msedge.exe", "Microsoft Edge"),
    "whatsapp": ("whatsapp.exe", "WhatsApp"),
    "telegram": ("telegram.exe", "Telegram"),
    "discord": ("discord.exe", "Discord"),
    "steam": ("steam.exe", "Steam"),
    "epic games": ("epicgameslauncher.exe", "Epic Games"),
    "vs code": ("code.exe", "VS Code"),
    "vscode": ("code.exe", "VS Code"),
    "visual studio code": ("code.exe", "VS Code"),
    "word": ("winword.exe", "Microsoft Word"),
    "excel": ("excel.exe", "Microsoft Excel"),
    "powerpoint": ("powerpnt.exe", "Microsoft PowerPoint"),
    "outlook": ("outlook.exe", "Microsoft Outlook"),
    "teams": ("ms-teams.exe", "Microsoft Teams"),
    "zoom": ("zoom.exe", "Zoom"),
    "slack": ("slack.exe", "Slack"),
    "obs": ("obs64.exe", "OBS Studio"),
    "vlc": ("vlc.exe", "VLC"),
    "media player": ("wmplayer.exe", "Windows Media Player"),
    "snipping tool": ("snippingtool.exe", "Snipping Tool"),
}

# ── Website shortcuts (open in browser) ─────────────────────
WEBSITE_SHORTCUTS = {
    "netflix": "https://netflix.com",
    "youtube": "https://youtube.com",
    "gmail": "https://mail.google.com",
    "google mail": "https://mail.google.com",
    "email": "https://mail.google.com",
    "mail": "https://mail.google.com",
    "facebook": "https://facebook.com",
    "instagram": "https://instagram.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "reddit": "https://reddit.com",
    "linkedin": "https://linkedin.com",
    "github": "https://github.com",
    "google drive": "https://drive.google.com",
    "drive": "https://drive.google.com",
    "google maps": "https://maps.google.com",
    "maps": "https://maps.google.com",
    "google translate": "https://translate.google.com",
    "translate": "https://translate.google.com",
    "wikipedia": "https://wikipedia.org",
    "amazon": "https://amazon.in",
    "flipkart": "https://flipkart.com",
    "whatsapp web": "https://web.whatsapp.com",
    "telegram web": "https://web.telegram.org",
    "stack overflow": "https://stackoverflow.com",
    "chat gpt": "https://chat.openai.com",
    "chatgpt": "https://chat.openai.com",
    "google": "https://google.com",
}


class AppController:
    """Manages app indexing, finding, opening, and closing."""

    def __init__(self):
        self.apps = {}
        self.index_building = False
        self.index_built = False
        self._build_index_async()

    def _build_index_async(self):
        """Build app index in a background thread."""
        if self.index_building:
            return
        self.index_building = True
        thread = threading.Thread(target=self._build_index, daemon=True)
        thread.start()

    def _build_index(self):
        """Build searchable app index — registry, Start Menu shortcuts, filesystem."""
        start_time = time.time()
        print("[INDEX] Building app index...")
        idx = {}

        # 1. Add special apps
        for name, (path, display) in SPECIAL_APPS.items():
            idx[name.lower()] = (path, display or name)

        # 2. Registry App Paths
        for reg in [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths",
        ]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            sub = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, sub) as sk:
                                try:
                                    val, _ = winreg.QueryValueEx(sk, "")
                                    if val and os.path.exists(val):
                                        name = os.path.splitext(
                                            os.path.basename(sub)
                                        )[0].lower()
                                        if name not in idx:
                                            idx[name] = (val, name)
                                except FileNotFoundError:
                                    pass
                        except OSError:
                            continue
            except Exception:
                pass

        # 3. Start Menu shortcuts (.lnk files) — better app discovery
        start_menu_dirs = [
            os.path.join(os.environ.get("APPDATA", ""),
                         r"Microsoft\Windows\Start Menu\Programs"),
            os.path.join(os.environ.get("PROGRAMDATA", ""),
                         r"Microsoft\Windows\Start Menu\Programs"),
        ]
        for sm_dir in start_menu_dirs:
            if not os.path.isdir(sm_dir):
                continue
            for root, dirs, files in os.walk(sm_dir):
                for f in files:
                    if f.lower().endswith(".lnk"):
                        name = os.path.splitext(f)[0].lower()
                        full = os.path.join(root, f)
                        if name not in idx:
                            idx[name] = (full, os.path.splitext(f)[0])

        # 4. Quick filesystem scan — key locations only, limited depth
        roots = [
            (os.environ.get("PROGRAMFILES", ""), 2),
            (os.environ.get("PROGRAMFILES(X86)", ""), 2),
            (os.environ.get("LOCALAPPDATA", ""), 2),
            (os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"), 2),
        ]
        for root, max_depth in roots:
            if not root or not os.path.exists(root):
                continue
            for dp, dn, fn in os.walk(root):
                depth = dp.count(os.sep) - root.count(os.sep)
                if depth > max_depth:
                    dn.clear()
                    continue
                for f in fn:
                    if not f.lower().endswith(".exe"):
                        continue
                    name = os.path.splitext(f)[0].lower()
                    full = os.path.join(dp, f)
                    if name not in idx or len(full) < len(idx[name][0]):
                        idx[name] = (full, os.path.splitext(f)[0])

        self.apps = idx
        self.index_built = True
        self.index_building = False
        elapsed = time.time() - start_time
        print(f"[INDEX] Done: {len(idx)} apps in {elapsed:.1f}s")

    def _is_critical(self, name):
        """Check if a process name is in the critical blacklist."""
        base = os.path.splitext(name)[0].lower().strip()
        return base in CRITICAL_PROCESS_BLACKLIST

    def find_app(self, query):
        """Find an app by fuzzy match. Returns (path, display_name) or (None, None)."""
        q = query.lower().strip()

        # Safety: reject critical process names
        if q in CRITICAL_PROCESS_BLACKLIST:
            return None, None

        # Wait briefly for index if not ready
        wait_start = time.time()
        while not self.index_built and time.time() - wait_start < 3.0:
            time.sleep(0.1)

        search_dict = self.apps if self.index_built else SPECIAL_APPS

        # Exact match
        if q in search_dict:
            return search_dict[q]

        # Substring match
        for name, (path, disp) in search_dict.items():
            if self._is_critical(name):
                continue
            if q in name or name in q:
                return path, disp

        # Word-based fuzzy
        qw = q.replace("-", " ").replace("_", " ").split()
        for name, (path, disp) in search_dict.items():
            if self._is_critical(name):
                continue
            nw = name.replace("-", " ").replace("_", " ").split()
            if all(any(qp in nw_part for nw_part in nw) for qp in qw):
                return path, disp

        # PATH fallback
        for variant in [f"{q}.exe", f"{q.replace(' ', '-')}.exe",
                        f"{q.replace(' ', '')}.exe"]:
            try:
                r = subprocess.run(["where", variant],
                                   capture_output=True, text=True, timeout=2)
                if r.returncode == 0:
                    exe_path = r.stdout.strip().splitlines()[0]
                    exe_name = os.path.splitext(
                        os.path.basename(exe_path)
                    )[0].lower()
                    if exe_name not in CRITICAL_PROCESS_BLACKLIST:
                        return exe_path, q
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        return None, None

    def open_app(self, target):
        """Open an application by name."""
        if not target:
            return False, "I'm not sure what to open."

        t = target.strip()
        tl = t.lower()
        print(f"[ACTION] Open app: '{t}'")

        # Check website shortcuts first
        if tl in WEBSITE_SHORTCUTS:
            url = WEBSITE_SHORTCUTS[tl]
            try:
                subprocess.Popen(["start", url], shell=True)
                return True, f"Opening {t}"
            except Exception as e:
                return False, f"Couldn't open {t}: {e}"

        # Check if it looks like a URL
        if tl.endswith((".com", ".org", ".net", ".gov", ".edu", ".io", ".in")) or \
           tl.startswith(("http://", "https://", "www.")):
            url = tl if tl.startswith(("http://", "https://")) else "https://" + tl
            try:
                subprocess.Popen(["start", url], shell=True)
                return True, f"Opening {t}"
            except Exception as e:
                return False, f"Couldn't open {t}: {e}"

        # Special apps with ms- protocols
        if tl in SPECIAL_APPS:
            path, display = SPECIAL_APPS[tl]
            try:
                if path.startswith("ms-"):
                    subprocess.Popen(["start", path], shell=True)
                else:
                    subprocess.Popen([path])
                return True, f"Opening {display or t}"
            except FileNotFoundError:
                # Try via shell
                try:
                    subprocess.Popen(["start", "", path], shell=True)
                    return True, f"Opening {display or t}"
                except Exception as e:
                    return False, f"Couldn't open {display or t}: {e}"
            except Exception as e:
                return False, f"Couldn't open {display or t}: {e}"

        # Index search
        path, disp = self.find_app(t)
        if path:
            try:
                if path.lower().endswith(".lnk"):
                    os.startfile(path)
                elif os.path.isfile(path):
                    subprocess.Popen([path])
                else:
                    subprocess.Popen(["start", "", path], shell=True)
                return True, f"Opening {disp or t}"
            except Exception as e:
                return False, f"Couldn't open {disp or t}: {e}"

        return False, f"I couldn't find '{t}'. Try saying the full app name."

    def close_app(self, target):
        """Close an application by name."""
        if not target:
            return False, "I'm not sure what to close."

        t = target.strip().lower()
        print(f"[ACTION] Close app: '{t}'")

        # Safety check
        if t in CRITICAL_PROCESS_BLACKLIST or any(
            blocked in t for blocked in CRITICAL_PROCESS_BLACKLIST
        ):
            return False, "I can't close system processes — that would be unsafe."

        # Resolve process name
        proc = None
        if t in SPECIAL_APPS:
            _, display = SPECIAL_APPS[t]
            # Get the exe name from special apps
            exe = SPECIAL_APPS[t][0]
            if exe and not exe.startswith("ms-"):
                proc = os.path.basename(exe)
        else:
            for name, (path, disp) in self.apps.items():
                if self._is_critical(name):
                    continue
                if t in name or name in t:
                    proc = os.path.basename(path)
                    break

        if not proc:
            proc = f"{t}.exe"

        # Final safety check
        proc_base = os.path.splitext(proc)[0].lower()
        if proc_base in CRITICAL_PROCESS_BLACKLIST:
            return False, "I can't close critical system processes."

        try:
            # Gentle close first
            r = subprocess.run(
                ["taskkill", "/im", proc],
                capture_output=True, text=True, timeout=5
            )
            if r.returncode == 0 or "SUCCESS" in r.stdout.upper():
                return True, f"Closed {target}"

            # Force close as fallback
            r2 = subprocess.run(
                ["taskkill", "/f", "/im", proc],
                capture_output=True, text=True, timeout=5
            )
            if r2.returncode == 0 or "SUCCESS" in r2.stdout.upper():
                return True, f"Closed {target}"

            # Window title fallback
            subprocess.run(
                ["taskkill", "/f", "/fi", f"WINDOWTITLE eq *{target}*"],
                capture_output=True, text=True, timeout=5
            )
            return True, f"Closed {target}"
        except subprocess.TimeoutExpired:
            return False, "That's taking too long. Try again?"
        except Exception as e:
            return False, f"Couldn't close {target}: {e}"

    def switch_to_app(self, target):
        """Bring a running app to the foreground."""
        if not target:
            return False, "Not sure which app to switch to."

        t = target.strip().lower()
        print(f"[ACTION] Switch to: '{t}'")

        try:
            import pygetwindow as gw
            windows = gw.getAllWindows()
            for w in windows:
                if w.title and t in w.title.lower():
                    try:
                        if w.isMinimized:
                            w.restore()
                        w.activate()
                        return True, f"Switched to {w.title}"
                    except Exception:
                        pass

            # Try matching by app name in SPECIAL_APPS
            if t in SPECIAL_APPS:
                display = SPECIAL_APPS[t][1]
                for w in windows:
                    if w.title and display and display.lower() in w.title.lower():
                        try:
                            if w.isMinimized:
                                w.restore()
                            w.activate()
                            return True, f"Switched to {w.title}"
                        except Exception:
                            pass
        except ImportError:
            pass
        except Exception as e:
            print(f"[WARN] switch_to_app error: {e}")

        # Fallback: just try to open it (will bring existing instance to front for most apps)
        return self.open_app(target)
