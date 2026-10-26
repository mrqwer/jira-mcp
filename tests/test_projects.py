import unittest
from unittest.mock import patch

from jira_mcp import settings
from jira_mcp.tools.projects.get_create_fields import get_create_fields
from jira_mcp.tools.projects.get_project_issue_types import get_project_issue_types
from jira_mcp.tools.projects.list_projects import list_projects


class ProjectsTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_list_projects_is_capped(self, request):
        request.return_value = [{"key": f"P{i}"} for i in range(10)]

        with patch.object(settings, "JIRA_MAX_RESULTS", 3):
            result = list_projects(max_results=50)

        self.assertEqual(request.call_args.args, ("GET", "project"))
        self.assertEqual([p["key"] for p in result], ["P0", "P1", "P2"])

    @patch("jira_mcp.client.request")
    def test_get_project_issue_types(self, request):
        request.return_value = {"projects": [{"key": "PROJ", "issuetypes": [{"name": "Task"}]}]}

        result = get_project_issue_types("PROJ")

        self.assertEqual(request.call_args.args, ("GET", "issue/createmeta"))
        self.assertEqual(
            request.call_args.kwargs["params"],
            {"projectKeys": "PROJ", "expand": "projects.issuetypes"},
        )
        self.assertEqual(result["issuetypes"], [{"name": "Task"}])

    @patch("jira_mcp.client.request", return_value={"projects": []})
    def test_get_project_issue_types_unknown_project(self, request):
        with self.assertRaisesRegex(ValueError, "unavailable or not creatable"):
            get_project_issue_types("NOPE")

    @patch("jira_mcp.client.request")
    def test_get_create_fields_resolves_localized_name_to_id(self, request):
        request.side_effect = [
            {"projects": [{"issuetypes": [{"id": "10004", "name": "Ошибка"}, {"id": "10002", "name": "Задача"}]}]},
            {"projects": [{"issuetypes": [{"id": "10002", "name": "Задача", "fields": {"summary": {"required": True}}}]}]},
        ]

        result = get_create_fields("PROJ", "задача")

        self.assertEqual(
            request.call_args_list[0].kwargs["params"],
            {"projectKeys": "PROJ", "expand": "projects.issuetypes"},
        )
        self.assertEqual(
            request.call_args_list[1].kwargs["params"],
            {
                "projectKeys": "PROJ",
                "issuetypeIds": "10002",
                "expand": "projects.issuetypes.fields",
            },
        )
        self.assertEqual(result["fields"], {"summary": {"required": True}})

    @patch("jira_mcp.client.request")
    def test_get_create_fields_accepts_type_id(self, request):
        request.side_effect = [
            {"projects": [{"issuetypes": [{"id": "10002", "name": "Задача"}]}]},
            {"projects": [{"issuetypes": [{"id": "10002", "fields": {}}]}]},
        ]

        get_create_fields("PROJ", "10002")

        self.assertEqual(request.call_args.kwargs["params"]["issuetypeIds"], "10002")

    @patch("jira_mcp.client.request")
    def test_get_create_fields_unknown_type_lists_available(self, request):
        request.return_value = {"projects": [{"issuetypes": [{"id": "1", "name": "Task"}]}]}

        with self.assertRaisesRegex(ValueError, r"unavailable in project 'PROJ'. Available: \['Task'\]"):
            get_create_fields("PROJ", "Nope")

        request.return_value = {"projects": []}
        with self.assertRaisesRegex(ValueError, "unavailable in project"):
            get_create_fields("NOPE", "Task")

    @patch("jira_mcp.client.request")
    def test_get_create_fields_empty_second_response(self, request):
        request.side_effect = [
            {"projects": [{"issuetypes": [{"id": "1", "name": "Task"}]}]},
            {"projects": []},
        ]

        with self.assertRaisesRegex(ValueError, "unavailable in project"):
            get_create_fields("PROJ", "Task")


if __name__ == "__main__":
    unittest.main()
