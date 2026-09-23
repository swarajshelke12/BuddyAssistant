#!/usr/bin/env python3
"""
Hermes Voice Assistant — Secured Laptop Agent
PERMISSIONS (strict):
  - Open / close applications
  - Browser control (tabs, search, navigate, bookmarks)
  - Open common folders (Desktop, Downloads, Documents, Pictures, Music, Videos)
NO access to: files, system settings, keyboard automation, window management,
              volume, brightness, screenshots, shutdown, or any destructive operations.
"""

import os, time, re, random
import speech_recognition as sr
import pyttsx3

from modules import nlp_engine
from modules.app_control import AppController
from modules import browser_control
from modules import file_control

# ── Configuration ────────────────────────────────────────
WAKE_WORDS = ["hey buddy", "hey hermes", "hey jarvis"]
SESSION_TIMEOUT = 60.0  # seconds before going back to standby

# ── Conversational responses ─────────────────────────────
RESPONSES = {
    "greeting": [
        "Hello! How can I help?",
        "Hey! What do you need?",
        "Hi! I'm ready.",
        "What's up? How can I assist?",
    ],
    "exit": [
        "Goodbye! Have a great day.",
        "See you later!",
        "Bye! Call me when you need me.",
    ],
    "error": [
        "I didn't quite catch that. Could you try again?",
        "Hmm, I'm not sure what you mean.",
        "Could you rephrase that?",
        "I didn't understand. Try again?",
    ],
    "denied": [
        "Sorry, I don't have permission to do that.",
        "That's outside what I'm allowed to do.",
        "I can only open and close apps, control your browser, and open common folders.",
    ],
}


