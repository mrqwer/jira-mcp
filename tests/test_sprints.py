import unittest
from unittest.mock import patch

from jira_mcp.tools.sprints.close_sprint import close_sprint
from jira_mcp.tools.sprints.create_sprint import create_sprint
from jira_mcp.tools.sprints.get_sprint_issues import get_sprint_issues
from jira_mcp.tools.sprints.list_sprints import list_sprints
from jira_mcp.tools.sprints.move_to_backlog import move_to_backlog
from jira_mcp.tools.sprints.move_to_sprint import move_to_sprint
from jira_mcp.tools.sprints.start_sprint import start_sprint

SPRINT = {
    "id": 11,
    "name": "Sprint 1",
    "state": "future",
    "startDate": "2026-11-02T09:00:00.000+05:00",
    "endDate": "2026-11-16T09:00:00.000+05:00",
    "goal": "Ship login",
    "originBoardId": 27,
}


class SprintsReadTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_list_sprints_filters_state(self, request):
        request.return_value = {"isLast": True, "values": [SPRINT]}

        result = list_sprints(27, state="active,future")

        self.assertEqual(request.call_args.args, ("GET", "board/27/sprint"))
        self.assertEqual(request.call_args.kwargs["api"], "agile")
        self.assertEqual(request.call_args.kwargs["params"]["state"], "active,future")
        self.assertEqual(
            result["items"][0],
            {
                "id": 11,
                "name": "Sprint 1",
                "state": "future",
                "start_date": "2026-11-02T09:00:00.000+05:00",
                "end_date": "2026-11-16T09:00:00.000+05:00",
                "complete_date": None,
                "goal": "Ship login",
            },
        )

    @patch("jira_mcp.client.request", return_value={"issues": []})
    def test_sprint_issues_path(self, request):
        get_sprint_issues(11, jql="status != Done")

        self.assertEqual(request.call_args.args, ("GET", "sprint/11/issue"))
        self.assertEqual(request.call_args.kwargs["params"]["jql"], "status != Done")


@patch("jira_mcp.client.request")
class SprintsWriteTest(unittest.TestCase):
    def test_move_to_sprint(self, request):
        request.return_value = {}

        result = move_to_sprint(11, ["PROJ-1", "PROJ-2"])

        self.assertEqual(request.call_args.args, ("POST", "sprint/11/issue"))
        self.assertEqual(request.call_args.kwargs["json"], {"issues": ["PROJ-1", "PROJ-2"]})
        self.assertEqual(request.call_args.kwargs["expected"], (204,))
        self.assertEqual(request.call_args.kwargs["api"], "agile")
        self.assertEqual(result["moved"], ["PROJ-1", "PROJ-2"])

    def test_move_to_backlog(self, request):
        request.return_value = {}

        move_to_backlog(["PROJ-1"])

        self.assertEqual(request.call_args.args, ("POST", "backlog/issue"))
        self.assertEqual(request.call_args.kwargs["json"], {"issues": ["PROJ-1"]})
        self.assertEqual(request.call_args.kwargs["api"], "agile")

    def test_issue_key_limits(self, request):
        with self.assertRaisesRegex(ValueError, "at least one"):
            move_to_sprint(11, [])
        with self.assertRaisesRegex(ValueError, "at most 50"):
            move_to_backlog([f"PROJ-{i}" for i in range(51)])

        request.assert_not_called()

    def test_create_sprint(self, request):
        request.return_value = SPRINT

        result = create_sprint(27, "Sprint 1", goal="Ship login")

        self.assertEqual(request.call_args.args, ("POST", "sprint"))
        self.assertEqual(
            request.call_args.kwargs["json"],
            {"name": "Sprint 1", "originBoardId": 27, "goal": "Ship login"},
        )
        self.assertEqual(request.call_args.kwargs["api"], "agile")
        self.assertEqual(result["id"], 11)

    def test_create_sprint_with_dates(self, request):
        request.return_value = SPRINT

        create_sprint(27, "Sprint 1", start_date="2026-11-02", end_date="2026-11-16")

        self.assertEqual(
            request.call_args.kwargs["json"],
            {
                "name": "Sprint 1",
                "originBoardId": 27,
                "startDate": "2026-11-02",
                "endDate": "2026-11-16",
            },
        )

    def test_start_sprint(self, request):
        request.return_value = dict(SPRINT, state="active")

        result = start_sprint(11, "2026-11-02T09:00:00.000+05:00", "2026-11-16T09:00:00.000+05:00")

        self.assertEqual(request.call_args.args, ("POST", "sprint/11"))
        self.assertEqual(
            request.call_args.kwargs["json"],
            {
                "state": "active",
                "startDate": "2026-11-02T09:00:00.000+05:00",
                "endDate": "2026-11-16T09:00:00.000+05:00",
            },
        )
        self.assertEqual(result["state"], "active")

    def test_close_sprint(self, request):
        request.return_value = dict(SPRINT, state="closed")

        result = close_sprint(11)

        self.assertEqual(request.call_args.args, ("POST", "sprint/11"))
        self.assertEqual(request.call_args.kwargs["json"], {"state": "closed"})
        self.assertEqual(result["state"], "closed")


if __name__ == "__main__":
    unittest.main()
