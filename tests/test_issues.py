import unittest
from unittest.mock import patch

from jira_mcp import settings
from jira_mcp.tools.issues.assign_ticket import assign_ticket
from jira_mcp.tools.issues.create_ticket import create_ticket
from jira_mcp.tools.issues.get_ticket import get_ticket
from jira_mcp.tools.issues.search_tickets import search_tickets
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
    def test_create_ticket_optional_fields(self, request):
        request.return_value = {"key": "PROJ-2"}

        create_ticket(
            "PROJ",
            "Sub task",
            "Details",
            issue_type="Sub-task",
            assignee_username="ivan",
            parent_key="PROJ-1",
            labels=[],
            priority="High",
        )

        self.assertEqual(request.call_args.args, ("POST", "issue"))
        self.assertEqual(request.call_args.kwargs["expected"], (201,))
        fields = request.call_args.kwargs["json"]["fields"]
        self.assertEqual(fields["issuetype"], {"name": "Sub-task"})
        self.assertEqual(fields["assignee"], {"name": "ivan"})
        self.assertEqual(fields["parent"], {"key": "PROJ-1"})
        self.assertEqual(fields["labels"], [])
        self.assertEqual(fields["priority"], {"name": "High"})

    @patch("jira_mcp.client.request", return_value={"key": "PROJ-3"})
    def test_create_ticket_omits_unset_optional_fields(self, request):
        create_ticket("PROJ", "Title", "Body")

        fields = request.call_args.kwargs["json"]["fields"]
        self.assertEqual(sorted(fields), ["description", "issuetype", "project", "summary"])

    @patch("jira_mcp.client.request")
    def test_get_ticket_trims_comments_and_adds_url(self, request):
        request.return_value = {
            "key": "PROJ-1",
            "fields": {"comment": {"comments": [{"id": str(i)} for i in range(5)]}},
        }

        result = get_ticket("PROJ-1", comment_limit=2)

        self.assertEqual(request.call_args.args, ("GET", "issue/PROJ-1"))
        params = request.call_args.kwargs["params"]
        self.assertIn("summary", params["fields"].split(","))
        self.assertEqual(params["expand"], "names,schema")
        self.assertEqual([c["id"] for c in result["fields"]["comment"]["comments"]], ["3", "4"])
        self.assertEqual(result["browse_url"], f"{settings.JIRA_URL}/browse/PROJ-1")

    @patch("jira_mcp.client.request")
    def test_get_ticket_custom_fields_and_no_comments(self, request):
        request.return_value = {
            "key": "PROJ-1",
            "fields": {"comment": {"comments": [{"id": "1"}]}},
        }

        result = get_ticket("PROJ-1", fields=["summary", "comment"], comment_limit=0)

        self.assertEqual(request.call_args.kwargs["params"]["fields"], "summary,comment")
        self.assertEqual(result["fields"]["comment"]["comments"], [])

    @patch("jira_mcp.client.request")
    def test_search_tickets(self, request):
        request.return_value = {"total": 1, "issues": [{"key": "PROJ-1"}]}

        result = search_tickets("project = PROJ", max_results=5, start_at=-3)

        self.assertEqual(request.call_args.args, ("GET", "search"))
        params = request.call_args.kwargs["params"]
        self.assertEqual(params["jql"], "project = PROJ")
        self.assertEqual(params["startAt"], 0)
        self.assertEqual(params["maxResults"], 5)
        self.assertEqual(result["issues"][0]["browse_url"], f"{settings.JIRA_URL}/browse/PROJ-1")

    @patch("jira_mcp.client.request", return_value={})
    def test_assign_ticket_and_unassign(self, request):
        self.assertEqual(assign_ticket("PROJ-1", "ivan"), {"key": "PROJ-1", "assignee": "ivan"})
        self.assertEqual(request.call_args.args, ("PUT", "issue/PROJ-1/assignee"))
        self.assertEqual(request.call_args.kwargs["json"], {"name": "ivan"})
        self.assertEqual(request.call_args.kwargs["expected"], (204,))

        assign_ticket("PROJ-1", None)
        self.assertEqual(request.call_args.kwargs["json"], {"name": None})

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


LOCALIZED_STATUSES = [
    {"id": "1", "name": "Сделать"},
    {"id": "3", "name": "В работе"},
]


def _history_responses(changelog):
    def respond(method, path, **kwargs):
        return LOCALIZED_STATUSES if path == "status" else changelog

    return respond


@patch("jira_mcp.client.request", side_effect=_history_responses(CHANGELOG))
class IssueHistoryTest(unittest.TestCase):
    def test_returns_all_changes_oldest_first(self, request):
        result = get_issue_history("PROJ-1")

        self.assertEqual(
            request.call_args_list[0].kwargs["params"],
            {"expand": "changelog", "fields": "summary"},
        )
        self.assertEqual([c["id"] for c in result["changes"]], ["1", "2", "3"])
        self.assertEqual(
            result["changes"][0]["items"][1],
            {"field": "assignee", "from": None, "to": "Ivan", "from_id": None, "to_id": "ivan"},
        )
        self.assertEqual(result["changes"][0]["author_username"], "ivan")
        self.assertTrue(result["history_complete"])

    def test_status_names_are_shown_as_jira_displays_them_now(self, request):
        first = get_issue_history("PROJ-1")["changes"][0]["items"][0]

        self.assertEqual(
            first,
            {"field": "status", "from": "Сделать", "to": "В работе", "from_id": "1", "to_id": "3"},
        )

    def test_unknown_status_id_keeps_changelog_name(self, request):
        last = get_issue_history("PROJ-1", field="status")["changes"][-1]["items"][0]

        self.assertEqual((last["from"], last["to"]), ("In Progress", "Done"))

    def test_filters_by_field_and_limits_to_latest(self, request):
        result = get_issue_history("PROJ-1", field="Status", limit=1)

        self.assertEqual(result["matching_changes"], 2)
        self.assertEqual(len(result["changes"]), 1)
        self.assertEqual(result["changes"][0]["id"], "3")

    def test_skips_status_lookup_without_status_changes(self, request):
        request.side_effect = _history_responses(
            {"key": "PROJ-1", "changelog": {"histories": [CHANGELOG["changelog"]["histories"][1]]}}
        )

        get_issue_history("PROJ-1")

        self.assertEqual(request.call_count, 1)

    def test_reports_truncated_history(self, request):
        request.side_effect = _history_responses(
            {
                "key": "PROJ-1",
                "changelog": {"total": 250, "histories": CHANGELOG["changelog"]["histories"]},
            }
        )

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
