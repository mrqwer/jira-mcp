import unittest
from unittest.mock import patch

from jira_mcp.tools.worklogs.add_worklog import add_worklog
from jira_mcp.tools.worklogs.delete_worklog import delete_worklog
from jira_mcp.tools.worklogs.get_worklogs import get_worklogs
from jira_mcp.tools.worklogs.update_worklog import update_worklog


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

    @patch("jira_mcp.client.request", return_value={"id": "101"})
    def test_add_worklog(self, request):
        add_worklog("PROJ-1", "1h 30m", comment="Review", started="2026-01-01T10:00:00.000+0500")

        self.assertEqual(request.call_args.args, ("POST", "issue/PROJ-1/worklog"))
        self.assertEqual(request.call_args.kwargs["expected"], (201,))
        self.assertEqual(
            request.call_args.kwargs["json"],
            {"timeSpent": "1h 30m", "comment": "Review", "started": "2026-01-01T10:00:00.000+0500"},
        )

        add_worklog("PROJ-1", "15m")
        self.assertEqual(request.call_args.kwargs["json"], {"timeSpent": "15m"})

    @patch("jira_mcp.client.request", return_value={"id": "100"})
    def test_update_worklog_sends_only_given_fields(self, request):
        update_worklog("PROJ-1", "100", time_spent="2h", comment="")

        self.assertEqual(request.call_args.args, ("PUT", "issue/PROJ-1/worklog/100"))
        self.assertEqual(request.call_args.kwargs["json"], {"timeSpent": "2h", "comment": ""})

    @patch("jira_mcp.client.request")
    def test_update_worklog_requires_a_change(self, request):
        with self.assertRaisesRegex(ValueError, "time_spent, comment or started"):
            update_worklog("PROJ-1", "100")

        request.assert_not_called()

    @patch("jira_mcp.client.request", return_value={})
    def test_delete_worklog(self, request):
        result = delete_worklog("PROJ-1", "100")

        self.assertEqual(request.call_args.args, ("DELETE", "issue/PROJ-1/worklog/100"))
        self.assertEqual(request.call_args.kwargs["expected"], (204,))
        self.assertEqual(result, {"deleted": True, "worklog_id": "100"})


if __name__ == "__main__":
    unittest.main()
