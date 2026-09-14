# Hermes Voice Assistant — Comet Browser & Desktop Control

Voice-activated assistant with **mandatory wake word** ("Hey Buddy"), **Comet as default browser**, **fuzzy app matching**, and **real Comet tab control**.

## 🚀 Quick Start

1. Open `Desktop\HermesVoiceAssistant`
2. Double-click **`run_hermes.bat`**
3. Wait for: `Hermes ready` + `Waiting for 'Hey Buddy'...`
4. Speak commands!

---

## 🗣️ Commands (Say "Hey Buddy" first, then your command)

### Open Apps (fuzzy matching — "anti gravity" finds anti-gravity.exe)
```
Hey Buddy, open Spotify
Hey Buddy, open File Explorer and open Spotify and open Notepad
Hey Buddy, open anti gravity
Hey Buddy, open Wispr Flow
Hey Buddy, open Comet
Hey Buddy, open Chrome
Hey Buddy, open VS Code
Hey Buddy, open Settings
```

### Close Apps
```
Hey Buddy, close Spotify
Hey Buddy, close Notepad and close Chrome
Hey Buddy, kill Discord
```

### Open Websites (default: Comet browser)
```
Hey Buddy, open Indian passport website
Hey Buddy, open Indian passport website on Comet
Hey Buddy, open Google on Chrome
Hey Buddy, open YouTube in Edge
Hey Buddy, open GitHub
Hey Buddy, open Gmail and GitHub
```

### Comet Browser Tabs (real tab control via keystrokes)
```
Hey Buddy, new tab
Hey Buddy, open new tab
Hey Buddy, close tab
Hey Buddy, close the tab
Hey Buddy, switch tab
Hey Buddy, next tab
Hey Buddy, previous tab
```

### Folders
```
Hey Buddy, open Downloads
Hey Buddy, open Desktop
Hey Buddy, open Documents
```

### Exit
```
Hey Buddy, stop
Hey Buddy, goodbye
Hey Buddy, quit
```

---

## ⚡ Key Features

| Feature | Details |
|---------|---------|
| **Wake Word Required** | Only activates on "Hey Buddy" — ignores everything else |
| **Default Browser** | Comet (not Chrome). Say "on Chrome" to override |
| **Fuzzy App Matching** | "anti gravity" → finds `anti-gravity.exe`, `antigravity.exe`, `Anti Gravity.exe` |
| **Multi-Command** | "open X and Y and Z" executes all in sequence |
| **Real Tab Control** | Ctrl+T / Ctrl+W / Ctrl+Tab in Comet |
| **Auto-Sleep** | Returns to listening for "Hey Buddy" after each command batch |
| **Privacy** | Terminal logs only — nothing saved to disk |

---

## 🎯 Examples

```
You:  Hey Buddy, open Spotify and open File Explorer
→ Opens Spotify, then File Explorer
→ Says: "Opening Spotify", "Opening File Explorer"
→ Returns to sleep

You:  Hey Buddy, open Indian passport website on Comet
→ Opens passportindia.gov.in in new Comet tab
→ Says: "Opening Indian passport website"

You:  Hey Buddy, new tab
→ Ctrl+T in Comet
→ Says: "New tab"

You:  Hey Buddy, close tab
→ Ctrl+W in Comet
→ Says: "Tab closed"

You:  Hey Buddy, switch tab
→ Ctrl+Tab in Comet
→ Says: "Switched tab next"
```

---

## 🔧 Troubleshooting

| Issue | Fix |
|-------|-----|
| "Hey Buddy" not heard | Speak clearly, closer to mic. Check Energy threshold (should be 40-120). |
| App not found | App name spoken differently? Try exact name or check it's installed. |
| Comet not opening | Ensure Comet is installed. Default path: `%LOCALAPPDATA%\Comet\comet.exe` |
| Website wrong | Say "on Chrome" or "in Edge" to override default Comet. |

---

## 📁 Files

```
Desktop/HermesVoiceAssistant/
├── hermes_assistant.py   # Main script
├── run_hermes.bat        # Launcher (uses Hermes venv Python)
└── README_HERMES_ASSISTANT.md
```

Run: Double-click `run_hermes.bat` or run in terminal:
```cmd
"C:\Users\aditi\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" hermes_assistant.py
```