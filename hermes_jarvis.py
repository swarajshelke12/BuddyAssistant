#!/usr/bin/env python3
"""
Hermes Voice Assistant — Jarvis Edition
- Natural language understanding (like Jarvis from Iron Man)
- Context-aware conversations
- Faster responses with background indexing
- Conversational TTS responses
- Continuous listening after wake word
- Smart task chaining and sequencing
"""

import os, time, subprocess, sys, re, json, threading
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import winreg

# ── Configuration ────────────────────────────────────────
WAKE_WORDS = ["hey buddy", "hey hermes", "hey jarvis"]
SPECIAL = {
    "file explorer": ("explorer.exe", "File Explorer"),
    "explorer": ("explorer.exe", "File Explorer"),
    "files": ("explorer.exe", "File Explorer"),
    "this pc": ("explorer.exe", "File Explorer"),
    "settings": ("ms-settings:", None),
    "windows settings": ("ms-settings:", None),
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
    "firefox": ("firefox.exe", "Mozilla Firefox"),
    "edge": ("msedge.exe", "Microsoft Edge"),
    "whatsapp": ("whatsapp.exe", "WhatsApp"),
    "telegram": ("telegram.exe", "Telegram"),
    "discord": ("discord.exe", "Discord"),
    "steam": ("steam.exe", "Steam"),
    "epic games": ("epicgameslauncher.exe", "Epic Games Launcher"),
    "netflix": ("netflix.com", None),  # Will open in browser
    "youtube": ("youtube.com", None),
    "gmail": ("mail.google.com", None),
    "facebook": ("facebook.com", None),
    "instagram": ("instagram.com", None),
    "twitter": ("twitter.com", None),
    "reddit": ("reddit.com", None),
}

# ── CRITICAL BLACKLIST: These processes MUST NEVER be killed ────────
CRITICAL_PROCESS_BLACKLIST = {
    "system", "smss", "csrss", "wininit", "winlogon", "services", "lsass",
    "svchost", "explorer", "dwm", "taskmgr", "winlogon", "fontdrvhost",
    "dwm", "sihost", "ctfmon", "rundll32", "dllhost", "conhost", "winlogon"
}

# ── CONVERSATIONAL RESPONSES ──────────────────────────────
OPEN_RESPONSES = [
    "Opening {target} for you",
    "On it - launching {target}",
    "Consider it done - {target} is starting",
    "Opening {target}",
    "Launching {target}",
    "Starting {target} now",
    "You got it - {target} is coming up"
]

CLOSE_RESPONSES = [
    "Closing {target}",
    "Shutting down {target}",
    "Taking care of {target}",
    "{target} is being closed",
    "Consider it closed",
    "Shutting {target} down"
]

ERROR_RESPONSES = [
    "I'm having trouble with that",
    "Let me try again",
    "One moment please",
    "Give me a second",
    "I'll figure that out"
]

