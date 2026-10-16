import unittest
from unittest.mock import patch

from jira_mcp.tools.links.delete_link import delete_link


class LinksTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_delete_link_calls_expected_endpoint(self, request):
        request.return_value = {}

        result = delete_link("10050")

        self.assertEqual(request.call_args.args, ("DELETE", "issueLink/10050"))
        self.assertEqual(request.call_args.kwargs["expected"], (204,))
        self.assertEqual(result, {"deleted": True, "link_id": "10050"})


if __name__ == "__main__":
    unittest.main()
