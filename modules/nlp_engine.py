"""
Hermes Voice Assistant — NLP Engine (Secured)
Parses conversational English into structured commands.
RESTRICTED to: open/close apps, browser control, open common folders.
No system control, no keyboard, no window management, no media, no file access.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Command:
    """A parsed voice command."""
    intent: str           # e.g., "open_app", "browser_search"
    target: str = ""      # e.g., "chrome", "youtube"
    params: dict = field(default_factory=dict)


# ── Intent Patterns (priority order — first match wins) ─────

INTENT_PATTERNS = [
    # ── EXIT ─────────────────────────────────────────────────
    ("exit", [
        r"^(goodbye|bye|see you|that's all|stop listening|exit|quit|go to sleep|shut down hermes|stop hermes)$",
    ], ["goodbye", "bye", "see you later", "that's all", "stop", "exit hermes",
        "quit hermes", "go to sleep"]),

    # ── GREETING ─────────────────────────────────────────────
    ("greeting", [
        r"^(hey|hi|hello|what's up|how are you|good morning|good afternoon|good evening|good night)$",
    ], ["hey", "hi", "hello", "what's up"]),

    # ── BROWSER: SEARCH ──────────────────────────────────────
    ("browser_search", [
        r"(?:search|look up|google|find|search for|look for|search up)\s+(?:for\s+)?(.+?)(?:\s+on\s+(?:google|the\s+web|the\s+internet|chrome|browser))?$",
        r"(?:google|bing)\s+(.+)",
        r"(?:open\s+(?:a\s+)?new\s+tab\s+and\s+search|search\s+(?:in\s+)?(?:a\s+)?new\s+tab\s+(?:for\s+)?)\s*(.+)",
        r"(?:what|who|where|when|why|how)\s+(?:is|are|was|were|do|does|did|can|could|would|should)\s+(.+)",
    ], []),

    # ── BROWSER: TAB CONTROL ────────────────────────────────
    ("browser_new_tab", [
        r"(?:open|create)\s+(?:a\s+)?new\s+tab",
        r"new\s+tab",
    ], ["new tab", "open tab", "create tab"]),

    ("browser_close_tab", [
        r"close\s+(?:this\s+|the\s+|current\s+)?tab",
    ], ["close tab", "close this tab"]),

    ("browser_next_tab", [
        r"(?:next|switch\s+to\s+(?:the\s+)?next|go\s+to\s+(?:the\s+)?next)\s+tab",
    ], ["next tab"]),

    ("browser_prev_tab", [
        r"(?:previous|prev|last|switch\s+to\s+(?:the\s+)?previous|go\s+to\s+(?:the\s+)?previous)\s+tab",
    ], ["previous tab", "prev tab", "last tab"]),

    ("browser_incognito", [
        r"(?:open|start|launch)\s+(?:an?\s+)?(?:incognito|private)\s*(?:window|tab|mode)?",
        r"incognito\s*(?:window|tab|mode)?",
        r"private\s+(?:window|tab|browsing|mode)",
    ], ["incognito", "private window", "private browsing"]),

    # ── BROWSER: NAVIGATION ──────────────────────────────────
    ("browser_back", [
        r"(?:go\s+)?back(?:\s+(?:a\s+)?page)?",
        r"previous\s+page",
    ], ["go back", "back"]),

    ("browser_forward", [
        r"(?:go\s+)?forward(?:\s+(?:a\s+)?page)?",
        r"next\s+page",
    ], ["go forward", "forward"]),

    ("browser_refresh", [
        r"refresh(?:\s+(?:the\s+)?page)?",
        r"reload(?:\s+(?:the\s+)?page)?",
    ], ["refresh", "reload"]),

    ("browser_navigate", [
        r"(?:go\s+to|navigate\s+to|visit|open)\s+((?:https?://|www\.)\S+)",
        r"(?:go\s+to|navigate\s+to|visit|open)\s+(\S+\.(?:com|org|net|io|dev|gov|edu|in|co)(?:/\S*)?)",
    ], []),

    ("browser_scroll_down", [
        r"scroll\s+down",
    ], ["scroll down"]),

    ("browser_scroll_up", [
        r"scroll\s+up",
    ], ["scroll up"]),

    ("browser_zoom_in", [
        r"zoom\s+in",
    ], ["zoom in"]),

    ("browser_zoom_out", [
        r"zoom\s+out",
    ], ["zoom out"]),

    ("browser_find", [
        r"find\s+(?:on\s+(?:this\s+)?page\s+)?(.+?)(?:\s+on\s+(?:this\s+)?page)?$",
    ], []),

    ("browser_bookmark", [
        r"bookmark\s+(?:this\s+)?(?:page)?",
        r"save\s+(?:this\s+)?(?:page|bookmark)",
    ], ["bookmark", "bookmark this page"]),

    ("browser_history", [
        r"(?:open|show)\s+(?:browser\s+)?history",
        r"browser\s+history",
    ], ["browser history", "history"]),

    ("browser_downloads", [
        r"(?:open|show)\s+(?:browser\s+)?downloads",
        r"browser\s+downloads",
    ], []),

    # ── FOLDER ACCESS (common folders only) ──────────────────
    ("file_open", [
        r"(?:open|show|go\s+to)\s+(?:my\s+)?(?:the\s+)?(desktop|downloads?|documents?|pictures?|photos?|music|videos?|home|user)\s*(?:folder|directory)?",
    ], []),

    ("file_search", [
        r"(?:search|look|find|locate)\s+(?:for\s+)?(?:a\s+)?(?:file\s+)?(?:called\s+|named\s+)?(.+?)(?:\s+(?:in|on|from)\s+(?:my\s+)?(?:files|folders|computer))?$",
        r"(?:do\s+i\s+have|is\s+there)\s+(?:a\s+)?(?:file\s+)?(?:called\s+|named\s+)?(.+?)(?:\s+(?:on|in)\s+(?:my\s+)?(?:computer|laptop|pc))?$",
    ], []),


    # ── APP CONTROL ──────────────────────────────────────────
    ("close_app", [
        r"close\s+(.+)",
        r"quit\s+(.+)",
        r"exit\s+(.+)",
        r"shut\s*(?:down)?\s+(.+)",
    ], []),

    ("open_app", [
        r"(?:open|launch|start|run)\s+(.+)",
        r"(.+)",  # Catch-all: assume "open <target>"
    ], []),
]


def _clean_text(text):
    """Remove polite words and filler."""
    if not text:
        return ""
    text = text.lower().strip()

    fillers = [
        "please", "could you", "can you", "would you", "will you",
        "i want to", "i need to", "i'd like to", "i would like to",
        "let's", "lets", "go ahead and", "just", "maybe", "possibly",
        "for me", "right now", "immediately", "quickly", "now",
        "hey buddy", "hey hermes", "hey jarvis",
    ]
    for filler in fillers:
        text = text.replace(filler, " ")

    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _split_compound(text):
    """Split compound commands on conjunctions.
    'Open Chrome and search YouTube' -> ['open chrome', 'search youtube']
    """
    parts = re.split(
        r'\s+(?:and\s+then|and\s+also|and\s+after\s+that|then|after\s+that|also)\s+',
        text
    )
    if len(parts) == 1:
        action_verbs = (
            "open", "close", "launch", "start", "search",
            "go", "navigate", "quit", "exit",
        )
        and_parts = re.split(r'\s+and\s+', text)
        if len(and_parts) > 1:
            valid_parts = [and_parts[0]]
            for part in and_parts[1:]:
                part_stripped = part.strip()
                if any(part_stripped.startswith(v) for v in action_verbs):
                    valid_parts.append(part_stripped)
                else:
                    valid_parts[-1] += " and " + part_stripped
            parts = valid_parts

    return [p.strip() for p in parts if p.strip()]


def _match_intent(text, context=None):
    """Match text against intent patterns. Returns Command or None."""
    text = text.strip()
    if not text:
        return None

    for intent, regexes, keywords in INTENT_PATTERNS:
        if text in keywords:
            return Command(intent=intent, target="")

        for pattern in regexes:
            m = re.match(pattern, text, re.IGNORECASE)
            if m:
                groups = m.groups()
                target = groups[0].strip() if groups else ""
                params = {}
                if len(groups) > 1 and groups[1]:
                    params["location"] = groups[1].strip()

                target = re.sub(r'^(the|a|an)\s+', '', target)
                target = re.sub(r'\s+(the|a|an)$', '', target)

                return Command(intent=intent, target=target, params=params)

    return None


def parse(text, context=None):
    """Parse natural language into a list of Command objects.
    
    Args:
        text: Raw speech-to-text output.
        context: Session context dict (last_opened, last_closed).
    
    Returns:
        List of Command objects.
    """
    if not text:
        return []

    cleaned = _clean_text(text)
    if not cleaned:
        return []

    # Contextual references
    if context:
        if cleaned in ["close it", "shut it down", "exit it", "quit it"]:
            last = context.get("last_opened", [])
            if last:
                return [Command(intent="close_app", target=last[-1])]

        if cleaned in ["open it again", "reopen it", "launch it again"]:
            last = context.get("last_opened", [])
            if last:
                return [Command(intent="open_app", target=last[-1])]

    parts = _split_compound(cleaned)
    commands = []
    for part in parts:
        cmd = _match_intent(part, context)
        if cmd:
            if not commands or commands[-1].intent != cmd.intent or \
               commands[-1].target != cmd.target:
                commands.append(cmd)

    return commands


# ── Testing ─────────────────────────────────────────────────

def test_parser():
    """Run test cases to verify the parser."""
    test_cases = [
        ("open chrome", ["open_app"]),
        ("close spotify", ["close_app"]),
        ("search youtube for python tutorials", ["browser_search"]),
        ("open a new tab and search youtube", ["browser_new_tab", "browser_search"]),
        ("close this tab", ["browser_close_tab"]),
        ("next tab", ["browser_next_tab"]),
        ("go back", ["browser_back"]),
        ("refresh the page", ["browser_refresh"]),
        ("open my downloads folder", ["file_open"]),
        ("goodbye", ["exit"]),
        ("hello", ["greeting"]),
        ("open chrome and then search youtube", ["open_app", "browser_search"]),
        ("close spotify and open vlc", ["close_app", "open_app"]),
        ("can you please open chrome", ["open_app"]),
        ("i want to launch spotify", ["open_app"]),
        ("open incognito", ["browser_incognito"]),
        ("open a new tab", ["browser_new_tab"]),
        ("switch to the next tab", ["browser_next_tab"]),
        ("go to github.com", ["browser_navigate"]),
        ("open discord", ["open_app"]),
        ("scroll down", ["browser_scroll_down"]),
        ("zoom in", ["browser_zoom_in"]),
        ("bookmark this page", ["browser_bookmark"]),
    ]

    passed = 0
    failed = 0
    for input_text, expected_intents in test_cases:
        commands = parse(input_text)
        actual_intents = [cmd.intent for cmd in commands]
        if actual_intents == expected_intents:
            passed += 1
            print(f"  [PASS] '{input_text}' -> {actual_intents}")
        else:
            failed += 1
            targets = [cmd.target for cmd in commands]
            print(f"  [FAIL] '{input_text}'")
            print(f"    Expected: {expected_intents}")
            print(f"    Got:      {actual_intents} (targets: {targets})")

    total = passed + failed
    print(f"\n  Results: {passed}/{total} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    print("\n[NLP ENGINE] Running parser tests...\n")
    test_parser()
