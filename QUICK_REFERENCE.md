# Buddy Agent - Natural Language Voice Control for Windows
## Quick Reference

### 🚦 Getting Started
1. Double-click `run_buddy.bat` OR run `python buddy_assistant.py`
2. Wait for "[INDEX] Done: X apps" and "[HERMES] Hermes ready"
3. Say: **"Hey Buddy"** 
4. Wait for spoken response: "Listening!"
5. Speak your command naturally

### 🗣️ Wake Words (Say one of these)
- "Hey Buddy" (recommended)
- "Hey Hermes" 
- "Hey Jarvis"

### ✅ What You Can Say

**Applications & Folders:**
- "Hey Buddy, open file folder"        → Opens File Explorer
- "Hey Buddy, open downloads folder"   → Opens Downloads
- "Hey Buddy, open my documents"       → Opens Documents
- "Hey Buddy, open chrome"             → Opens Chrome browser
- "Hey Buddy, close spotify"           → Closes Spotify
- "Hey Buddy, open notepad"            → Opens Notepad

**Browser Control:**
- "Hey Buddy, open a new tab"          → Ctrl+T
- "Hey Buddy, close this tab"          → Ctrl+W
- "Hey Buddy, go to github.com"        → Navigates to GitHub
- "Hey Buddy, search for python"       → New tab + search
- "Hey Buddy, refresh the page"        → F5
- "Hey Buddy, open incognito"          → Ctrl+Shift+N
- "Hey Buddy, bookmark this page"      → Ctrl+D

**File Search:**
- "Hey Buddy, search for resume"       → Finds resume files
- "Hey Buddy, find a file called budget" → Finds budget files

**💬 Natural Language Examples:**
- "Hey Buddy, open file folder and open downloads folder"
- "Hey Buddy, open chrome and then search for python tutorials"
- "Hey Buddy, close spotify and open vlc"
- "Hey Buddy, open a new tab and search youtube"
- "Hey Buddy, open my pictures folder"

**🔗 Complex Chains (Buddy's Specialty):**
- "Hey Buddy, open file folder and open downloads folder and also open comet and open a new tab and search for youtube"
- "Hey Buddy, open chrome and search for python tutorials and open a new tab"
- "Hey Buddy, close spotify and open vlc and go to netflix.com"

### ⏱️ Session Behavior
- After "Hey Buddy": You have **8 seconds** to give commands
- Spoken confirmation: "Listening!" means ready for command
- Auto-returns to sleep after timeout
- Say "Hey Buddy" again to wake up

### 🔐 Safety First
Buddy ONLY has access to:
- ✅ Open/close applications  
- ✅ Browser control (tabs, search, navigate)
- ✅ Common folders (Desktop, Downloads, Documents, Pictures, Music, Videos)
- ❌ NO access to: files, system settings, keyboard, shutdown, volume, etc.

### 🛠️ If Something's Not Working
**No response to wake word:**
- Check microphone permissions in Windows Settings
- Ensure no other app is using the microphone exclusively
- Try restarting Buddy Agent

**Commands not understood:**
- Speak clearly at normal pace
- Try rephrasing (Buddy learns from context)
- Use exact wake words: "Hey Buddy"
- Check console for "[HEARD]" logs to see what was recognized

**Need to restart:**
- Close the console window and double-click run_buddy.bat again

### 📁 Files Location
- **Main app**: `Buddy Windows agent/buddy_assistant.py`
- **Launcher**: `Buddy Windows agent/run_buddy.bat` 
- **Config**: `Buddy Windows agent/config.json`

### 💡 Pro Tips
- Buddy understands polite words: "please", "could you", etc.
- Contextual references work: "close it" closes what you last opened
- Multi-app chains: "open x and y and z" executes all in sequence
- Error handling: Buddy speaks back when things go wrong

---

**You now have a natural voice assistant for your Windows PC!**
Just say "Hey Buddy" and tell it what you need - it understands conversational English and executes your commands safely and reliably.