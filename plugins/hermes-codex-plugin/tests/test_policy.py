import unittest

from hermes_codex_plugin.domain.memory.policy import search_hint_context


class PolicyTest(unittest.TestCase):
    def test_search_hint_uses_request_without_domain_expansion(self) -> None:
        prompt = (
            "Review this Python service and improve it according to "
            "DDD and code style rules"
        )

        hint = search_hint_context(prompt)

        self.assertIn(prompt, hint)
        self.assertNotIn("collection operations", hint)

    def test_search_hint_compacts_whitespace_and_limits_long_queries(self) -> None:
        prompt = "  first line\n\nsecond line  " + ("x" * 500)

        hint = search_hint_context(prompt)

        self.assertIn("first line second line", hint)
        self.assertLess(len(hint), 700)


if __name__ == "__main__":
    unittest.main()