class Hermes:
    def __init__(self):
        # Speech
        self.rec = sr.Recognizer()
        self.mic = sr.Microphone(device_index=17)
        self.tts = pyttsx3.init()
        self._setup_tts()

        # Modules
        self.app_ctrl = AppController()

        # State
        self.running = True
        self.in_session = False
        self.session_start = 0
        self.context = {
            "last_opened": [],
            "last_closed": [],
        }

    def _setup_tts(self):
        """Configure text-to-speech."""
        voices = self.tts.getProperty('voices')
        if voices:
            for voice in voices:
                if any(n in voice.name.lower() for n in ["female", "zira", "hazel"]):
                    self.tts.setProperty('voice', voice.id)
                    break
        self.tts.setProperty('rate', 180)
        self.tts.setProperty('volume', 0.9)

    def speak(self, text):
        """Speak text aloud."""
        print(f"[HERMES] {text}")
        try:
            self.tts.say(text)
            self.tts.runAndWait()
        except Exception:
            pass

    def listen(self):
        """Listen once, return text or None."""
        try:
            with self.mic as source:
                self.rec.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.rec.listen(source, timeout=2.0, phrase_time_limit=10.0)
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

    def detect_wake_word(self, text):
        """Check if wake word is in text. Returns (detected, remaining_text)."""
        if not text:
            return False, None
        tl = text.lower().strip()
        for wake in WAKE_WORDS:
            if wake in tl:
                remaining = tl.replace(wake, "", 1).strip()
                remaining = re.sub(r'\s+', ' ', remaining).strip()
                return True, remaining
        return False, None

    # ── Command Dispatcher (locked down) ──────────────────────

    def dispatch(self, cmd):
        """Route a Command to the correct handler.
        ONLY allows: apps, browser, common folders.
        """
        intent = cmd.intent
        target = cmd.target

        # ── Exit / Greeting ──────────────────────────────────
        if intent == "exit":
            self.speak(random.choice(RESPONSES["exit"]))
            self.running = False
            return True, ""

        if intent == "greeting":
            return True, random.choice(RESPONSES["greeting"])

        # ── Browser (ALLOWED) ────────────────────────────────
        if intent == "browser_search":
            return browser_control.search(target)
        if intent == "browser_new_tab":
            return browser_control.new_tab()
        if intent == "browser_close_tab":
            return browser_control.close_tab()
        if intent == "browser_next_tab":
            return browser_control.next_tab()
        if intent == "browser_prev_tab":
            return browser_control.prev_tab()
        if intent == "browser_navigate":
            return browser_control.navigate(target)
        if intent == "browser_back":
            return browser_control.go_back()
        if intent == "browser_forward":
            return browser_control.go_forward()
        if intent == "browser_refresh":
            return browser_control.refresh()
        if intent == "browser_incognito":
            return browser_control.open_incognito()
        if intent == "browser_zoom_in":
            return browser_control.zoom_in()
        if intent == "browser_zoom_out":
            return browser_control.zoom_out()
        if intent == "browser_find":
            return browser_control.find_on_page(target)
        if intent == "browser_bookmark":
            return browser_control.bookmark()
        if intent == "browser_history":
            return browser_control.open_history()
        if intent == "browser_downloads":
            return browser_control.open_downloads()
        if intent == "browser_scroll_down":
            return browser_control.scroll_down()
        if intent == "browser_scroll_up":
            return browser_control.scroll_up()

        # ── Open common folders (ALLOWED — whitelisted only) ─
        if intent == "file_open":
            return file_control.open_folder(target)

        # ── Search files (ALLOWED — read-only, common folders) ─
        if intent == "file_search":
            return file_control.search_files(target)

        # ── Open/close apps (ALLOWED) ────────────────────────
        if intent == "close_app":
            ok, msg = self.app_ctrl.close_app(target)
            if ok and target:
                self.context["last_closed"].append(target)
                self.context["last_closed"] = self.context["last_closed"][-5:]
            return ok, msg

        if intent == "open_app":
            ok, msg = self.app_ctrl.open_app(target)
            if ok and target:
                self.context["last_opened"].append(target)
                self.context["last_opened"] = self.context["last_opened"][-5:]
            return ok, msg

        # ── Everything else: DENIED ──────────────────────────
        return False, random.choice(RESPONSES["denied"])

    # ── Main Loop ─────────────────────────────────────────────

    def run(self):
        """Main execution loop."""
        print("""
        +---------------------------------------------------------------+
        |                                                               |
        |              H E R M E S   A C T I V A T E D                 |
        |              Secured Laptop Control Agent                     |
        |                                                               |
        |  Say "Hey Buddy", "Hey Hermes", or "Hey Jarvis"              |
        |  Then speak naturally.                                        |
        |                                                               |
        |  I can:                                                       |
        |   - Open and close any application                            |
        |   - Control your browser (tabs, search, navigate)             |
        |   - Open common folders (Desktop, Downloads, etc.)            |
        |                                                               |
        |  Examples:                                                    |
        |   "Open Chrome"                                               |
        |   "Open a new tab and search YouTube"                         |
        |   "Close Spotify"                                             |
        |   "Open my downloads folder"                                  |
        |   "Go to github.com"                                          |
        |                                                               |
        +---------------------------------------------------------------+
        """)

        print("\nListening for wake word...\n")

        while self.running:
            txt = self.listen()
            if not txt:
                time.sleep(0.1)
                continue

            print(f"[HEARD] '{txt}'")

            # Check for wake word
            is_wake, remaining = self.detect_wake_word(txt)

            if is_wake:
                self.in_session = True
                self.session_start = time.time()

                if remaining:
                    print(f"[CMD] '{remaining}'")
                    commands = nlp_engine.parse(remaining, self.context)
                    if commands:
                        self._execute_commands(commands)
                    else:
                        self.speak("Yes? I'm listening.")
                else:
                    self.speak("Yes?")
                continue

            # If in active session, process commands directly
            if self.in_session:
                if time.time() - self.session_start > SESSION_TIMEOUT:
                    self.in_session = False
                    print("[SESSION] Timed out")
                    self.speak("Going back to standby. Call me when you need me.")
                    continue

                print(f"[CMD] '{txt}'")
                commands = nlp_engine.parse(txt, self.context)
                if commands:
                    self._execute_commands(commands)
                    self.session_start = time.time()
                else:
                    self.speak(random.choice(RESPONSES["error"]))

            time.sleep(0.1)

    def _execute_commands(self, commands):
        """Execute a list of parsed commands."""
        for cmd in commands:
            ok, response = self.dispatch(cmd)
            if not self.running:
                return
            if response:
                self.speak(response)
            if len(commands) > 1:
                time.sleep(0.3)

        if len(commands) > 1:
            self.speak("All done.")


# ── Test Mode ─────────────────────────────────────────────────

def run_test_mode():
    """Run NLP parser tests without microphone."""
    print("\n" + "=" * 60)
    print("  HERMES - NLP Parser Test Mode (Secured)")
    print("=" * 60 + "\n")
    success = nlp_engine.test_parser()
    print("\n" + "=" * 60)
    if success:
        print("  All tests passed!")
    else:
        print("  Some tests failed. Check output above.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        run_test_mode()
    else:
        Hermes().run()