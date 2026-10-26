import unittest
from unittest.mock import patch

from jira_mcp.tools.links.add_remote_link import add_remote_link
from jira_mcp.tools.links.delete_link import delete_link
from jira_mcp.tools.links.delete_remote_link import delete_remote_link


class LinksTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_delete_link_calls_expected_endpoint(self, request):
        request.return_value = {}

        result = delete_link("10050")

        self.assertEqual(request.call_args.args, ("DELETE", "issueLink/10050"))
        self.assertEqual(request.call_args.kwargs["expected"], (204,))
        self.assertEqual(result, {"deleted": True, "link_id": "10050"})

    @patch("jira_mcp.client.request", return_value={"id": 300})
    def test_add_remote_link(self, request):
        result = add_remote_link("PROJ-1", "https://git.example.com/pr/1", "PR #1", summary="Fix")

        self.assertEqual(request.call_args.args, ("POST", "issue/PROJ-1/remotelink"))
        self.assertEqual(
            request.call_args.kwargs["json"],
            {"object": {"url": "https://git.example.com/pr/1", "title": "PR #1", "summary": "Fix"}},
        )
        self.assertEqual(result["remote_link_id"], 300)

    @patch("jira_mcp.client.request", return_value={})
    def test_delete_remote_link(self, request):
        delete_remote_link("PROJ-1", "300")

        self.assertEqual(request.call_args.args, ("DELETE", "issue/PROJ-1/remotelink/300"))
        self.assertEqual(request.call_args.kwargs["expected"], (204,))


if __name__ == "__main__":
    unittest.main()
