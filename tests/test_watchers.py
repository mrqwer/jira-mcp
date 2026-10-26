import unittest
from unittest.mock import patch

from jira_mcp.tools.watchers.add_watcher import add_watcher
from jira_mcp.tools.watchers.get_watchers import get_watchers
from jira_mcp.tools.watchers.remove_watcher import remove_watcher


class WatchersTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_get_watchers(self, request):
        request.return_value = {
            "isWatching": False,
            "watchCount": 1,
            "watchers": [{"name": "ivan", "displayName": "Ivan", "emailAddress": "x"}],
        }

        result = get_watchers("PROJ-1")

        self.assertEqual(request.call_args.args, ("GET", "issue/PROJ-1/watchers"))
        self.assertEqual(
            result,
            {
                "key": "PROJ-1",
                "watch_count": 1,
                "is_watching": False,
                "watchers": [{"username": "ivan", "display_name": "Ivan"}],
            },
        )

    @patch("jira_mcp.client.request", return_value={})
    def test_add_watcher_posts_username_string(self, request):
        add_watcher("PROJ-1", "ivan")

        self.assertEqual(request.call_args.args, ("POST", "issue/PROJ-1/watchers"))
        self.assertEqual(request.call_args.kwargs["json"], "ivan")
        self.assertEqual(request.call_args.kwargs["expected"], (204,))

    @patch("jira_mcp.client.request", return_value={})
    def test_remove_watcher_uses_username_param(self, request):
        remove_watcher("PROJ-1", "ivan")

        self.assertEqual(request.call_args.args, ("DELETE", "issue/PROJ-1/watchers"))
        self.assertEqual(request.call_args.kwargs["params"], {"username": "ivan"})


if __name__ == "__main__":
    unittest.main()
