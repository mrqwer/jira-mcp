import unittest
from unittest.mock import patch

from jira_mcp.tools.worklogs.get_worklogs import get_worklogs


class WorklogsTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_get_worklogs_normalizes_items(self, request):
        request.return_value = {
            "startAt": 0,
            "maxResults": 1,
            "total": 1,
            "worklogs": [
                {
                    "id": "100",
                    "author": {"name": "ivan", "displayName": "Ivan"},
                    "started": "2026-01-01T10:00:00.000+0500",
                    "timeSpent": "1h 30m",
                    "timeSpentSeconds": 5400,
                    "comment": "Review",
                }
            ],
        }

        result = get_worklogs("PROJ-1")

        self.assertEqual(request.call_args.args, ("GET", "issue/PROJ-1/worklog"))
        self.assertEqual(
            result["items"],
            [
                {
                    "id": "100",
                    "author": "Ivan",
                    "author_username": "ivan",
                    "started": "2026-01-01T10:00:00.000+0500",
                    "time_spent": "1h 30m",
                    "time_spent_seconds": 5400,
                    "comment": "Review",
                }
            ],
        )
        self.assertIsNone(result["next_start_at"])


if __name__ == "__main__":
    unittest.main()
