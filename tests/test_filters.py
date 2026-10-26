import unittest
from unittest.mock import patch

from jira_mcp.tools.filters.list_favourite_filters import list_favourite_filters
from jira_mcp.tools.filters.run_filter import run_filter


class FiltersTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_list_favourite_filters(self, request):
        request.return_value = [
            {"id": "10802", "name": "Mine", "jql": "assignee = currentUser()", "owner": {"name": "ivan"}}
        ]

        result = list_favourite_filters()

        self.assertEqual(request.call_args.args, ("GET", "filter/favourite"))
        self.assertEqual(
            result,
            [{"id": "10802", "name": "Mine", "jql": "assignee = currentUser()", "owner": "ivan", "description": None}],
        )

    @patch("jira_mcp.client.request")
    def test_run_filter_searches_with_filter_jql(self, request):
        request.side_effect = [
            {"id": "10802", "name": "Mine", "jql": "assignee = currentUser()"},
            {"total": 1, "issues": [{"key": "PROJ-1", "fields": {}}]},
        ]

        result = run_filter("10802", max_results=5)

        self.assertEqual(request.call_args_list[0].args, ("GET", "filter/10802"))
        self.assertEqual(request.call_args_list[1].args, ("GET", "search"))
        self.assertEqual(
            request.call_args_list[1].kwargs["params"]["jql"], "assignee = currentUser()"
        )
        self.assertEqual(result["filter"]["name"], "Mine")
        self.assertEqual(result["issues"][0]["key"], "PROJ-1")


if __name__ == "__main__":
    unittest.main()
