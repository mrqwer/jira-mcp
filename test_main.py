import unittest
from unittest.mock import patch

import main


class JiraToolsTest(unittest.TestCase):
    def test_client_uses_hardcoded_basic_auth(self):
        main._client.cache_clear()
        client = main._client()

        self.assertEqual(client.auth, (main.JIRA_USER, main.JIRA_PASSWORD))
        self.assertNotIn("Authorization", client.headers)

    @patch("main._request")
    def test_create_ticket_keeps_core_fields_authoritative(self, request):
        request.return_value = {"key": "PROJ-1"}

        result = main.create_ticket(
            "proj",
            "Useful title",
            "Useful description",
            additional_fields={"summary": "wrong", "customfield_10000": 3},
        )

        fields = request.call_args.kwargs["json"]["fields"]
        self.assertEqual(fields["summary"], "Useful title")
        self.assertEqual(fields["customfield_10000"], 3)
        self.assertEqual(result["browse_url"], f"{main.JIRA_URL}/browse/PROJ-1")

    @patch("main._request")
    def test_change_status_uses_target_status_name(self, request):
        request.side_effect = [
            {
                "transitions": [
                    {"id": "31", "name": "Start progress", "to": {"name": "In Progress"}}
                ]
            },
            {},
        ]

        result = main.change_status("PROJ-1", "in progress")

        self.assertEqual(result["transition_id"], "31")
        self.assertEqual(request.call_args.kwargs["json"], {"transition": {"id": "31"}})


if __name__ == "__main__":
    unittest.main()
