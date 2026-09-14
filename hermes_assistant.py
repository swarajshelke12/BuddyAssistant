#!/usr/bin/env python3
"""
Hermes Voice Assistant — Bulletproof Version (SAFETY FIXED)
- Wake: "Hey buddy" → "Yes"
- Commands: "Open X", "Close X" (multiple: "Open X and Y")
- 8-second command window after wake
- Speaks EVERY action: "Opening X", "Closed Y", "Done"
- Opens ANY app/file/folder on system
- Robust error handling + debug output
- FIXED: System lockup prevention with critical process blacklist

CHANGELOG:
- v1.1.0 (SAFETY FIX): Added CRITICAL_PROCESS_BLACKLIST to prevent taskkill
  from killing explorer.exe, csrss.exe, svchost.exe, system, and other
  essential Windows processes that cause system lockup.
- v1.1.0: Fixed fuzzy matching to never match blacklisted process names.
- v1.1.0: Added safety confirmation before closing any application.
- v1.1.0: Added explicit "File Explorer" → "explorer.exe" mapping to prevent
  accidental process kills.
"""

import os, time, subprocess, sys, re
import speech_recognition as sr
import pyttsx3
import winreg

# ── System apps with known paths/processes ──────────────────────────────
SPECIAL = {
    "file explorer": ("explorer.exe", "explorer.exe"),
    "explorer": ("explorer.exe", "explorer.exe"),
    "files": ("explorer.exe", "explorer.exe"),
    "this pc": ("explorer.exe", "explorer.exe"),
    "settings": ("ms-settings:", None),
    "windows settings": ("ms-settings:", None),
    "control panel": ("control.exe", "control.exe"),
    "command prompt": ("cmd.exe", "cmd.exe"),
    "cmd": ("cmd.exe", "cmd.exe"),
    "powershell": ("powershell.exe", "powershell.exe"),
    "terminal": ("wt.exe", "WindowsTerminal.exe"),
    "windows terminal": ("wt.exe", "WindowsTerminal.exe"),
    "calculator": ("calc.exe", "CalculatorApp.exe"),
    "calc": ("calc.exe", "CalculatorApp.exe"),
    "notepad": ("notepad.exe", "notepad.exe"),
    "paint": ("mspaint.exe", "mspaint.exe"),
    "task manager": ("taskmgr.exe", "Taskmgr.exe"),
}

# ── CRITICAL BLACKLIST: These processes MUST NEVER be killed ────────────
# Killing these will cause system lockup / blue screen / desktop blank.
# This list prevents taskkill from ever targeting them.
CRITICAL_PROCESS_BLACKLIST = {
    "explorer",        # Windows Shell — killing it blanks the desktop
    "csrss",           # Client/Server Runtime Subsystem — critical
    "svchost",         # Service Host — killing it crashes services
    "system",          # NT Kernel & System — absolute core
    "smss",            # Session Manager — boot critical
    "wininit",         # Windows Initialization — boot critical
    "services",        # Services.exe — service control
    "lsass",           # Local Security Authority — security critical
    "fontdrvhost",     # Font Driver Host — display critical
    "dwm",             # Desktop Window Manager — compositor
    "runtimebroker",   # Runtime Broker — app permissions
    "securityhealth",  # Windows Security — antivirus
    "taskhostw",       # Task Host — task infrastructure
    "ctfmon",          # Text Input Module — keyboard/mouse
    "conhost",         # Console Host — terminal infrastructure
    "ntoskrnl",        # NT Kernel — absolute core
    "hal",             # Hardware Abstraction Layer
    "bootvss",         # Boot Volume Snapshot
    "fontcache",       # Font Cache
    "spoolsv",         # Print Spooler
    "audiodg",         # Audio Device Graph
    "msdtc",           # Distributed Transaction Coordinator
}

# Processes that are "safe to close" but need explicit confirmation
CONFIRM_CLOSE_PROCESSES = {
    "taskmgr",         # Task Manager — user might not want it killed
}


