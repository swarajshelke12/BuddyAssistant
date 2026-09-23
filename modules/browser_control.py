"""
Hermes Voice Assistant — Browser Control
Handles: new tab, close tab, switch tabs, search, navigate, back/forward,
         refresh, incognito, zoom, find on page, bookmarks.
All operations use keyboard shortcuts (browser-agnostic: Chrome/Edge/Firefox).
"""

import time
import subprocess
import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


def _ensure_browser_focused():
    """Small delay to let browser come to foreground."""
    time.sleep(0.3)


def open_browser(browser=None):
    """Launch a browser. If browser is None, opens system default."""
    browsers = {
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "edge": "msedge.exe",
        "microsoft edge": "msedge.exe",
        "firefox": "firefox.exe",
        "mozilla firefox": "firefox.exe",
        "brave": "brave.exe",
        "opera": "opera.exe",
    }
    if browser:
        exe = browsers.get(browser.lower().strip())
        if exe:
            try:
                subprocess.Popen([exe])
                return True, f"Opening {browser}"
            except FileNotFoundError:
                # Try via start command
                try:
                    subprocess.Popen(["start", "", exe], shell=True)
                    return True, f"Opening {browser}"
                except Exception as e:
                    return False, f"Couldn't open {browser}: {e}"
    # Default: open system default browser
    try:
        subprocess.Popen(["start", "https://www.google.com"], shell=True)
        return True, "Opening your default browser"
    except Exception as e:
        return False, f"Couldn't open browser: {e}"


def new_tab():
    """Open a new browser tab (Ctrl+T)."""
    try:
        pyautogui.hotkey('ctrl', 't')
        time.sleep(0.3)
        return True, "New tab opened"
    except Exception as e:
        return False, f"Couldn't open new tab: {e}"


def close_tab():
    """Close the current browser tab (Ctrl+W)."""
    try:
        pyautogui.hotkey('ctrl', 'w')
        return True, "Tab closed"
    except Exception as e:
        return False, f"Couldn't close tab: {e}"


def next_tab():
    """Switch to the next tab (Ctrl+Tab)."""
    try:
        pyautogui.hotkey('ctrl', 'tab')
        return True, "Switched to next tab"
    except Exception as e:
        return False, f"Couldn't switch tab: {e}"


def prev_tab():
    """Switch to the previous tab (Ctrl+Shift+Tab)."""
    try:
        pyautogui.hotkey('ctrl', 'shift', 'tab')
        return True, "Switched to previous tab"
    except Exception as e:
        return False, f"Couldn't switch tab: {e}"


def search(query):
    """Open a new tab and search for a query.
    Opens new tab → focuses address bar → types query → presses Enter.
    """
    if not query:
        return False, "Nothing to search for."
    try:
        # Open new tab (this auto-focuses the address bar in most browsers)
        pyautogui.hotkey('ctrl', 't')
        time.sleep(0.5)
        # Type the search query
        import pyperclip
        pyperclip.copy(query)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)
        pyautogui.press('enter')
        return True, f"Searching for {query}"
    except Exception as e:
        return False, f"Couldn't search: {e}"


def navigate(url):
    """Navigate to a URL in the current tab.
    Focuses address bar (Ctrl+L) → types URL → presses Enter.
    """
    if not url:
        return False, "No URL to navigate to."
    # Auto-add https:// if missing
    if not url.startswith(("http://", "https://", "www.")):
        # Check if it looks like a domain
        if "." in url:
            url = "https://" + url
        else:
            # Treat as search query instead
            return search(url)
    if url.startswith("www."):
        url = "https://" + url
    try:
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.3)
        import pyperclip
        pyperclip.copy(url)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)
        pyautogui.press('enter')
        return True, f"Navigating to {url}"
    except Exception as e:
        return False, f"Couldn't navigate: {e}"


def go_back():
    """Go back in browser history (Alt+Left)."""
    try:
        pyautogui.hotkey('alt', 'left')
        return True, "Going back"
    except Exception as e:
        return False, f"Couldn't go back: {e}"


def go_forward():
    """Go forward in browser history (Alt+Right)."""
    try:
        pyautogui.hotkey('alt', 'right')
        return True, "Going forward"
    except Exception as e:
        return False, f"Couldn't go forward: {e}"


def refresh():
    """Refresh the current page (F5)."""
    try:
        pyautogui.press('f5')
        return True, "Page refreshed"
    except Exception as e:
        return False, f"Couldn't refresh: {e}"


def hard_refresh():
    """Hard refresh / clear cache refresh (Ctrl+Shift+R)."""
    try:
        pyautogui.hotkey('ctrl', 'shift', 'r')
        return True, "Hard refreshed"
    except Exception as e:
        return False, f"Couldn't hard refresh: {e}"


def open_incognito():
    """Open an incognito/private window (Ctrl+Shift+N)."""
    try:
        pyautogui.hotkey('ctrl', 'shift', 'n')
        time.sleep(0.5)
        return True, "Incognito window opened"
    except Exception as e:
        return False, f"Couldn't open incognito: {e}"


def zoom_in():
    """Zoom in (Ctrl+Plus)."""
    try:
        pyautogui.hotkey('ctrl', '+')
        return True, "Zoomed in"
    except Exception as e:
        return False, f"Couldn't zoom in: {e}"


def zoom_out():
    """Zoom out (Ctrl+Minus)."""
    try:
        pyautogui.hotkey('ctrl', '-')
        return True, "Zoomed out"
    except Exception as e:
        return False, f"Couldn't zoom out: {e}"


def zoom_reset():
    """Reset zoom to 100% (Ctrl+0)."""
    try:
        pyautogui.hotkey('ctrl', '0')
        return True, "Zoom reset"
    except Exception as e:
        return False, f"Couldn't reset zoom: {e}"


def find_on_page(text=None):
    """Open find bar (Ctrl+F), optionally type search text."""
    try:
        pyautogui.hotkey('ctrl', 'f')
        if text:
            time.sleep(0.3)
            import pyperclip
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
        return True, f"Find opened{f' — searching for {text}' if text else ''}"
    except Exception as e:
        return False, f"Couldn't open find: {e}"


def bookmark():
    """Bookmark the current page (Ctrl+D)."""
    try:
        pyautogui.hotkey('ctrl', 'd')
        return True, "Page bookmarked"
    except Exception as e:
        return False, f"Couldn't bookmark: {e}"


def open_downloads():
    """Open the downloads page (Ctrl+J)."""
    try:
        pyautogui.hotkey('ctrl', 'j')
        return True, "Downloads opened"
    except Exception as e:
        return False, f"Couldn't open downloads: {e}"


def open_history():
    """Open browser history (Ctrl+H)."""
    try:
        pyautogui.hotkey('ctrl', 'h')
        return True, "History opened"
    except Exception as e:
        return False, f"Couldn't open history: {e}"


def open_url_in_new_tab(url):
    """Open a URL in a new tab: new tab → navigate."""
    ok, msg = new_tab()
    if not ok:
        return ok, msg
    time.sleep(0.3)
    return navigate(url)


def scroll_down(amount=5):
    """Scroll down the page."""
    try:
        pyautogui.scroll(-amount)
        return True, "Scrolled down"
    except Exception as e:
        return False, f"Couldn't scroll: {e}"


def scroll_up(amount=5):
    """Scroll up the page."""
    try:
        pyautogui.scroll(amount)
        return True, "Scrolled up"
    except Exception as e:
        return False, f"Couldn't scroll: {e}"
