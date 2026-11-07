"""Offline regressions: no real Messages database or Slack API is accessed."""

import contextlib
import io
import os
from pathlib import Path
import runpy
import sys
import types
import unittest
from unittest import mock


SCRIPT = Path(os.environ.get("MONITOR_SCRIPT", Path(__file__).resolve().parents[1] / "monitor.py"))


class StopPolling(BaseException):
    pass


def message(rowid, text, outgoing=False, sender="sender@example.test"):
    # Match the positional row layout consumed by the existing monitor.
    row = [None] * 30
    row[0] = rowid
    row[2] = text
    row[21] = int(outgoing)
    row[-5] = sender
    return tuple(row)


def poll(snapshots):
    """Execute the entrypoint with inert Slack/SQLite and bounded polling."""
    calls = []
    connections = []
    snapshots = iter(snapshots)
    ticks = 0

    class SlackClient:
        def __init__(self, token):
            self.token = token

        def api_call(self, method, **kwargs):
            calls.append((method, kwargs))
            return {"ok": True}

    class Connection:
        closed = False

        def __init__(self, rows):
            self.rows = rows

        def cursor(self):
            return self

        def execute(self, query):
            self.query = query
            return self

        def __iter__(self):
            return iter(self.rows)

        def close(self):
            self.closed = True

    def connect(path):
        connection = Connection(next(snapshots))
        connections.append(connection)
        return connection

    def sleep(seconds):
        nonlocal ticks
        ticks += 1
        if ticks == 2:
            raise StopPolling

    slack = types.ModuleType("slackclient")
    slack.SlackClient = SlackClient
    # Explicitly block the two obsolete, unused imports even if installed locally.
    modules = {"slackclient": slack, "BaseHTTPServer": None, "imessage": None}
    with mock.patch.dict(sys.modules, modules), mock.patch("sqlite3.connect", connect), mock.patch("time.sleep", sleep), contextlib.redirect_stdout(io.StringIO()):
        try:
            runpy.run_path(str(SCRIPT), run_name="__main__")
        except StopPolling:
            pass

    assert ticks == 2
    assert all(connection.closed for connection in connections)
    return calls


class Python3RegressionTests(unittest.TestCase):
    def test_startup_reaches_polling_without_unused_modules(self):
        self.assertEqual(poll([[], []]), [])

    def test_existing_messages_are_not_forwarded_on_startup(self):
        history = [message(2, "second"), message(1, "first")]
        self.assertEqual(poll([history, history]), [])

    def check_forward(self, row, expected):
        old = message(1, "existing")
        self.assertEqual(poll([[old], [row, old]]), [
            ("chat.postMessage", {"channel": "iMessage", "text": expected})
        ])

    def test_outgoing_ascii_is_text(self):
        self.check_forward(message(2, "Hello", outgoing=True), "Me: Hello")

    def test_outgoing_unicode_is_text(self):
        self.check_forward(message(2, "Grüße 👋 中文", outgoing=True), "Me: Grüße 👋 中文")

    def test_incoming_ascii_is_text(self):
        self.check_forward(message(2, "Hello", sender="+15555550123"), "+15555550123: Hello")

    def test_incoming_unicode_is_text(self):
        self.check_forward(message(2, "Grüße 👋 中文", sender="Zoë"), "Zoë: Grüße 👋 中文")

    def test_unknown_message_behavior_is_preserved(self):
        self.check_forward(message(2, None), "Unknown message")

    def test_multiple_new_messages_remain_in_chronological_order(self):
        old = message(1, "existing")
        calls = poll([[old], [message(3, "reply", outgoing=True), message(2, "hello"), old]])
        self.assertEqual([kwargs["text"] for _, kwargs in calls], ["sender@example.test: hello", "Me: reply"])


if __name__ == "__main__":
    unittest.main()
