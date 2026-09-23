#!/usr/bin/env python3
"""
Buddy Agent — Voice-Controlled Laptop Operator
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

# ── Conversational Personality ────────────────────────────
# Buddy speaks like a real person — varied, warm, natural.

RESPONSES = {
    "greeting": [
        "Hey there! What can I do for you?",
        "What's up? I'm all ears.",
        "Hi! I'm right here, what do you need?",
        "Hey! Good to hear from you. What's on your mind?",
        "Hello! Fire away, I'm ready.",
    ],
    "exit": [
        "Alright, take care! I'll be here if you need me.",
        "Goodbye! Don't be a stranger.",
        "See ya! Just call my name when you're back.",
        "Catch you later! Have a good one.",
        "Bye for now! I'll keep the lights on.",
    ],
    "error": [
        "Hmm, I didn't quite get that. Mind saying it again?",
        "Sorry, that went over my head. Could you try again?",
        "I missed that one. Can you rephrase?",
        "Not sure I followed. One more time?",
        "I'm drawing a blank on that. What did you mean?",
    ],
    "denied": [
        "Ah, that's outside my wheelhouse. I can help with apps, browser stuff, and folders though!",
        "Sorry, I'm not allowed to do that one. But I can open apps, search the web, or open your folders.",
        "I wish I could, but that's beyond my permissions. Anything else I can help with?",
    ],
    "wake": [
        "Yes?",
        "I'm here!",
        "What's up?",
        "Hey! What do you need?",
        "Right here. Go ahead.",
        "Listening!",
    ],
    "wake_with_command": [
        "On it!",
        "Got it, let me handle that.",
        "Sure thing!",
        "Right away.",
    ],
    "multi_done": [
        "All taken care of!",
        "Done and done.",
        "Everything's set.",
        "All sorted!",
    ],
    "session_timeout": [
        "Alright, I'll be on standby. Just say my name when you need me.",
        "Going quiet for now. Call me anytime!",
        "I'll be right here whenever you're ready.",
    ],
}

# ── Human-like response wrappers per action type ─────────
# These replace the robotic module return messages with natural speech.

SUCCESS_PHRASES = {
    "open_app": [
        "Opening {target} for you.",
        "Sure, firing up {target}.",
        "Launching {target} right now.",
        "{target} is coming right up.",
        "Here comes {target}.",
        "You got it, starting {target}.",
    ],
    "close_app": [
        "Closing {target}.",
        "Shutting {target} down.",
        "Done, {target} is closed.",
        "{target} is out of the way.",
        "Consider {target} closed.",
    ],
    "browser_search": [
        "Searching for {target} now.",
        "Let me look that up for you.",
        "On it, searching {target}.",
        "Looking up {target}.",
    ],
    "browser_new_tab": [
        "New tab opened.",
        "Here's a fresh tab for you.",
        "Got you a new tab.",
    ],
    "browser_close_tab": [
        "Tab closed.",
        "Gone, that tab's closed.",
        "Done, tab is out of here.",
    ],
    "browser_navigate": [
        "Taking you to {target}.",
        "Heading to {target} now.",
        "On our way to {target}.",
    ],
    "browser_back": [
        "Going back.",
        "Taking you back.",
        "Stepping back a page.",
    ],
    "browser_forward": [
        "Going forward.",
        "Moving ahead.",
    ],
    "browser_refresh": [
        "Refreshing the page.",
        "Page refreshed.",
        "Here, nice and fresh.",
    ],
    "browser_incognito": [
        "Opening a private window for you.",
        "Incognito mode, nice and private.",
        "Here's your incognito window.",
    ],
    "browser_next_tab": [
        "Switched to the next tab.",
        "Moving to the next one.",
        "Here's your next tab.",
    ],
    "browser_prev_tab": [
        "Switched to the previous tab.",
        "Going back a tab.",
    ],
    "browser_zoom_in": ["Zoomed in.", "Bigger? You got it."],
    "browser_zoom_out": ["Zoomed out.", "Made it smaller."],
    "browser_scroll_down": ["Scrolling down.", "Going down."],
    "browser_scroll_up": ["Scrolling up.", "Going back up."],
    "browser_bookmark": ["Page bookmarked!", "Saved that bookmark."],
    "browser_history": ["Here's your history.", "Opening your browsing history."],
    "browser_downloads": ["Opening your downloads.", "Here are your downloads."],
    "browser_find": ["Find bar is open.", "Here, search away."],
    "file_open": [
        "Opening your {target} folder.",
        "Here's your {target}.",
        "Pulling up {target} for you.",
    ],
    "file_search": [
        "Let me look through your files.",
        "Searching your folders now.",
    ],
}

FAILURE_PHRASES = [
    "Hmm, I ran into a problem with that.",
    "That didn't quite work. Want me to try again?",
    "I had some trouble with that one.",
    "Oops, something went wrong there.",
    "I couldn't quite pull that off.",
]


def humanize(intent, target, ok, raw_msg):
    """Turn a raw module response into a natural, human-like message."""
    if not ok:
        # For failures, use the raw message if it's informative, else a generic one
        if raw_msg and len(raw_msg) > 10:
            return raw_msg
        return random.choice(FAILURE_PHRASES)

    # For successes, pick a personality-rich template
    templates = SUCCESS_PHRASES.get(intent)
    if templates:
        phrase = random.choice(templates)
        # Fill in {target} if present
        display_target = target.capitalize() if target else "that"
        return phrase.format(target=display_target)

    # Fallback: use raw message or generic
    if raw_msg:
        return raw_msg
    return random.choice(["Done.", "All set.", "You got it."])


class BuddyAgent:
    """Buddy Agent — Voice-Controlled Laptop Operator."""
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
        print(f"[BUDDY] {text}")
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
        Returns (success, human_response).
        """
        intent = cmd.intent
        target = cmd.target

        # ── Exit / Greeting (direct personality) ─────────────
        if intent == "exit":
            self.speak(random.choice(RESPONSES["exit"]))
            self.running = False
            return True, ""

        if intent == "greeting":
            return True, random.choice(RESPONSES["greeting"])

        # ── Route to module, then humanize the response ──────
        ok, raw_msg = False, ""

        # Browser
        if intent == "browser_search":
            ok, raw_msg = browser_control.search(target)
        elif intent == "browser_new_tab":
            ok, raw_msg = browser_control.new_tab()
        elif intent == "browser_close_tab":
            ok, raw_msg = browser_control.close_tab()
        elif intent == "browser_next_tab":
            ok, raw_msg = browser_control.next_tab()
        elif intent == "browser_prev_tab":
            ok, raw_msg = browser_control.prev_tab()
        elif intent == "browser_navigate":
            ok, raw_msg = browser_control.navigate(target)
        elif intent == "browser_back":
            ok, raw_msg = browser_control.go_back()
        elif intent == "browser_forward":
            ok, raw_msg = browser_control.go_forward()
        elif intent == "browser_refresh":
            ok, raw_msg = browser_control.refresh()
        elif intent == "browser_incognito":
            ok, raw_msg = browser_control.open_incognito()
        elif intent == "browser_zoom_in":
            ok, raw_msg = browser_control.zoom_in()
        elif intent == "browser_zoom_out":
            ok, raw_msg = browser_control.zoom_out()
        elif intent == "browser_find":
            ok, raw_msg = browser_control.find_on_page(target)
        elif intent == "browser_bookmark":
            ok, raw_msg = browser_control.bookmark()
        elif intent == "browser_history":
            ok, raw_msg = browser_control.open_history()
        elif intent == "browser_downloads":
            ok, raw_msg = browser_control.open_downloads()
        elif intent == "browser_scroll_down":
            ok, raw_msg = browser_control.scroll_down()
        elif intent == "browser_scroll_up":
            ok, raw_msg = browser_control.scroll_up()

        # Folders
        elif intent == "file_open":
            ok, raw_msg = file_control.open_folder(target)
        elif intent == "file_search":
            ok, raw_msg = file_control.search_files(target)
            # Search results are already descriptive — use them directly
            return ok, raw_msg

        # Apps
        elif intent == "close_app":
            ok, raw_msg = self.app_ctrl.close_app(target)
            if ok and target:
                self.context["last_closed"].append(target)
                self.context["last_closed"] = self.context["last_closed"][-5:]
        elif intent == "open_app":
            ok, raw_msg = self.app_ctrl.open_app(target)
            if ok and target:
                self.context["last_opened"].append(target)
                self.context["last_opened"] = self.context["last_opened"][-5:]

        # Unknown → DENIED
        else:
            return False, random.choice(RESPONSES["denied"])

        # Convert raw response into human-like speech
        return ok, humanize(intent, target, ok, raw_msg)

    # ── Main Loop ─────────────────────────────────────────────

    def run(self):
        """Main execution loop."""
        print("""
        +---------------------------------------------------------------+
        |                                                               |
        |              B U D D Y   A G E N T   O N L I N E             |
        |              Voice-Controlled Laptop Operator                 |
        |                                                               |
        |  Say "Hey Buddy" to wake me up.                              |
        |  Then just speak naturally — I'll handle the rest.           |
        |                                                               |
        |  I can:                                                       |
        |   - Open and close any application                            |
        |   - Control your browser (tabs, search, navigate)             |
        |   - Open common folders (Desktop, Downloads, etc.)            |
        |   - Search for files by name                                  |
        |                                                               |
        |  Examples:                                                    |
        |   "Hey Buddy, open Chrome"                                    |
        |   "Hey Buddy, open a new tab and search YouTube"              |
        |   "Hey Buddy, close Spotify"                                  |
        |   "Hey Buddy, open my downloads folder"                       |
        |   "Hey Buddy, go to github.com"                               |
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
                    # Wake word + command together — acknowledge then execute
                    print(f"[CMD] '{remaining}'")
                    commands = nlp_engine.parse(remaining, self.context)
                    if commands:
                        self._execute_commands(commands)
                    else:
                        self.speak(random.choice(RESPONSES["wake"]))
                else:
                    self.speak(random.choice(RESPONSES["wake"]))
                continue

            # If in active session, process commands directly
            if self.in_session:
                if time.time() - self.session_start > SESSION_TIMEOUT:
                    self.in_session = False
                    print("[SESSION] Timed out")
                    self.speak(random.choice(RESPONSES["session_timeout"]))
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
        """Execute a list of parsed commands with natural responses."""
        for cmd in commands:
            ok, response = self.dispatch(cmd)
            if not self.running:
                return
            if response:
                self.speak(response)
            if len(commands) > 1:
                time.sleep(0.3)

        if len(commands) > 1:
            self.speak(random.choice(RESPONSES["multi_done"]))


# Backward compatibility alias
Hermes = BuddyAgent


# ── Test Mode ─────────────────────────────────────────────────

def run_test_mode():
    """Run NLP parser tests without microphone."""
    print("\n" + "=" * 60)
    print("  BUDDY AGENT - NLP Parser Test Mode (Secured)")
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
        BuddyAgent().run()