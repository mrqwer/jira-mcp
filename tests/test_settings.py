import unittest
from unittest.mock import patch

from jira_mcp import settings


class SettingsTest(unittest.TestCase):
    def test_env_bool_and_int_parse_values(self):
        with patch.dict(
            "os.environ", {"JIRA_VERIFY_SSL": "false", "JIRA_TIMEOUT": "5"}
        ):
            self.assertFalse(settings.env_bool("JIRA_VERIFY_SSL", True))
            self.assertEqual(settings.env_int("JIRA_TIMEOUT", 20), 5)

        with patch.dict("os.environ", {}, clear=True):
            self.assertTrue(settings.env_bool("JIRA_VERIFY_SSL", True))
            self.assertEqual(settings.env_int("JIRA_TIMEOUT", 20), 20)


if __name__ == "__main__":
    unittest.main()
