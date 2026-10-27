"""Record one fish fed to the whale: feed.py FEED_JSON LOGIN [DATE].

Each GitHub user counts at most once per UTC day. Exits 0 if the fish was
counted, 1 if this user already fed the whale today.
"""

import datetime
import json
import sys
from pathlib import Path

path, login = Path(sys.argv[1]), sys.argv[2].lower()
today = sys.argv[3] if len(sys.argv) > 3 else datetime.datetime.now(datetime.timezone.utc).date().isoformat()

state = json.loads(path.read_text())
if state["last_fed"].get(login) == today:
    sys.exit(1)
state["count"] += 1
state["last_fed"][login] = today
path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
