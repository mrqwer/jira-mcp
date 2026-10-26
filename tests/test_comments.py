import unittest
from unittest.mock import patch

from jira_mcp.tools.comments.add_comment import add_comment
from jira_mcp.tools.comments.delete_comment import delete_comment
from jira_mcp.tools.comments.get_comments import get_comments


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

    @patch("jira_mcp.client.request", return_value={"id": "8"})
    def test_add_comment_creates(self, request):
        add_comment("PROJ-1", "Hello")

        self.assertEqual(request.call_args.args, ("POST", "issue/PROJ-1/comment"))
        self.assertEqual(request.call_args.kwargs["expected"], (201,))
        self.assertEqual(request.call_args.kwargs["json"], {"body": "Hello"})

    @patch("jira_mcp.client.request", return_value={"id": "8"})
    def test_add_comment_edits_existing(self, request):
        add_comment("PROJ-1", "Edited", comment_id="8")

        self.assertEqual(request.call_args.args, ("PUT", "issue/PROJ-1/comment/8"))
        self.assertEqual(request.call_args.kwargs["expected"], (200,))
        self.assertEqual(request.call_args.kwargs["json"], {"body": "Edited"})

    @patch("jira_mcp.client.request")
    def test_get_comments_pages_and_normalizes(self, request):
        request.return_value = {
            "startAt": 0,
            "maxResults": 1,
            "total": 2,
            "comments": [
                {
                    "id": "7",
                    "author": {"name": "ivan", "displayName": "Ivan"},
                    "created": "2026-01-01T10:00:00.000+0500",
                    "updated": "2026-01-01T10:00:00.000+0500",
                    "body": "Looks good",
                }
            ],
        }

        result = get_comments("PROJ-1", max_results=1, newest_first=True)

        self.assertEqual(request.call_args.args, ("GET", "issue/PROJ-1/comment"))
        self.assertEqual(
            request.call_args.kwargs["params"],
            {"orderBy": "-created", "startAt": 0, "maxResults": 1},
        )
        self.assertEqual(
            result["items"],
            [
                {
                    "id": "7",
                    "author": "Ivan",
                    "author_username": "ivan",
                    "created": "2026-01-01T10:00:00.000+0500",
                    "updated": "2026-01-01T10:00:00.000+0500",
                    "body": "Looks good",
                }
            ],
        )
        self.assertEqual(result["next_start_at"], 1)

    @patch("jira_mcp.client.request", return_value={"comments": []})
    def test_get_comments_oldest_first_by_default(self, request):
        get_comments("PROJ-1")

        self.assertEqual(request.call_args.kwargs["params"]["orderBy"], "created")


if __name__ == "__main__":
    unittest.main()
