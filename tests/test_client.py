import unittest
from unittest.mock import patch

from jira_mcp import client, settings


class ClientTest(unittest.TestCase):
    def tearDown(self):
        client.session.cache_clear()

    @patch.multiple(
        settings,
        JIRA_URL="http://jira.example.com",
        JIRA_USER="user",
        JIRA_PASSWORD="secret",
    )
    def test_session_uses_basic_auth(self):
        client.session.cache_clear()
        http = client.session()

        self.assertEqual(http.auth, ("user", "secret"))
        self.assertNotIn("Authorization", http.headers)

    @patch.multiple(
        settings, JIRA_URL="http://jira.example.com", JIRA_USER="", JIRA_PASSWORD=""
    )
    def test_session_reports_missing_settings(self):
        client.session.cache_clear()

        with self.assertRaisesRegex(RuntimeError, "JIRA_USER, JIRA_PASSWORD"):
            client.session()


if __name__ == "__main__":
    unittest.main()
