import unittest
from unittest.mock import patch

from jira_mcp import settings
from jira_mcp.tools.issues.create_ticket import create_ticket


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


if __name__ == "__main__":
    unittest.main()
