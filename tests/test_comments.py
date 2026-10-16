import unittest
from unittest.mock import patch

from jira_mcp.tools.comments.delete_comment import delete_comment


class CommentsTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_delete_comment_calls_expected_endpoint(self, request):
        request.return_value = {}

        result = delete_comment("PROJ-1", "10050")

        self.assertEqual(
            request.call_args.args, ("DELETE", "issue/PROJ-1/comment/10050")
        )
        self.assertEqual(request.call_args.kwargs["expected"], (204,))
        self.assertEqual(result, {"deleted": True, "comment_id": "10050"})


if __name__ == "__main__":
    unittest.main()
