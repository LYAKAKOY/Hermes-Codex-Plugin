from pathlib import Path
import os
import tempfile
import unittest

from hermes_codex_plugin import __version__
from hermes_codex_plugin.presentation.mcp.server import MCPServer


class MCPServerTest(unittest.TestCase):
    def test_initialize_returns_server_info(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["HERMES_CODEX_DB"] = str(Path(tmp) / "memory.sqlite3")
            try:
                server = MCPServer()

                response = server.handle_message(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {"protocolVersion": "2024-11-05"},
                    }
                )

                self.assertEqual(response["result"]["serverInfo"]["version"], __version__)
                self.assertIn("hermes_codex_search_chats", response["result"]["instructions"])
            finally:
                os.environ.pop("HERMES_CODEX_DB", None)

    def test_tools_list_contains_memory_tools(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["HERMES_CODEX_DB"] = str(Path(tmp) / "memory.sqlite3")
            try:
                server = MCPServer()

                response = server.handle_message(
                    {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
                )

                tool_names = {tool["name"] for tool in response["result"]["tools"]}
                self.assertIn("hermes_codex_search", tool_names)
                self.assertIn("hermes_codex_search_chats", tool_names)
                self.assertIn("hermes_codex_remember", tool_names)
                self.assertIn("hermes_codex_forget", tool_names)
            finally:
                os.environ.pop("HERMES_CODEX_DB", None)

    def test_tools_call_search(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["HERMES_CODEX_DB"] = str(Path(tmp) / "memory.sqlite3")
            try:
                server = MCPServer()
                server.store.add_entry("Always run unittest before release.", kind="rule")

                response = server.handle_message(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "hermes_codex_search",
                            "arguments": {"query": "unittest release"},
                        },
                    }
                )

                text = response["result"]["content"][0]["text"]
                self.assertIn("unittest", text)
            finally:
                os.environ.pop("HERMES_CODEX_DB", None)

    def test_search_chats_ignores_current_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["HERMES_CODEX_DB"] = str(Path(tmp) / "memory.sqlite3")
            try:
                server = MCPServer()
                server.store.add_entry(
                    "Previous chat fact: HCP_MCP_CROSS_CHAT_FACT.",
                    kind="assistant",
                    session_id="old-chat",
                    cwd="/tmp/old-project",
                )

                response = server.handle_message(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "hermes_codex_search_chats",
                            "arguments": {"query": "HCP_MCP_CROSS_CHAT_FACT"},
                        },
                    }
                )

                text = response["result"]["content"][0]["text"]
                self.assertIn("HCP_MCP_CROSS_CHAT_FACT", text)
                self.assertIn("old-chat", text)
            finally:
                os.environ.pop("HERMES_CODEX_DB", None)

    def test_remember_stats_and_forget_tools_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["HERMES_CODEX_DB"] = str(Path(tmp) / "memory.sqlite3")
            try:
                server = MCPServer()

                remember_response = server.handle_message(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "hermes_codex_remember",
                            "arguments": {
                                "content": "MCP round trip memory.",
                                "kind": "rule",
                            },
                        },
                    }
                )
                remember_text = remember_response["result"]["content"][0]["text"]
                entry_id = int(remember_text.split("#")[1])

                stats_response = server.handle_message(
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {
                            "name": "hermes_codex_stats",
                            "arguments": {},
                        },
                    }
                )
                stats_text = stats_response["result"]["content"][0]["text"]
                self.assertIn('"total_entries": 1', stats_text)

                forget_response = server.handle_message(
                    {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "hermes_codex_forget",
                            "arguments": {"id": entry_id},
                        },
                    }
                )

                self.assertIn(
                    "Deleted entry #{}".format(entry_id),
                    forget_response["result"]["content"][0]["text"],
                )
            finally:
                os.environ.pop("HERMES_CODEX_DB", None)

    def test_unknown_method_and_tool_return_jsonrpc_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["HERMES_CODEX_DB"] = str(Path(tmp) / "memory.sqlite3")
            try:
                server = MCPServer()

                unknown_method = server.handle_message(
                    {"jsonrpc": "2.0", "id": 1, "method": "missing/method"}
                )
                unknown_tool = server.handle_message(
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {"name": "missing_tool", "arguments": {}},
                    }
                )

                self.assertEqual(unknown_method["error"]["code"], -32601)
                self.assertEqual(unknown_tool["error"]["code"], -32601)
            finally:
                os.environ.pop("HERMES_CODEX_DB", None)

    def test_notification_without_id_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["HERMES_CODEX_DB"] = str(Path(tmp) / "memory.sqlite3")
            try:
                server = MCPServer()

                response = server.handle_message(
                    {"jsonrpc": "2.0", "method": "notifications/initialized"}
                )

                self.assertIsNone(response)
            finally:
                os.environ.pop("HERMES_CODEX_DB", None)

    def test_remember_tool_rejects_empty_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["HERMES_CODEX_DB"] = str(Path(tmp) / "memory.sqlite3")
            try:
                server = MCPServer()

                with self.assertRaises(ValueError):
                    server.tool_remember({"content": "   "})
            finally:
                os.environ.pop("HERMES_CODEX_DB", None)


if __name__ == "__main__":
    unittest.main()
