import unittest
from unittest.mock import patch

from jira_mcp.tools.users.find_assignable_users import find_assignable_users
from jira_mcp.tools.users.find_users import find_users
from jira_mcp.tools.users.get_my_permissions import get_my_permissions
from jira_mcp.tools.users.get_myself import get_myself


class UsersTest(unittest.TestCase):
    @patch("jira_mcp.client.request", return_value={"name": "ivan"})
    def test_get_myself(self, request):
        self.assertEqual(get_myself(), {"name": "ivan"})
        self.assertEqual(request.call_args.args, ("GET", "myself"))

    @patch("jira_mcp.client.request")
    def test_find_users(self, request):
        request.return_value = {"users": [{"name": "ivan"}], "total": 1}

        result = find_users("iv", max_results=5)

        self.assertEqual(request.call_args.args, ("GET", "user/picker"))
        self.assertEqual(request.call_args.kwargs["params"], {"query": "iv", "maxResults": 5})
        self.assertEqual(result, [{"name": "ivan"}])


class AssignableUsersTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_searches_by_project(self, request):
        request.return_value = [
            {"name": "ivan", "displayName": "Ivan", "emailAddress": "ivan@example.com", "active": True}
        ]

        result = find_assignable_users(project_key="PROJ", query="iv", max_results=5)

        self.assertEqual(request.call_args.args, ("GET", "user/assignable/search"))
        self.assertEqual(
            request.call_args.kwargs["params"],
            {"username": "iv", "maxResults": 5, "project": "PROJ"},
        )
        self.assertEqual(
            result,
            [{"username": "ivan", "display_name": "Ivan", "email": "ivan@example.com", "active": True}],
        )

    @patch("jira_mcp.client.request", return_value=[])
    def test_issue_key_takes_precedence(self, request):
        find_assignable_users(project_key="PROJ", issue_key="PROJ-1")

        params = request.call_args.kwargs["params"]
        self.assertEqual(params["issueKey"], "PROJ-1")
        self.assertNotIn("project", params)

    @patch("jira_mcp.client.request")
    def test_requires_project_or_issue(self, request):
        with self.assertRaisesRegex(ValueError, "project_key or issue_key"):
            find_assignable_users()

        request.assert_not_called()


PERMISSIONS = {
    "permissions": {
        "EDIT_ISSUES": {"name": "Edit Issues", "havePermission": True},
        "DELETE_ISSUES": {"name": "Delete Issues", "havePermission": False},
        "TRANSITION_ISSUES": {"name": "Transition Issues", "havePermission": True},
    }
}


@patch("jira_mcp.client.request", return_value=PERMISSIONS)
class MyPermissionsTest(unittest.TestCase):
    def test_splits_granted_and_denied(self, request):
        result = get_my_permissions(project_key="PROJ")

        self.assertEqual(request.call_args.args, ("GET", "mypermissions"))
        self.assertEqual(request.call_args.kwargs["params"], {"projectKey": "PROJ"})
        self.assertEqual(result, {"granted": ["EDIT_ISSUES", "TRANSITION_ISSUES"], "denied": ["DELETE_ISSUES"]})

    def test_checks_single_permission(self, request):
        result = get_my_permissions(issue_key="PROJ-1", permission="delete_issues")

        self.assertEqual(request.call_args.kwargs["params"], {"issueKey": "PROJ-1"})
        self.assertEqual(
            result, {"permission": "DELETE_ISSUES", "name": "Delete Issues", "granted": False}
        )

    def test_rejects_unknown_permission(self, request):
        with self.assertRaisesRegex(ValueError, "Unknown Jira permission 'NOPE'"):
            get_my_permissions(permission="nope")


if __name__ == "__main__":
    unittest.main()
