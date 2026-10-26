import unittest
from unittest.mock import patch

from jira_mcp.tools.links.add_remote_link import add_remote_link
from jira_mcp.tools.links.delete_link import delete_link
from jira_mcp.tools.links.delete_remote_link import delete_remote_link
from jira_mcp.tools.links.get_link_types import get_link_types
from jira_mcp.tools.links.get_remote_links import get_remote_links
from jira_mcp.tools.links.link_tickets import link_tickets


class LinksTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_delete_link_calls_expected_endpoint(self, request):
        request.return_value = {}

        result = delete_link("10050")

        self.assertEqual(request.call_args.args, ("DELETE", "issueLink/10050"))
        self.assertEqual(request.call_args.kwargs["expected"], (204,))
        self.assertEqual(result, {"deleted": True, "link_id": "10050"})

    @patch("jira_mcp.client.request", return_value={})
    def test_link_tickets(self, request):
        result = link_tickets("PROJ-1", "PROJ-2", "Blocks", comment="Blocked by API")

        self.assertEqual(request.call_args.args, ("POST", "issueLink"))
        self.assertEqual(request.call_args.kwargs["expected"], (201,))
        self.assertEqual(
            request.call_args.kwargs["json"],
            {
                "type": {"name": "Blocks"},
                "inwardIssue": {"key": "PROJ-1"},
                "outwardIssue": {"key": "PROJ-2"},
                "comment": {"body": "Blocked by API"},
            },
        )
        self.assertEqual(result["link_type"], "Blocks")

        link_tickets("PROJ-1", "PROJ-2", "Relates")
        self.assertNotIn("comment", request.call_args.kwargs["json"])

    @patch("jira_mcp.client.request")
    def test_get_link_types(self, request):
        request.return_value = {"issueLinkTypes": [{"name": "Blocks"}]}

        self.assertEqual(get_link_types(), [{"name": "Blocks"}])
        self.assertEqual(request.call_args.args, ("GET", "issueLinkType"))

    @patch("jira_mcp.client.request")
    def test_get_remote_links_always_returns_list(self, request):
        request.return_value = [{"id": 1}]
        self.assertEqual(get_remote_links("PROJ-1"), [{"id": 1}])
        self.assertEqual(request.call_args.args, ("GET", "issue/PROJ-1/remotelink"))

        request.return_value = {"id": 2}
        self.assertEqual(get_remote_links("PROJ-1"), [{"id": 2}])

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