# ────────────────────────────────────────────────────────────────
class HermesJarvis:
    def __init__(self):
        self.rec = sr.Recognizer()
        self.mic = sr.Microphone(device_index=17)  # Adjust as needed
        self.tts = pyttsx3.init()
        self._setup_tts()
        self.apps = {}
        self.index_building = False
        self.index_built = False
        self.context = {
            "last_opened": [],
            "last_closed": [],
            "current_session": [],
            "preferences": {}
        }
        self.conversation_state = "idle"  # idle, listening, processing
        self._build_index_async()  # Start building index in background
    
    def _setup_tts(self):
        """Configure text-to-speech for more natural sound"""
        voices = self.tts.getProperty('voices')
        if voices:
            # Try to find a pleasant voice
            for voice in voices:
                if "female" in voice.name.lower() or "zira" in voice.name.lower() or "hazel" in voice.name.lower():
                    self.tts.setProperty('voice', voice.id)
                    break
        self.tts.setProperty('rate', 180)  # Slightly faster than default
        self.tts.setProperty('volume', 0.9)
    
    def speak(self, text):
        """Speak text with more natural delivery"""
        print(f"[HERMES] {text}")
        if self.tts:
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception:
                pass
    
    def _build_index_async(self):
        """Build app index in background thread"""
        if self.index_building:
            return
        self.index_building = True
        thread = threading.Thread(target=self._build_index, daemon=True)
        thread.start()
    
    def _build_index(self):
        """Build searchable app index - optimized for speed"""
        start_time = time.time()
        print("[INDEX] Building background index...")
        idx = {}
        
        # 1. Add special apps (instant)
        for name, (path, _) in SPECIAL.items():
            idx[name.lower()] = (path, name)
        
        # 2. Registry App Paths (very fast)
        for reg in [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths",
        ]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        sub = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sub) as sk:
                            try:
                                val, _ = winreg.QueryValueEx(sk, "")
                                if val and os.path.exists(val):
                                    name = os.path.splitext(os.path.basename(sub))[0].lower()
                                    if name not in idx:
                                        idx[name] = (val, name)
                            except FileNotFoundError:
                                pass
            except Exception:
                pass
        
        # 3. Quick filesystem scan - LIMITED to key locations
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
                        idx[name] = (full, name)
        
        self.apps = idx
        self.index_built = True
        self.index_building = False
        elapsed = time.time() - start_time
        print(f"[INDEX] Background index complete: {len(idx)} apps in {elapsed:.1f}s")
    
    def _is_critical_process(self, name):
        """Check if a process name is in the critical blacklist."""
        base = os.path.splitext(name)[0].lower().strip()
        return base in CRITICAL_PROCESS_BLACKLIST
    
    def _is_blacklisted_query(self, query):
        """Check if a user query would match a critical process."""
        q = query.lower().strip()
        return any(blocked in q for blocked in CRITICAL_PROCESS_BLACKLIST)
    
    def find_app(self, query):
        """Find app by fuzzy match - with safety filtering"""
        q = query.lower().strip()
        
        # SAFETY: Reject queries that would match critical processes
        if self._is_blacklisted_query(q):
            return (None, None)
        
        # Wait briefly for index if not ready (but don't block long)
        wait_start = time.time()
        while not self.index_built and time.time() - wait_start < 3.0:
            time.sleep(0.1)
        
        # Use cached index or fallback to SPECIAL
        search_dict = self.apps if self.index_built else SPECIAL
        
        if q in search_dict:
            return search_dict[q]
        
        # Substring match
        for name, (path, disp) in search_dict.items():
            if self._is_critical_process(name):
                continue
            if q in name or name in q:
                return search_dict[name]
        
        # Word-based fuzzy
        qw = q.replace("-", " ").replace("_", " ").split()
        for name, (path, disp) in search_dict.items():
            if self._is_critical_process(name):
                continue
            nw = name.replace("-", " ").replace("_", " ").split()
            if all(any(qw_part in nw_part for nw_part in nw) for qw_part in qw):
                return search_dict[name]
        
        # PATH fallback for .exe files
        for v in [f"{q}.exe", f"{q.replace(' ', '-')}.exe", f"{q.replace(' ', '')}.exe"]:
            try:
                r = subprocess.run(["where", v], capture_output=True, text=True, timeout=2)
                if r.returncode == 0:
                    exe_path = r.stdout.strip().splitlines()[0]
                    exe_name = os.path.splitext(os.path.basename(exe_path))[0].lower()
                    if exe_name not in CRITICAL_PROCESS_BLACKLIST:
                        return (exe_path, q)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        return (None, None)
    
    def find_file_folder(self, query):
        """Find file or folder - enhanced for natural language"""
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
        
        # Handle "X from Y", "X in Y", "show me X", etc.
        for prep in [" from ", " in ", " show me ", " open "]:
            if prep in q:
                parts = q.split(prep, 1)
                if len(parts) == 2:
                    t, loc = parts[0].strip(), parts[1].strip()
                    if loc in special:
                        p = os.path.join(special[loc], t)
                        if os.path.exists(p):
                            return p
        
        # Handle natural phrases like "my downloads folder", "the documents directory"
        natural_map = {
            "my downloads": "downloads",
            "my documents": "documents", 
            "my desktop": "desktop",
            "my pictures": "pictures",
            "my music": "music",
            "my videos": "videos"
        }
        for phrase, key in natural_map.items():
            if phrase in q and key in special:
                return special[key]
        
        # Expand environment variables and user paths
        exp = os.path.expandvars(os.path.expanduser(q))
        if os.path.exists(exp):
            return exp
        return None
    
    def natural_language_parse(self, text):
        """
        Parse natural language into commands - understands conversational English
        Examples: 
        - "Can you open Spotify please?"
        - "I need to check my email"
        - "Close Chrome and open Firefox"
        - "Launch Photoshop and start a new design"
        - "Play some music on Spotify"
        """
        if not text:
            return []
        
        # Convert to lowercase for easier matching
        original = text.strip()
        text = text.lower().strip()
        
        # Exit commands
        exit_phrases = ["goodbye", "bye", "see you later", "that's all", "stop", "exit", "quit", "go to sleep"]
        if any(phrase in text for phrase in exit_phrases):
            return [("exit", None)]
        
        # Remove polite words and question words for cleaner parsing
        polite_words = ["please", "could you", "can you", "would you", "i want to", "i need to", 
                       "let's", "lets", "go ahead and", "just", "maybe", "possibly"]
        for word in polite_words:
            text = text.replace(word, " ")
        
        # Remove question words at start
        question_starts = ["what", "where", "when", "why", "how", "who"]
        for word in question_starts:
            if text.startswith(word + " "):
                text = text[len(word)+1:].strip()
                break
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # If empty after cleaning, try to infer intent
        if not text or text in ["hey", "hi", "hello"]:
            return [("greeting", None)]
        
        commands = []
        
        # Handle complex sentences with multiple actions
        # Split by conjunctions but keep track of action type
        parts = re.split(r'\s*(?:and|then|,|&|\s+plus\s+|\s+as well as\s+)\s*', text)
        
        current_action = None
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Detect action type from verbs
            action_detected = None
            target_part = part
            
            # Opening related verbs
            open_verbs = ["open", "launch", "start", "run", "execute", "fire up", "kick off", 
                         "begin", "commence", "initiate", "boot up", "power on", "turn on",
                         "play", "watch", "visit", "go to", "navigate to", "show me", "display"]
            
            # Closing related verbs  
            close_verbs = ["close", "shut", "exit", "quit", "terminate", "kill", "end", 
                          "stop", "close down", "shut down", "power off", "turn off"]
            
            # Check for opening intent
            for verb in open_verbs:
                if part.startswith(verb + " ") or part == verb:
                    action_detected = "open"
                    target_part = part[len(verb):].strip()
                    break
            
            # Check for closing intent
            if not action_detected:
                for verb in close_verbs:
                    if part.startswith(verb + " ") or part == verb:
                        action_detected = "close"
                        target_part = part[len(verb):].strip()
                        break
            
            # Handle special cases
            if not action_detected:
                # "play music" -> open spotify/youtube
                if part.startswith("play ") and ("music" in part or "song" in part):
                    action_detected = "open"
                    # Extract what to play
                    what_to_play = part[5:].strip()
                    if "spotify" in what_to_play or "music" in what_to_play:
                        target_part = "spotify"
                    elif "youtube" in what_to_play or "video" in what_to_play:
                        target_part = "youtube"
                    else:
                        # Default to Spotify for music
                        target_part = "spotify"
                # "watch youtube" -> open youtube
                elif part.startswith("watch ") and ("video" in part or "youtube" in part or "movie" in part):
                    action_detected = "open"
                    target_part = "youtube"
                # "check email" -> open gmail/outlook
                elif part.startswith("check ") and ("email" in part or "mail" in part):
                    action_detected = "open"
                    target_part = "gmail"
                # "open browser" -> open chrome
                elif part == "browser" or part.startswith("open browser"):
                    action_detected = "open"
                    target_part = "chrome"
                # "close it" -> refer to context
                elif part in ["close it", "shut it down", "exit it", "quit it"]:
                    if self.context["last_opened"]:
                        action_detected = "close"
                        target_part = self.context["last_opened"][-1]  # Most recently opened
                    else:
                        # Default to closing last thing we know about
                        target_part = "the current window"
                # "open it again" -> reopen last opened
                elif part in ["open it again", "reopen it", "launch it again"]:
                    if self.context["last_opened"]:
                        action_detected = "open"
                        target_part = self.context["last_opened"][-1]
                    else:
                        target_part = "the last thing"
            
            # If we still don't have an action, make an educated guess
            if not action_detected:
                # If it sounds like an app name or website, assume open
                if any(keyword in part for keyword in [".com", ".org", ".net", "spotify", "chrome", "firefox", 
                                                     "whatsapp", "telegram", "discord", "steam"]):
                    action_detected = "open"
                # If it contains words like "close", "shut", "end" assume close
                elif any(word in part for word in ["close", "shut", "end", "exit", "quit", "stop"]):
                    action_detected = "close"
                # Default to open for unknown terms (safer assumption)
                else:
                    action_detected = "open"
            
            # Clean up the target
            target = target_part.strip()
            # Remove leading/trailing articles
            target = re.sub(r'^(the|a|an)\s+', '', target)
            target = re.sub(r'\s+(the|a|an)$', '', target)
            
            if target and action_detected:
                # Avoid duplicates in sequence
                if not commands or commands[-1] != (action_detected, target):
                    commands.append((action_detected, target))
                    current_action = action_detected
        
        return commands
    
    def listen(self):
        """Listen once, return text or None"""
        try:
            with self.mic as source:
                # Adjust for ambient noise each time for better accuracy
                self.rec.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.rec.listen(source, timeout=2.0, phrase_time_limit=8.0)
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f"[AUDIO ERROR] {e}")
            return None
        
        try:
            # Try with Indian English first, then fallback
            return self.rec.recognize_google(audio, language="en-IN").lower()
        except sr.UnknownValueError:
            try:
                return self.rec.recognize_google(audio).lower()
            except Exception:
                return None
        except sr.RequestError as e:
            print(f"[NET ERROR] {e}")
            return None
    
    def detect_wake_word(self, text):
        """Detect if wake word is present in text"""
        if not text:
            return False, None
        
        text_lower = text.lower().strip()
        for wake_word in WAKE_WORDS:
            if wake_word in text_lower:
                # Remove wake word from text
                remaining = text_lower.replace(wake_word, "", 1).strip()
                # Clean up extra spaces
                remaining = re.sub(r'\s+', ' ', remaining).strip()
                return True, remaining
        return False, None
    
    def execute_commands(self, commands):
        """Execute commands with natural, conversational responses"""
        if not commands:
            # Try to be helpful even when we don't understand
            self.speak(self._get_error_response())
            return
        
        for action, target in commands:
            if action == "exit":
                self.speak("Goodbye! Have a brilliant day.")
                self.running = False
                return
            elif action == "greeting":
                self.speak("Hello! How can I assist you today?")
                continue
            elif action == "open":
                response = self._get_open_response(target)
                self.speak(response)
                success = self.open_target(target)
                if success and target:
                    self.context["last_opened"].append(target)
                    # Keep only last 5 items
                    if len(self.context["last_opened"]) > 5:
                        self.context["last_opened"] = self.context["last_opened"][-5:]
            elif action == "close":
                response = self._get_close_response(target)
                self.speak(response)
                success = self.close_target(target)
                if success and target:
                    self.context["last_closed"].append(target)
                    if len(self.context["last_closed"]) > 5:
                        self.context["last_closed"] = self.context["last_closed"][-5:]
        
        # Only say "Done" if we executed multiple commands
        if len(commands) > 1:
            self.speak("All taken care of.")
    
    def _get_open_response(self, target):
        """Get a natural response for opening"""
        import random
        if not target:
            target = "that"
        template = random.choice(OPEN_RESPONSES)
        return template.format(target=target)
    
    def _get_close_response(self, target):
        """Get a natural response for closing"""
        import random
        if not target:
            target = "that"
        template = random.choice(CLOSE_RESPONSES)
        return template.format(target=target)
    
    def _get_error_response(self):
        """Get a helpful error response"""
        import random
        return random.choice(ERROR_RESPONSES)
    
    def open_target(self, target):
        """Open app, file, or folder - enhanced"""
        if not target:
            self.speak("I'm not sure what you'd like me to open.")
            return False
        
        t = target.strip()
        tl = t.lower()
        print(f"[ACTION] Open: '{t}'")
        
        # Special handling for websites
        if tl.endswith((".com", ".org", ".net", ".gov", ".edu")) or \
           tl.startswith(("http://", "https://", "www.")):
            try:
                if not tl.startswith(("http://", "https://")):
                    tl = "https://" + tl
                subprocess.Popen(["start", tl], shell=True)
                self.speak(f"Opening {t} in your browser")
                return True
            except Exception as e:
                print(f"[ERROR] {e}")
                self.speak(f"I had trouble opening {t}")
                return False
        
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
                display_name = disp or t
                self.speak(f"Opening {display_name}")
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
        
        self.speak(f"I couldn't find {t}. Would you like me to try something else?")
        return False
    
    def close_target(self, target):
        """Close app by process name - with safety"""
        if not target:
            self.speak("I'm not sure what you'd like me to close.")
            return False
        
        t = target.strip().lower()
        print(f"[ACTION] Close: '{t}'")
        
        # Handle contextual references
        if target in ["it", "that", "the current window", "this"]:
            if self.context["last_opened"]:
                target = self.context["last_opened"][-1]
                t = target.lower()
            else:
                self.speak("I'm not sure what you're referring to.")
                return False
        
        # Safety checks
        if self._is_blacklisted_query(t):
            self.speak("I can't close system processes - that would be unsafe.")
            return False
        
        # Check SPECIAL for blacklisted processes
        for blocked_name in CRITICAL_PROCESS_BLACKLIST:
            if blocked_name in t:
                self.speak("I can't close critical system processes.")
                return False
        
        proc = None
        if t in SPECIAL:
            proc = SPECIAL[t][1]
            if proc and self._is_critical_process(proc):
                self.speak("I can't close that system process.")
                return False
        else:
            # Find in index, filtering out blacklisted apps
            for name, (path, disp) in self.apps.items():
                if self._is_critical_process(name):
                    continue
                if t in name or name in t:
                    proc = os.path.basename(path)
                    break
        
        if not proc:
            proc = f"{t}.exe"
        
        # Final safety check
        proc_base = os.path.splitext(proc)[0].lower()
        if proc_base in CRITICAL_PROCESS_BLACKLIST:
            self.speak("I can't close critical system processes.")
            return False
        
        self.speak(f"Closing {target}")
        
        try:
            # Try gentle close first
            r = subprocess.run(
                ["taskkill", "/im", proc],
                capture_output=True, text=True, timeout=5
            )
            
            if r.returncode == 0 or "SUCCESS" in r.stdout.upper():
                self.speak(f"Closed {target}")
                return True
            
            # Window title fallback for stubborn apps
            r2 = subprocess.run(
                ["taskkill", "/f", "/fi", f"WINDOWTITLE eq *{target}*"],
                capture_output=True, text=True, timeout=5
            )
            
            self.speak(f"Closed {target}")
            return True
        except subprocess.TimeoutExpired:
            self.speak("That's taking longer than expected. Let me know if you'd like me to try again.")
            return False
        except Exception as e:
            print(f"[ERROR] close: {e}")
            self.speak(f"I had trouble closing {target}.")
            return False
    
    def run(self):
        """Main execution loop - Jarvis style"""
        print("""
        ╔════════════════════════════════════════════════════════════════════════╗
        ║                                                                          ║
        ║                     J A R V I S   A C T I V A T E D                     ║
        ║                                                                          ║
        ║  Say "Hey Buddy", "Hey Hermes", or "Hey Jarvis" to get my attention     ║
        ║  I understand natural English - just speak naturally!                  ║
        ║                                                                          ║
        ╚════════════════════════════════════════════════════════════════════════╝
        """)
        
        self.running = True
        self.in_session = False
        self.session_start = 0
        
        print("\\nListening for wake word...\\n")
        
        while self.running:
            # Listen for audio
            txt = self.listen()
            if not txt:
                time.sleep(0.1)
                continue
            
            print(f"[HEARD] '{txt}'")
            
            # Check for wake word
            is_wake, remaining_text = self.detect_wake_word(txt)
            
            if is_wake:
                # Wake word detected - respond and enter active mode
                self.speak("Yes?")
                self.in_session = True
                self.session_start = time.time()
                self.conversation_state = "listening"
                
                # If there was text after wake word, process it immediately
                if remaining_text:
                    print(f"[CMD] '{remaining_text}'")
                    cmds = self.natural_language_parse(remaining_text)
                    if cmds:
                        self.execute_commands(cmds)
                    # Stay in session for continued conversation
                else:
                    # Just wake word - invite further commands
                    self.conversation_state = "idle"
                continue
            
            # If we're in an active session, process commands
            if self.in_session:
                # Check if session has expired (30 seconds of inactivity)
                if time.time() - self.session_start > 30.0:
                    self.in_session = False
                    self.conversation_state = "idle"
                    print("[SESSION] Session ended due to inactivity")
                    self.speak("Going back to standby. Call me when you need me.")
                    continue
                
                # Process the command
                print(f"[CMD] '{txt}'")
                cmds = self.natural_language_parse(txt)
                
                if cmds:
                    self.execute_commands(cmds)
                    # Reset session timer on successful command
                    self.session_start = time.time()
                else:
                    # Didn't understand - ask for clarification politely
                    if self.conversation_state == "listening":
                        self.speak("I'm not sure I understood. Could you repeat that?")
                        self.conversation_state = "clarifying"
                    else:
                        # Already asked for clarification, go back to idle
                        self.conversation_state = "idle"
            
            time.sleep(0.1)

if __name__ == "__main__":
    HermesJarvis().run()