# 🚀 Voice Assistant Project — Re-start Prompt

**Copy and paste this entire prompt into a new session to rebuild your voice-activated Jarvis-style assistant:**

---

## **PROJECT: Buddy Agent (Voice-Controlled Laptop Assistant)**

### **🎯 GOAL**
Build a voice assistant that responds to "Hey Buddy" (or "Hey Hermes", "Hey Jarvis") and can:
- Open/close ANY application on the system (not just hardcoded apps)
- Open websites directly ("open gmail.com", "go to github")
- Control browser tabs (new tab, close tab, search)
- Open system folders (Downloads, Desktop, Documents)
- Understand natural language commands like a human would
- Provide conversational voice feedback ("Opening Chrome for you", "Consider it done")
- Support multiple actions in one command ("open Spotify and Chrome")

### **🔧 TECH STACK & REQUIREMENTS**
```python
# Core dependencies (install via pip):
pip install SpeechRecognition pyttsx3 pyaudio

# Python: 3.10+ (Windows 10/11)
# Speech Recognition: Google STT API (online, requires internet)
# TTS: pyttsx3 (offline, uses Windows SAPI5 voices)
# OS: subprocess.Popen, os.startfile for app launching
```

### **📁 FILE STRUCTURE**
```
HermesVoiceAssistant/
├── buddy_assistant.py           # MAIN ENTRY POINT
├── modules/
│   ├── nlp_engine.py           # Natural language parser
│   ├── app_control.py          # App open/close logic
│   ├── browser_control.py      # Browser tab management
│   └── file_control.py         # File/folder operations
├── run_buddy.bat              # Double-click launcher
├── config.json                # Wake words, timeouts
├── README.md                  # Documentation
└── PROJECT_HISTORY.md         # This file
```

### **🧠 KEY IMPLEMENTATIONS TO BUILD**

#### **1. Wake Word Detection (in buddy_assistant.py)**
- Listen continuously for "hey buddy", "hey hermes", "hey jarvis"
- Respond with conversational "Yes?", "I'm here!", "What's up?"
- 30-second session window (extendable to 60s)
- Background: microphone index 17 (adjust as needed)

#### **2. Natural Language Parser (modules/nlp_engine.py)**
```python
# Understands phrases like:
- "Can you open Spotify please?" → open_app("spotify")
- "I need to check my email" → open_app("gmail")
- "Close Chrome and open Firefox" → [close_app, open_app]
- "Play some music" → open_app("spotify")
- "Open it again" → use context["last_opened"]
- "Open my downloads folder" → file_control.open_folder("downloads")
```

#### **3. Application Control (modules/app_control.py)**
```python
# Safety: CRITICAL_PROCESS_BLACKLIST = {"system", "csrss", "svchost", "explorer", ...}
# Find ANY app via:
# 1. Registry App Paths
# 2. Start Menu shortcuts
# 3. Program Files directories
# 4. PATH environment variable

# Key function signatures:
find_app(query: str) -> (path, display_name)
open_app(target: str) -> (success, message)
close_app(target: str) -> (success, message)
```

#### **4. Browser Control (modules/browser_control.py)**
```python
# Use Selenium or direct keyboard commands for:
- new_tab()
- close_tab()
- go_back() / go_forward()
- search(query) → open new tab + search
- navigate(url)
- zoom_in(), zoom_out()
```

#### **5. File Control (modules/file_control.py)**
```python
# Support natural phrases:
- "my downloads" → ~/Downloads
- "open documents folder" → ~/Documents
- "search for invoice.pdf" → search files
```

### **🗣️ CONVERSATIONAL RESPONSES**
```python
OPEN_PHRASES = [
    "Opening {target} for you",
    "On it - launching {target}",
    "Consider it done",
    "You got it",
    "{target} is coming right up"
]

CLOSE_PHRASES = [
    "Closing {target}",
    "Shutting down {target}",
    "Done, {target} is closed"
]

ERROR_PHRASES = [
    "Hmm, I didn't catch that",
    "Let me try again",
    "What did you say?"
]
```

### **🚨 SAFETY REQUIREMENTS**
1. Never allow closing critical Windows processes:
   - explorer.exe, csrss.exe, svchost.exe, system processes
2. Handle "close file explorer" → BLOCK (shouldn't kill desktop)
3. Handle "open file explorer" → ALLOW (launching is safe)
4. All app openings go through fuzzy matching + safety checks

### **📝 QUICK START COMMANDS**
```bash
# 1. Create project structure
mkdir HermesVoiceAssistant/modules

# 2. Install dependencies
pip install SpeechRecognition pyttsx3 pyaudio

# 3. Create files and copy implementations
# 4. Double-click run_buddy.bat
# 5. Say "Hey Buddy, open Spotify"
```

### **✅ SUCCESS VERIFICATION**
Test these voice commands:
1. "Hey Buddy" → should respond "Yes?"
2. "Hey Buddy, open Chrome" → Chrome opens
3. "Hey Buddy, open gmail.com" → Browser opens Gmail
4. "Hey Buddy, open my downloads folder" → Downloads opens
5. "Hey Buddy, close this" → Should ask what they mean
6. "Hey Buddy, open Spotify and Chrome" → Both open
7. "Hey Buddy, exit" → Should say goodbye

### **📚 KEY LESSONS LEARNED**
1. Use background threads for app indexing (don't block startup)
2. Cache the app index to JSON for faster subsequent starts
3. Remove "the" and polite words before parsing
4. Track "last_opened" context for pronoun resolution
5. Expand "open X and Y" to detect multiple commands
6. Always close TTS engine threads gracefully

---

**END OF PROMPT - Save this file as REBUILD_PROMPT.md and copy it when starting fresh**