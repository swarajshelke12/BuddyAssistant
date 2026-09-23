"""
Buddy Agent — Folder Access (Restricted)
ONLY opens well-known user folders. Safe, restricted file search by name.
"""

import os
import subprocess


# ── Allowed folders (whitelist) ─────────────────────────────

def _user_folder(name):
    return os.path.join(os.environ.get("USERPROFILE", ""), name)

ALLOWED_FOLDERS = {
    "desktop": _user_folder("Desktop"),
    "downloads": _user_folder("Downloads"),
    "documents": _user_folder("Documents"),
    "pictures": _user_folder("Pictures"),
    "music": _user_folder("Music"),
    "videos": _user_folder("Videos"),
    "home": os.environ.get("USERPROFILE", ""),
}

# Natural language aliases → folder key
FOLDER_ALIASES = {
    "my downloads": "downloads",
    "my documents": "documents",
    "my desktop": "desktop",
    "my pictures": "pictures",
    "my photos": "pictures",
    "my music": "music",
    "my videos": "videos",
    "my files": "documents",
    "download folder": "downloads",
    "downloads folder": "downloads",
    "document folder": "documents",
    "documents folder": "documents",
    "picture folder": "pictures",
    "pictures folder": "pictures",
    "home folder": "home",
    "home directory": "home",
    "user folder": "home",
}


def open_folder(name):
    """Open an allowed folder in File Explorer. Only whitelisted folders permitted."""
    if not name:
        return False, "Which folder would you like me to open?"

    q = name.lower().strip()

    # Strip common prefixes/suffixes
    for prefix in ["my ", "the ", "open ", "go to ", "show "]:
        if q.startswith(prefix):
            q = q[len(prefix):].strip()
    for suffix in [" folder", " directory", " dir"]:
        if q.endswith(suffix):
            q = q[:-len(suffix)].strip()

    # Resolve via direct match or alias
    folder_key = None
    if q in ALLOWED_FOLDERS:
        folder_key = q
    elif q in FOLDER_ALIASES:
        folder_key = FOLDER_ALIASES[q]

    if folder_key and folder_key in ALLOWED_FOLDERS:
        path = ALLOWED_FOLDERS[folder_key]
        if os.path.isdir(path):
            try:
                subprocess.Popen(["explorer.exe", path])
                return True, f"Opening {folder_key.capitalize()}"
            except Exception as e:
                return False, f"Couldn't open {folder_key}: {e}"

    return False, f"I can only open common folders like Desktop, Downloads, Documents, Pictures, Music, or Videos."


def search_files(query):
    """Search for files matching a query inside allowed common folders only.
    Read-only — just reports what it finds, doesn't open or modify anything.
    """
    if not query:
        return False, "What should I search for?"

    q = query.lower().strip()
    results = []

    for folder_name, folder_path in ALLOWED_FOLDERS.items():
        if not os.path.isdir(folder_path):
            continue
        try:
            for root, dirs, files in os.walk(folder_path):
                # Max 2 levels deep to keep it fast
                depth = root.count(os.sep) - folder_path.count(os.sep)
                if depth > 2:
                    dirs.clear()
                    continue
                for f in files:
                    if q in f.lower():
                        results.append((f, folder_name.capitalize()))
                        if len(results) >= 10:
                            break
                if len(results) >= 10:
                    break
        except PermissionError:
            continue
        if len(results) >= 10:
            break

    if results:
        count = len(results)
        summary = ", ".join(f"{name} in {loc}" for name, loc in results[:3])
        more = f" and {count - 3} more" if count > 3 else ""
        return True, f"Found {count} match{'es' if count != 1 else ''}: {summary}{more}"
    return False, f"No files found matching '{query}' in your common folders."
