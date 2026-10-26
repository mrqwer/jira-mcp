import unittest
from unittest.mock import patch

from jira_mcp import settings
from jira_mcp.tools.issues.create_ticket import create_ticket
from jira_mcp.tools.issues.get_edit_fields import get_edit_fields
from jira_mcp.tools.issues.get_issue_history import get_issue_history
from jira_mcp.tools.issues.notify_issue import notify_issue
from jira_mcp.tools.issues.update_ticket import update_ticket


class IssuesTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_create_ticket_keeps_core_fields_authoritative(self, request):
        request.return_value = {"key": "PROJ-1"}

        result = create_ticket(
            "proj",
            "Useful title",
            "Useful description",
            additional_fields={"summary": "wrong", "customfield_10000": 3},
        )

        fields = request.call_args.kwargs["json"]["fields"]
        self.assertEqual(fields["summary"], "Useful title")
        self.assertEqual(fields["customfield_10000"], 3)
        self.assertEqual(result["browse_url"], f"{settings.JIRA_URL}/browse/PROJ-1")

    @patch("jira_mcp.client.request")
    def test_get_edit_fields_returns_field_metadata(self, request):
        request.return_value = {"fields": {"labels": {"operations": ["add", "set", "remove"]}}}

        result = get_edit_fields("PROJ-1")

        self.assertEqual(request.call_args.args, ("GET", "issue/PROJ-1/editmeta"))
        self.assertEqual(result, {"labels": {"operations": ["add", "set", "remove"]}})


CHANGELOG = {
    "key": "PROJ-1",
    "changelog": {
        "startAt": 0,
        "maxResults": 3,
        "total": 3,
        "histories": [
            {
                "id": "1",
                "author": {"name": "ivan", "displayName": "Ivan"},
                "created": "2026-01-01T10:00:00.000+0500",
                "items": [
                    {"field": "status", "from": "1", "fromString": "To Do", "to": "3", "toString": "In Progress"},
                    {"field": "assignee", "from": None, "fromString": None, "to": "ivan", "toString": "Ivan"},
                ],
            },
            {
                "id": "2",
                "author": {"name": "petr", "displayName": "Petr"},
                "created": "2026-01-02T10:00:00.000+0500",
                "items": [{"field": "labels", "fromString": "", "toString": "backend"}],
            },
            {
                "id": "3",
                "author": {"name": "ivan", "displayName": "Ivan"},
                "created": "2026-01-03T10:00:00.000+0500",
                "items": [{"field": "status", "fromString": "In Progress", "toString": "Done"}],
            },
        ],
    },
}


@patch("jira_mcp.client.request", return_value=CHANGELOG)
class IssueHistoryTest(unittest.TestCase):
    def test_returns_all_changes_oldest_first(self, request):
        result = get_issue_history("PROJ-1")

        self.assertEqual(
            request.call_args.kwargs["params"], {"expand": "changelog", "fields": "summary"}
        )
        self.assertEqual([c["id"] for c in result["changes"]], ["1", "2", "3"])
        self.assertEqual(
            result["changes"][0]["items"][0],
            {"field": "status", "from": "To Do", "to": "In Progress"},
        )
        self.assertEqual(result["changes"][0]["author_username"], "ivan")
        self.assertTrue(result["history_complete"])

    def test_filters_by_field_and_limits_to_latest(self, request):
        result = get_issue_history("PROJ-1", field="Status", limit=1)

        self.assertEqual(result["matching_changes"], 2)
        self.assertEqual(len(result["changes"]), 1)
        self.assertEqual(result["changes"][0]["items"], [{"field": "status", "from": "In Progress", "to": "Done"}])

    def test_reports_truncated_history(self, request):
        request.return_value = {
            "key": "PROJ-1",
            "changelog": {"total": 250, "histories": CHANGELOG["changelog"]["histories"]},
        }

        self.assertFalse(get_issue_history("PROJ-1")["history_complete"])


@patch("jira_mcp.client.request", return_value={})
class NotifyIssueTest(unittest.TestCase):
    def test_notifies_users_and_roles(self, request):
        notify_issue("PROJ-1", "Ping", "Please review", usernames=["ivan"], assignee=True)

        self.assertEqual(request.call_args.args, ("POST", "issue/PROJ-1/notify"))
        self.assertEqual(request.call_args.kwargs["expected"], (204,))
        self.assertEqual(
            request.call_args.kwargs["json"],
            {
                "subject": "Ping",
                "textBody": "Please review",
                "to": {
                    "reporter": False,
                    "assignee": True,
                    "watchers": False,
                    "users": [{"name": "ivan"}],
                },
            },
        )

    def test_requires_a_recipient(self, request):
        with self.assertRaisesRegex(ValueError, "usernames"):
            notify_issue("PROJ-1", "Ping", "text")

        request.assert_not_called()


@patch("jira_mcp.client.request", return_value={})
class UpdateTicketTest(unittest.TestCase):
    def test_fields_only_keeps_previous_payload(self, request):
        result = update_ticket("PROJ-1", fields={"summary": "New"})

        self.assertEqual(request.call_args.args, ("PUT", "issue/PROJ-1"))
        self.assertEqual(request.call_args.kwargs["json"], {"fields": {"summary": "New"}})
        self.assertEqual(request.call_args.kwargs["params"], {"notifyUsers": "true"})
        self.assertEqual(result["updated_fields"], ["summary"])
        self.assertEqual(result["update_operations"], [])

    def test_update_operations_and_fields_together(self, request):
        update = {"labels": [{"add": "backend"}, {"remove": "old"}]}

        result = update_ticket(
            "PROJ-1", fields={"summary": "New"}, update=update, notify_users=False
        )

        self.assertEqual(
            request.call_args.kwargs["json"],
            {"fields": {"summary": "New"}, "update": update},
        )
        self.assertEqual(request.call_args.kwargs["params"], {"notifyUsers": "false"})
        self.assertEqual(result["update_operations"], ["labels"])

    def test_requires_fields_or_update(self, request):
        with self.assertRaisesRegex(ValueError, "Pass fields, update"):
            update_ticket("PROJ-1")

        request.assert_not_called()

    def test_rejects_same_field_in_both(self, request):
        with self.assertRaisesRegex(ValueError, r"\['labels'\]"):
            update_ticket(
                "PROJ-1", fields={"labels": ["a"]}, update={"labels": [{"add": "b"}]}
            )

        request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
