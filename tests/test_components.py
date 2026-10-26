import unittest
from unittest.mock import patch

from jira_mcp.tools.components.create_component import create_component
from jira_mcp.tools.components.list_components import list_components


class ComponentsTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_list_components(self, request):
        request.return_value = [
            {"id": "5", "name": "API", "lead": {"name": "ivan"}, "assigneeType": "PROJECT_DEFAULT"}
        ]

        result = list_components("PROJ")

        self.assertEqual(request.call_args.args, ("GET", "project/PROJ/components"))
        self.assertEqual(
            result,
            [{"id": "5", "name": "API", "description": None, "lead": "ivan", "assignee_type": "PROJECT_DEFAULT"}],
        )

    @patch("jira_mcp.client.request")
    def test_create_component(self, request):
        request.return_value = {"id": "6", "name": "UI"}

        create_component("proj", "UI", lead_username="petr")

        self.assertEqual(request.call_args.args, ("POST", "component"))
        self.assertEqual(request.call_args.kwargs["expected"], (201,))
        self.assertEqual(
            request.call_args.kwargs["json"],
            {"project": "PROJ", "name": "UI", "leadUserName": "petr"},
        )


if __name__ == "__main__":
    unittest.main()
