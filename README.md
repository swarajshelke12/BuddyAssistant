<div align="center">

<!-- Animated title using SVG -->
<a href="https://github.com/swarajshelke12/HermesVoiceAgent">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=36&duration=3000&pause=1000&color=6C63FF&center=true&vCenter=true&width=600&lines=Hey+Buddy%2C+open+Chrome.;Hey+Buddy%2C+search+YouTube.;Hey+Buddy%2C+close+Spotify.;Meet+Hermes." alt="Typing animation" />
</a>

<br />

<img src="https://readme-typing-svg.demolab.com?font=Inter&weight=400&size=18&duration=4000&pause=1000&color=A0A0B0&center=true&vCenter=true&width=700&lines=A+voice+agent+that+runs+your+laptop+%E2%80%94+not+just+an+assistant%2C+a+real+operator." alt="Subtitle" />

<br /><br />

<!-- Badges -->
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Build](https://img.shields.io/badge/Build-Passing-22C55E?style=for-the-badge&logo=checkmarx&logoColor=white)
![Privacy](https://img.shields.io/badge/100%25-Local%20%26%20Private-6C63FF?style=for-the-badge&logo=shield&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge)

<br />

**[Quick Start](#-quick-start)** · **[What It Can Do](#-what-hermes-can-do)** · **[How It Works](#-how-it-works)** · **[Voice Commands](#-voice-command-reference)** · **[Architecture](#-architecture)**

</div>

---

<br />

## ⚡ What Is Hermes?

> *"Hey Buddy, open Chrome and search YouTube."*

That's it. That's the whole idea.

**Hermes** is a voice-activated laptop operator for Windows. Not just a smart speaker shortcut, not just a macro runner — a real agent that **understands natural English**, figures out what you mean, and **actually does it**. Open apps. Control your browser. Search your files. Switch tabs. All hands-free, all offline, all private.

Think **J.A.R.V.I.S.** — minus the Iron Man suit, plus your actual laptop.

<br />

---

## ✨ What Hermes Can Do

<br />

<div align="center">

| 🎯 Capability | 💬 Example |
|:---|:---|
| **Launch any app** | *"Open Discord"*, *"Start VS Code"*, *"Launch Spotify"* |
| **Close any app** | *"Close Chrome"*, *"Quit Notepad"* |
| **Browser tabs** | *"Open a new tab and search YouTube"*, *"Close this tab"* |
| **Web search** | *"Search for Python tutorials"*, *"Google the weather"* |
| **Navigate anywhere** | *"Go to github.com"*, *"Open YouTube"*, *"Visit Reddit"* |
| **Browser controls** | *"Go back"*, *"Refresh the page"*, *"Open incognito"* |
| **Open folders** | *"Open my Downloads"*, *"Show my Desktop folder"* |
| **Search files** | *"Find a file called resume"*, *"Search for budget"* |
| **Chain commands** | *"Open Chrome and search YouTube"* all in one breath |
| **Context awareness** | *"Close it"* → closes what you just opened |

</div>

<br />

---

## 🔐 Built With Safety First

Hermes is **permission-locked by design**. It only has access to exactly three things:

```
✅  Open and close applications
✅  Control your browser  (tabs, search, navigate)
✅  Open common folders   (Desktop, Downloads, Documents, Pictures, Music, Videos)
```

That's the full list. There's no keyboard snooping, no system command execution, no file modification, no screenshots, no shutdown commands, no volume changes — **nothing else**. Any request outside this boundary is politely declined.

<br />

> [!NOTE]
> The unused modules (`system_control`, `window_control`, `keyboard_control`) aren't just disabled — they were **deleted from disk** entirely so they can't be accidentally re-enabled.

<br />

---

## 🚀 Quick Start

### Prerequisites

- **OS**: Windows 10 or 11 (64-bit)
- **Python**: 3.10 or higher
- **Microphone**: Any working mic, configured in Windows Sound settings
- **Internet**: Required for speech recognition (Google STT) — everything else runs offline

<br />

### 1 · Clone the repo

```bash
git clone https://github.com/swarajshelke12/HermesVoiceAgent.git
cd HermesVoiceAgent
```

### 2 · Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3 · Install dependencies

```bash
pip install SpeechRecognition pyttsx3 pyaudio pyautogui pyperclip
```

### 4 · Run it

```bash
# Option A — Python directly
python hermes_assistant.py

# Option B — Double-click the launcher
run_hermes.bat
```

<br />

Once it starts, you'll see the activation banner and hear a startup chime. Then:

```
Say → "Hey Buddy"   (or "Hey Hermes" or "Hey Jarvis")
Wait → "Yes?" / "I'm here!" / "What's up?"
Say → your command
```

<br />

---

## 🗣️ Voice Command Reference

> Wake Hermes first: **"Hey Buddy"**, **"Hey Hermes"**, or **"Hey Jarvis"**

<br />

### 📱 Apps

```
"Open Chrome"
"Launch Spotify"
"Start VS Code"
"Close Discord"
"Quit Notepad"
"Close it"              ← closes whatever you last opened
"Open it again"         ← reopens whatever you last opened
```

<br />

### 🌐 Browser

```
"Open a new tab"
"Open a new tab and search YouTube"
"Search for Python tutorials"
"Go to github.com"
"Close this tab"
"Next tab"
"Previous tab"
"Go back"
"Go forward"
"Refresh the page"
"Open incognito"
"Bookmark this page"
"Zoom in" / "Zoom out"
"Scroll down" / "Scroll up"
"Open browser history"
```

<br />

### 📁 Folders

```
"Open my Downloads"
"Open my Documents"
"Open the Desktop folder"
"Show my Pictures"
"Open my Music"
"Open Videos"
```

<br />

### 🔍 File Search

```
"Search for resume"
"Find a file called budget"
"Look for presentation"
"Do I have a file called notes?"
```

<br />

### 💬 Conversation

```
"Hello"  /  "Hey"  /  "Hi"        ← Hermes greets you back
"Goodbye"  /  "Bye"  /  "Stop"    ← ends the session
```

<br />

### 🔗 Chained Commands *(the cool part)*

```
"Open Chrome and search YouTube"
"Close Spotify and open VLC"
"Open a new tab and go to reddit.com"
"Can you please open Discord"          ← polite words stripped automatically
"I want to launch Spotify"             ← natural phrasing understood
```

<br />

---

## ⚙️ How It Works

<br />

```
You speak
    ↓
Wake word detection  ("Hey Buddy" / "Hey Hermes" / "Hey Jarvis")
    ↓
Google Speech-to-Text (en-IN → en fallback)
    ↓
NLP Engine  (regex intent matching, compound command splitting, context resolution)
    ↓
Dispatcher  (routes to the right module)
    ↓
         ┌──────────────┬─────────────────┬─────────────────┐
         ▼              ▼                 ▼                 ▼
    App Control    Browser Control   File Control     Denied ✗
    (open/close)   (tabs, search,    (folders only,
                    navigate)         read-only)
         └──────────────┴─────────────────┘
                        ↓
              humanize()  ← converts technical output to natural speech
                        ↓
              Hermes speaks back to you
```

<br />

The NLP engine uses **priority-ordered regex intent matching** — not an LLM, not a cloud API. Everything runs on your machine. The parser handles:

- **Polite words**: *"could you please"*, *"I want to"*, *"can you"* → stripped before parsing
- **Compound commands**: *"open Chrome and search YouTube"* → split into two separate commands
- **Contextual references**: *"close it"* → resolved to whatever you last opened
- **Fuzzy app matching**: registry + Start Menu shortcuts + filesystem scan + PATH fallback

<br />

---

## 🏗️ Architecture

```mermaid
flowchart TD
    A[🎙️ Microphone] --> B{Wake Word\nDetected?}
    B -- No --> A
    B -- Yes --> C[🔊 Hermes responds\n'Yes?' / 'I'm here!']
    C --> D[Active Listening\n60s session window]
    D --> E[🧠 NLP Engine\nIntent Matching + Compound Split]

    E --> F{Intent Type}

    F -->|open_app / close_app| G[App Control\nRegistry + Start Menu + Fuzzy Index]
    F -->|browser_*| H[Browser Control\nKeyboard Shortcuts]
    F -->|file_open| I[File Control\nWhitelisted Folders Only]
    F -->|file_search| I
    F -->|unknown| J[🚫 Permission Denied\nPolite refusal]

    G --> K[humanize\nNatural language response]
    H --> K
    I --> K
    J --> K

    K --> L[🔊 pyttsx3 TTS\nHermes speaks back]
    L --> D
```

<br />

---

## 📦 Project Structure

```
HermesVoiceAssistant/
│
├── hermes_assistant.py           ← Main entry point & orchestrator
│
├── modules/
│   ├── nlp_engine.py             ← Intent parser (regex-based, no LLM)
│   ├── app_control.py            ← Open/close apps, fuzzy index builder
│   ├── browser_control.py        ← Tab management, search, navigation
│   └── file_control.py           ← Whitelisted folder access + file search
│
├── hermes_assistant_config.json  ← Runtime configuration
├── run_hermes.bat                ← One-click launcher
├── BUILD.md                      ← Full build history & technical deep-dive
└── DEV_LOG.md                    ← Engineering changelog
```

<br />

---

## 🛠️ Dependencies

| Package | Purpose |
|:---|:---|
| `SpeechRecognition` | Microphone capture + Google STT |
| `pyttsx3` | Offline text-to-speech (SAPI5) |
| `pyaudio` | Audio stream input |
| `pyautogui` | Keyboard shortcuts for browser control |
| `pyperclip` | Clipboard-based text pasting (handles Unicode) |
| `psutil` | Process detection and management |
| `pywin32` | Windows registry access for app indexing |

<br />

---

## 🎨 Why "Hermes"?

In Greek mythology, **Hermes** is the messenger god — the one who carries words between worlds instantly, without being seen. That's exactly what this assistant does: it listens, understands, acts, and speaks back — all in a few hundred milliseconds, running quietly in the background.

No cloud dependency for the core engine. No data sent anywhere. Just you, your voice, and your laptop doing what you say.

<br />

---

## 👤 Author

<div align="center">

**Swaraj Shelke**
*Builder of things that should exist*

[![GitHub](https://img.shields.io/badge/GitHub-swarajshelke12-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/swarajshelke12)

<br />

*Built over ~3 days of iterative voice testing, debugging, and a lot of "Hey Buddy, open Chrome".*

</div>

<br />

---

## 📄 License

MIT — do whatever you want, just don't blame me if Hermes develops opinions.

---

<div align="center">

<br />

*If it made your laptop feel a little more like a spaceship, it worked.*

<br />

![Footer](https://capsule-render.vercel.app/api?type=waving&color=6C63FF&height=100&section=footer)

</div>