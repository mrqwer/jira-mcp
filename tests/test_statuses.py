import unittest
from unittest.mock import patch

from jira_mcp.tools.statuses.get_all_statuses import get_all_statuses
from jira_mcp.tools.statuses.get_project_statuses import get_project_statuses


class StatusesTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_get_project_statuses_calls_expected_endpoint(self, request):
        request.return_value = [{"name": "Задача", "statuses": []}]

        result = get_project_statuses("PROJ")

        self.assertEqual(request.call_args.args, ("GET", "project/PROJ/statuses"))
        self.assertEqual(result, [{"name": "Задача", "statuses": []}])

    @patch("jira_mcp.client.request")
    def test_get_all_statuses_calls_expected_endpoint(self, request):
        request.return_value = [{"id": "10201", "name": "Готово"}]

        result = get_all_statuses()

        self.assertEqual(request.call_args.args, ("GET", "status"))
        self.assertEqual(result, [{"id": "10201", "name": "Готово"}])


if __name__ == "__main__":
    unittest.main()