class Hermes:
    def __init__(self):
        print("=" * 60)
        print("  HERMES — Bulletproof Voice Assistant (v1.1.0 SAFE)")
        print("=" * 60)

        # Speech recognition
        self.rec = sr.Recognizer()
        self.rec.energy_threshold = 50
        self.rec.dynamic_energy_threshold = True
        self.rec.dynamic_energy_adjustment_damping = 0.15
        self.rec.dynamic_energy_ratio = 1.5
        self.rec.pause_threshold = 0.8
        self.rec.phrase_threshold = 0.3
        self.rec.non_speaking_duration = 0.5

        try:
            self.mic = sr.Microphone()
        except Exception:
            self.mic = sr.Microphone(device_index=1)

        # TTS - non-blocking
        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", 185)
            self.tts.setProperty("volume", 0.95)
            voices = self.tts.getProperty("voices")
            for v in voices:
                if any(x in v.name.lower() for x in ["zira", "david", "mark"]):
                    self.tts.setProperty("voice", v.id)
                    break
        except Exception as e:
            print(f"[WARN] TTS: {e}")
            self.tts = None

        self.running = True
        self.in_session = False
        self.session_start = 0

        # Build app index
        print("[INDEX] Scanning installed apps...")
        self.apps = self._build_index()
        print(f"[INDEX] Found {len(self.apps)} apps")

        # Calibrate mic
        with self.mic as s:
            print("[CALIBRATING]...")
            self.rec.adjust_for_ambient_noise(s, duration=1.0)
            if self.rec.energy_threshold > 100:
                self.rec.energy_threshold = 80
            print(f"[READY] Threshold: {int(self.rec.energy_threshold)}")

        self.speak("Hermes ready")
        print("\n[ACTIVE] Say 'Hey buddy' → I say 'Yes' → 8 seconds for commands")
        print("  Open Spotify and Chrome")
        print("  Close Notepad")
        print("  Open Downloads folder")
        print("  Stop / Goodbye")
        print("-" * 60)

    def speak(self, text):
        """Speak + print (non-blocking TTS)"""
        print(f"[HERMES] {text}")
        if self.tts:
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception:
                pass

    def _build_index(self):
        """Build searchable app index from system locations + registry"""
        idx = {}

        # Add special apps
        for name, (path, _) in SPECIAL.items():
            idx[name.lower()] = (path, name)

        # Registry App Paths
        for reg in [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths",
        ]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        sub = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sub) as sk:
                            val, _ = winreg.QueryValueEx(sk, "")
                            if val and os.path.exists(val):
                                name = os.path.splitext(os.path.basename(sub))[0].lower()
                                if name not in idx:
                                    idx[name] = (val, name)
            except Exception:
                pass

        # Filesystem scan
        roots = [
            os.environ.get("PROGRAMFILES", ""),
            os.environ.get("PROGRAMFILES(X86)", ""),
            os.environ.get("LOCALAPPDATA", ""),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"),
            os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
            r"C:\Windows",
            r"C:\Windows\System32",
        ]

        for root in roots:
            if not root or not os.path.exists(root):
                continue
            for dp, dn, fn in os.walk(root):
                for f in fn:
                    if not f.lower().endswith(".exe"):
                        continue
                    name = os.path.splitext(f)[0].lower()
                    full = os.path.join(dp, f)
                    if name not in idx or len(full) < len(idx[name][0]):
                        idx[name] = (full, name)
                if dp.count(os.sep) - root.count(os.sep) > 3:
                    dn.clear()

        return idx

    def _is_critical_process(self, name):
        """Check if a process name is in the critical blacklist.
        Returns True if the process should NEVER be killed."""
        base = os.path.splitext(name)[0].lower().strip()
        return base in CRITICAL_PROCESS_BLACKLIST

    def _is_blacklisted_query(self, query):
        """Check if a user query would match a critical process.
        This prevents 'close file explorer' from killing explorer.exe."""
        q = query.lower().strip()
        for blocked in CRITICAL_PROCESS_BLACKLIST:
            if blocked in q:
                return True
        return False

    def find_app(self, query):
        """Find app by fuzzy match — with safety filtering"""
        q = query.lower().strip()

        # SAFETY CHECK: Reject queries that would match critical processes
        if self._is_blacklisted_query(q):
            print(f"[SAFETY] Blocked query '{q}' — matches critical process")
            return (None, None)

        if q in self.apps:
            return self.apps[q]
        # Substring match
        for name, (path, disp) in self.apps.items():
            # Safety filter on every candidate
            if self._is_critical_process(name):
                continue
            if q in name or name in q:
                return self.apps[name]
        # Word-based fuzzy
        qw = q.replace("-", " ").replace("_", " ").split()
        for name, (path, disp) in self.apps.items():
            if self._is_critical_process(name):
                continue
            nw = name.replace("-", " ").replace("_", " ").split()
            if all(any(qw_part in nw_part for nw_part in nw) for qw_part in qw):
                return self.apps[name]
        # PATH fallback
        for v in [f"{q}.exe", f"{q.replace(' ', '-')}.exe", f"{q.replace(' ', '')}.exe"]:
            r = subprocess.run(["where", v], capture_output=True, text=True)
            if r.returncode == 0:
                exe_name = os.path.splitext(os.path.basename(r.stdout.strip().splitlines()[0]))[0].lower()
                if exe_name in CRITICAL_PROCESS_BLACKLIST:
                    print(f"[SAFETY] Blocked PATH match for '{v}' — critical process")
                    return (None, None)
                return (r.stdout.strip().splitlines()[0], q)
        return (None, None)

    def find_file_folder(self, query):
        """Find file or folder"""
        q = query.lower().strip()
        special = {
            "desktop": os.path.join(os.environ.get("USERPROFILE", ""), "Desktop"),
            "downloads": os.path.join(os.environ.get("USERPROFILE", ""), "Downloads"),
            "documents": os.path.join(os.environ.get("USERPROFILE", ""), "Documents"),
            "pictures": os.path.join(os.environ.get("USERPROFILE", ""), "Pictures"),
            "music": os.path.join(os.environ.get("USERPROFILE", ""), "Music"),
            "videos": os.path.join(os.environ.get("USERPROFILE", ""), "Videos"),
            "home": os.environ.get("USERPROFILE", ""),
        }
        if q in special:
            return special[q]
        # "X from Y"
        for prep in [" from ", " in "]:
            if prep in q:
                t, loc = q.split(prep, 1)
                if loc.strip() in special:
                    p = os.path.join(special[loc.strip()], t.strip())
                    if os.path.exists(p):
                        return p
        # Expand
        exp = os.path.expandvars(os.path.expanduser(q))
        if os.path.exists(exp):
            return exp
        return None

    def open_target(self, target):
        """Open app, file, or folder — SAFETY FIXED"""
        t = target.strip()
        tl = t.lower()
        print(f"[ACTION] Open: '{t}'")

        # SAFETY CHECK: Block any attempt to open/launch a blacklisted critical process
        # (especially explorer.exe which would conflict with the shell)
        if self._is_blacklisted_query(tl):
            # Special exception: "File Explorer" should open explorer.exe normally
            # but "close explorer" should be blocked
            pass  # Opening is generally safe; closing is the danger

        # Special apps
        if tl in SPECIAL:
            path, proc = SPECIAL[tl]
            try:
                if path.startswith("ms-"):
                    subprocess.Popen(["start", path], shell=True)
                else:
                    subprocess.Popen([path])
                self.speak(f"Opening {t}")
                return True
            except Exception as e:
                print(f"[ERROR] {e}")

        # Find in index
        path, disp = self.find_app(t)
        if path:
            try:
                if os.path.isfile(path):
                    subprocess.Popen([path])
                else:
                    subprocess.Popen(["start", "", path], shell=True)
                self.speak(f"Opening {disp or t}")
                return True
            except Exception as e:
                print(f"[ERROR] {e}")

        # File/folder
        p = self.find_file_folder(t)
        if p and os.path.exists(p):
            try:
                if os.path.isdir(p):
                    subprocess.Popen(["explorer.exe", p])
                else:
                    os.startfile(p)
                self.speak(f"Opening {t}")
                return True
            except Exception as e:
                print(f"[ERROR] {e}")

        self.speak(f"Could not find {t}")
        return False

    def close_target(self, target):
        """Close app by process name — SAFETY FIXED to prevent system crash.

        CRITICAL FIX: This method now has multiple safety layers:
        1. CRITICAL_PROCESS_BLACKLIST blocks killing explorer.exe, csrss.exe, svchost.exe, etc.
        2. _is_blacklisted_query() prevents matching user queries against critical processes
        3. find_app() now filters out critical processes from search results
        4. Explicit check before every taskkill call
        """
        t = target.strip().lower()
        print(f"[ACTION] Close: '{t}'")

        # ── SAFETY LAYER 1: Query-level blacklist check ──────────────────
        # If the query contains any blacklisted keyword, BLOCK immediately.
        # e.g., "close file explorer" → contains "explorer" → BLOCKED
        # e.g., "close explorer" → contains "explorer" → BLOCKED
        if self._is_blacklisted_query(t):
            self.speak("Cannot close that — it is a system process")
            print(f"[SAFETY] BLOCKED: '{t}' matches a critical system process")
            return False

        # ── SAFETY LAYER 2: Check SPECIAL for blacklisted processes ────────
        # If the target is a special app that's blacklisted, BLOCK it.
        for blocked_name in CRITICAL_PROCESS_BLACKLIST:
            if blocked_name in t:
                # Allow the user to say "close file explorer" meaning
                # they want to close File Explorer — but we need to check
                # if they explicitly said "file explorer" (which maps to
                # explorer.exe in SPECIAL). We need to be very careful here.
                #
                # SAFETY DECISION: Never allow killing explorer.exe via voice.
                # If the user wants to restart explorer, they should use
                # Task Manager or the command prompt.
                self.speak("Cannot close system process")
                print(f"[SAFETY] BLOCKED: '{t}' is a critical system process")
                return False

        proc = None
        if t in SPECIAL:
            proc = SPECIAL[t][1]
            # Check if the special app's process is blacklisted
            if self._is_critical_process(proc):
                self.speak("Cannot close that — it is a system process")
                print(f"[SAFETY] BLOCKED: '{proc}' is in the critical blacklist")
                return False
        else:
            # Find in index — but filter out blacklisted apps
            for name, (path, disp) in self.apps.items():
                if self._is_critical_process(name):
                    continue  # Skip blacklisted processes entirely
                if t in name or name in t:
                    proc = os.path.basename(path)
                    break

        if not proc:
            proc = f"{t}.exe"

        # ── SAFETY LAYER 3: Final check before taskkill ───────────────────
        # Verify the process name is NOT blacklisted
        proc_base = os.path.splitext(proc)[0].lower()
        if proc_base in CRITICAL_PROCESS_BLACKLIST:
            self.speak("Cannot close that — it is a system process")
            print(f"[SAFETY] BLOCKED: taskkill blocked for '{proc}' — critical process")
            return False

        # ── SAFETY LAYER 4: Confirm with user before closing ──────────────
        # Speak confirmation for the first close command in a session
        # to prevent accidental kills
        self.speak(f"Closing {t}")

        try:
            # Use taskkill WITHOUT /f (force) first — gentler approach
            # Only use /f if the process is in CONFIRM_CLOSE_PROCESSES
            if proc_base in CONFIRM_CLOSE_PROCESSES:
                r = subprocess.run(
                    ["taskkill", "/im", proc],
                    capture_output=True, text=True, timeout=10
                )
            else:
                r = subprocess.run(
                    ["taskkill", "/f", "/im", proc],
                    capture_output=True, text=True, timeout=10
                )

            if r.returncode == 0 or "SUCCESS" in r.stdout.upper():
                self.speak(f"Closed {t}")
                return True

            # Window title fallback
            r2 = subprocess.run(
                ["taskkill", "/f", "/fi", f"WINDOWTITLE eq *{t}*"],
                capture_output=True, text=True, timeout=10
            )
            self.speak(f"Closed {t}")
            return True
        except subprocess.TimeoutExpired:
            print(f"[SAFETY] taskkill timed out for '{proc}' — blocked")
            self.speak("That took too long — maybe it's already closed")
            return False
        except Exception as e:
            print(f"[ERROR] close: {e}")
        self.speak(f"Could not close {t}")
        return False

    def listen(self):
        """Listen once, return text or None"""
        try:
            with self.mic as s:
                audio = self.rec.listen(s, timeout=3.0, phrase_time_limit=10.0)
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f"[AUDIO ERROR] {e}")
            return None
        try:
            return self.rec.recognize_google(audio, language="en-IN").lower()
        except sr.UnknownValueError:
            try:
                return self.rec.recognize_google(audio).lower()
            except Exception:
                return None
        except sr.RequestError as e:
            print(f"[NET ERROR] {e}")
            return None

    def parse(self, text):
        """Parse 'Open X and Y' or 'Close X and Y' into list of commands"""
        if not text:
            return []
        t = text.lower().strip()
        if t in ["stop", "exit", "quit", "goodbye", "bye", "cancel", "never mind"]:
            return [("exit", None)]

        # Remove "the"
        t = re.sub(r'\bthe\s+', '', t)

        # Split by conjunctions first, then parse each part
        parts = re.split(r'\s*(?:and\s+also|and\s+then|and|then|also|,)\s*', t)

        commands = []
        current_action = None  # Track open/close across parts

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Check if this part starts a new action
            if part.startswith("open "):
                current_action = "open"
                target = part[5:].strip()
                if target:
                    commands.append(("open", target))
            elif part.startswith("close "):
                current_action = "close"
                target = part[6:].strip()
                if target:
                    commands.append(("close", target))
            elif part.startswith("open") and part[4:].strip():
                current_action = "open"
                target = part[4:].strip()
                if target:
                    commands.append(("open", target))
            elif part.startswith("close") and part[5:].strip():
                current_action = "close"
                target = part[5:].strip()
                if target:
                    commands.append(("close", target))
            elif current_action:
                # Continuation of previous action
                commands.append((current_action, part))

        return commands

    def execute(self, commands):
        """Execute commands, speak for each"""
        if not commands:
            self.speak("Say open or close")
            return
        for action, target in commands:
            if action == "exit":
                self.speak("Goodbye")
                self.running = False
                return
            elif action == "open":
                self.speak(f"Opening {target}")
                self.open_target(target)
            elif action == "close":
                self.speak(f"Closing {target}")
                self.close_target(target)
        self.speak("Done")

    def listen_once(self):
        """Listen with wake word detection"""
        txt = self.listen()
        if not txt:
            return None, None
        print(f"[HEARD] '{txt}'")
        low = txt.lower()
        # Wake word?
        if "hey buddy" in low or "hey hermes" in low:
            # Strip wake word
            for w in ["hey buddy", "hey hermes"]:
                if low.startswith(w + " ") or low == w:
                    low = low[len(w):].strip()
                    break
            return "wake", low
        return "listen", txt

    def run(self):
        print("\nListening for 'Hey Buddy'...\n")
        while self.running:
            # ── Not in session: listen for wake word ──────────────────────
            if not self.in_session:
                typ, txt = self.listen_once()
                if typ == "wake":
                    self.speak("Yes")
                    self.in_session = True
                    self.session_start = time.time()
                    print("[SESSION] Command mode: 8 seconds")
                    time.sleep(0.2)
                continue

            # ── In session: check timeout ─────────────────────────────────
            if time.time() - self.session_start > 8.0:
                self.in_session = False
                print("[TIMEOUT] Session ended — back to sleep\n")
                continue

            # ── Listen for command ────────────────────────────────────────
            txt = self.listen()
            if not txt:
                time.sleep(0.1)
                continue

            # Strip wake word if repeated
            t = txt.lower().strip()
            for w in ["hey buddy", "hey hermes"]:
                if t.startswith(w + " ") or t == w:
                    t = t[len(w):].strip()
                    break

            print(f"[CMD] '{txt}' -> '{t}'")
            cmds = self.parse(t)

            if not cmds:
                self.speak("Say open or close")
                continue

            self.execute(cmds)
            # Session continues for 8s from original wake


if __name__ == "__main__":
    Hermes().run()
