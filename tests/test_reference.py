import unittest
from unittest.mock import patch

from jira_mcp.tools.reference.get_issue_types import get_issue_types
from jira_mcp.tools.reference.get_priorities import get_priorities
from jira_mcp.tools.reference.get_resolutions import get_resolutions


class ReferenceTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_get_priorities(self, request):
        request.return_value = [{"id": "1", "name": "High", "description": "Urgent", "iconUrl": "x"}]

        self.assertEqual(
            get_priorities(), [{"id": "1", "name": "High", "description": "Urgent"}]
        )
        self.assertEqual(request.call_args.args, ("GET", "priority"))

    @patch("jira_mcp.client.request")
    def test_get_resolutions(self, request):
        request.return_value = [{"id": "10000", "name": "Done", "description": "Work done"}]

        self.assertEqual(
            get_resolutions(), [{"id": "10000", "name": "Done", "description": "Work done"}]
        )
        self.assertEqual(request.call_args.args, ("GET", "resolution"))

    @patch("jira_mcp.client.request")
    def test_get_issue_types(self, request):
        request.return_value = [
            {"id": "1", "name": "Task", "subtask": False, "description": ""},
            {"id": "2", "name": "Sub-task", "subtask": True, "description": ""},
        ]

        result = get_issue_types()

        self.assertEqual(request.call_args.args, ("GET", "issuetype"))
        self.assertEqual([(t["name"], t["subtask"]) for t in result], [("Task", False), ("Sub-task", True)])


if __name__ == "__main__":
    unittest.main()
