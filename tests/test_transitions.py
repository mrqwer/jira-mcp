import unittest
from unittest.mock import patch

from jira_mcp.tools.transitions.change_status import change_status


class TransitionsTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_change_status_uses_target_status_name(self, request):
        request.side_effect = [
            {
                "transitions": [
                    {"id": "31", "name": "Start progress", "to": {"name": "In Progress"}}
                ]
            },
            {},
        ]

        result = change_status("PROJ-1", "in progress")

        self.assertEqual(result["transition_id"], "31")
        self.assertEqual(request.call_args.kwargs["json"], {"transition": {"id": "31"}})


if __name__ == "__main__":
    unittest.main()
