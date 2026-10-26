import unittest
from unittest.mock import patch

from jira_mcp.tools.epics.add_to_epic import add_to_epic
from jira_mcp.tools.epics.get_epic_issues import get_epic_issues
from jira_mcp.tools.epics.list_epics import list_epics


class EpicsTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_list_epics_filters_done(self, request):
        request.return_value = {
            "isLast": True,
            "values": [{"id": 1, "key": "PROJ-10", "name": "Auth", "summary": "Auth work", "done": False}],
        }

        result = list_epics(25, done=False)

        self.assertEqual(request.call_args.args, ("GET", "board/25/epic"))
        self.assertEqual(request.call_args.kwargs["params"]["done"], "false")
        self.assertEqual(request.call_args.kwargs["api"], "agile")
        self.assertEqual(result["items"][0]["key"], "PROJ-10")
        self.assertTrue(result["items"][0]["browse_url"].endswith("/browse/PROJ-10"))

    @patch("jira_mcp.client.request", return_value={"issues": []})
    def test_get_epic_issues_path(self, request):
        get_epic_issues("PROJ-10")

        self.assertEqual(request.call_args.args, ("GET", "epic/PROJ-10/issue"))
        self.assertEqual(request.call_args.kwargs["api"], "agile")

    @patch("jira_mcp.client.request", return_value={})
    def test_add_to_epic(self, request):
        result = add_to_epic("PROJ-10", ["PROJ-1"])

        self.assertEqual(request.call_args.args, ("POST", "epic/PROJ-10/issue"))
        self.assertEqual(request.call_args.kwargs["json"], {"issues": ["PROJ-1"]})
        self.assertEqual(request.call_args.kwargs["expected"], (204,))
        self.assertEqual(result, {"epic": "PROJ-10", "added": ["PROJ-1"]})


if __name__ == "__main__":
    unittest.main()
