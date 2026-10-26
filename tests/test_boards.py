import unittest
from unittest.mock import patch

from jira_mcp.tools.boards.get_backlog import get_backlog
from jira_mcp.tools.boards.get_board_config import get_board_config
from jira_mcp.tools.boards.get_board_issues import get_board_issues
from jira_mcp.tools.boards.list_boards import list_boards
from jira_mcp.tools.boards.rank_issues import rank_issues

AGILE_ISSUES = {
    "startAt": 0,
    "maxResults": 1,
    "total": 2,
    "issues": [
        {
            "key": "PROJ-1",
            "fields": {
                "summary": "Fix login",
                "status": {"name": "In Progress"},
                "assignee": {"name": "ivan"},
                "issuetype": {"name": "Bug"},
                "priority": {"name": "High"},
                "updated": "2026-01-01T10:00:00.000+0500",
            },
        }
    ],
}


class BoardsTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_list_boards_uses_agile_api_and_filters(self, request):
        request.return_value = {
            "isLast": True,
            "values": [{"id": 25, "name": "Main", "type": "kanban", "self": "x"}],
        }

        result = list_boards(project_key="PROJ", board_type="kanban")

        self.assertEqual(request.call_args.args, ("GET", "board"))
        self.assertEqual(request.call_args.kwargs["api"], "agile")
        self.assertEqual(request.call_args.kwargs["params"]["projectKeyOrId"], "PROJ")
        self.assertEqual(request.call_args.kwargs["params"]["type"], "kanban")
        self.assertEqual(result["items"], [{"id": 25, "name": "Main", "type": "kanban"}])

    @patch("jira_mcp.client.request", return_value={"values": []})
    def test_list_boards_by_name_only(self, request):
        list_boards(name="Open")

        params = request.call_args.kwargs["params"]
        self.assertEqual(params["name"], "Open")
        self.assertNotIn("projectKeyOrId", params)
        self.assertNotIn("type", params)

    @patch("jira_mcp.client.request")
    def test_board_config_resolves_status_names(self, request):
        request.side_effect = [
            {
                "id": 25,
                "name": "Main",
                "type": "kanban",
                "filter": {"id": "10802"},
                "subQuery": {"query": "fixVersion is EMPTY"},
                "columnConfig": {
                    "columns": [
                        {"name": "Backlog", "statuses": []},
                        {"name": "Doing", "statuses": [{"id": "3"}, {"id": "4"}], "max": 5},
                    ]
                },
            },
            [{"id": "3", "name": "In Progress"}, {"id": "4", "name": "Review"}],
        ]

        result = get_board_config(25)

        self.assertEqual(request.call_args_list[0].args, ("GET", "board/25/configuration"))
        self.assertEqual(request.call_args_list[0].kwargs["api"], "agile")
        self.assertEqual(request.call_args_list[1].args, ("GET", "status"))
        self.assertEqual(result["filter_id"], "10802")
        self.assertEqual(result["sub_query"], "fixVersion is EMPTY")
        self.assertEqual(result["columns"][0], {"name": "Backlog", "statuses": []})
        self.assertEqual(
            result["columns"][1],
            {
                "name": "Doing",
                "statuses": [{"id": "3", "name": "In Progress"}, {"id": "4", "name": "Review"}],
                "limits": {"min": None, "max": 5},
            },
        )

    @patch("jira_mcp.client.request", return_value=AGILE_ISSUES)
    def test_board_issues_are_compacted(self, request):
        result = get_board_issues(25, jql="assignee = currentUser()", max_results=1)

        self.assertEqual(request.call_args.args, ("GET", "board/25/issue"))
        params = request.call_args.kwargs["params"]
        self.assertEqual(params["jql"], "assignee = currentUser()")
        self.assertEqual(params["fields"], "summary,status,assignee,issuetype,priority,updated")
        item = result["items"][0]
        self.assertEqual(item["key"], "PROJ-1")
        self.assertEqual(item["status"], "In Progress")
        self.assertEqual(item["assignee"], "ivan")
        self.assertTrue(item["browse_url"].endswith("/browse/PROJ-1"))
        self.assertEqual(result["next_start_at"], 1)

    @patch("jira_mcp.client.request", return_value={"issues": []})
    def test_backlog_path(self, request):
        get_backlog(27)

        self.assertEqual(request.call_args.args, ("GET", "board/27/backlog"))
        self.assertNotIn("jql", request.call_args.kwargs["params"])


@patch("jira_mcp.client.request", return_value={})
class RankIssuesTest(unittest.TestCase):
    def test_ranks_before_issue(self, request):
        result = rank_issues(["PROJ-2", "PROJ-3"], before_issue_key="PROJ-1")

        self.assertEqual(request.call_args.args, ("PUT", "issue/rank"))
        self.assertEqual(request.call_args.kwargs["api"], "agile")
        self.assertEqual(request.call_args.kwargs["expected"], (204, 207))
        self.assertEqual(
            request.call_args.kwargs["json"],
            {"issues": ["PROJ-2", "PROJ-3"], "rankBeforeIssue": "PROJ-1"},
        )
        self.assertEqual(result["errors"], [])

    def test_ranks_after_issue_and_reports_partial_errors(self, request):
        request.return_value = {"entries": [{"issueKey": "PROJ-2", "status": 400}]}

        result = rank_issues(["PROJ-2"], after_issue_key="PROJ-1")

        self.assertEqual(request.call_args.kwargs["json"]["rankAfterIssue"], "PROJ-1")
        self.assertEqual(result["errors"], [{"issueKey": "PROJ-2", "status": 400}])

    def test_requires_exactly_one_anchor(self, request):
        with self.assertRaises(ValueError):
            rank_issues(["PROJ-2"])
        with self.assertRaises(ValueError):
            rank_issues(["PROJ-2"], before_issue_key="PROJ-1", after_issue_key="PROJ-3")
        with self.assertRaises(ValueError):
            rank_issues([], before_issue_key="PROJ-1")

        request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
