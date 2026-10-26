import unittest
from unittest.mock import patch

from jira_mcp import settings
from jira_mcp.tools.issues.create_ticket import create_ticket
from jira_mcp.tools.issues.get_edit_fields import get_edit_fields
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
