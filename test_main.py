import tempfile
import unittest
from pathlib import Path
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
    def test_add_attachment_sends_multipart_with_no_check_token(self, request):
        request.return_value = [{"id": "10001", "filename": "screenshot.png"}]

        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "screenshot.png"
            file_path.write_bytes(b"fake-png-bytes")

            result = main.add_attachment("PROJ-1", str(file_path))

        self.assertEqual(result, {"id": "10001", "filename": "screenshot.png"})
        call_kwargs = request.call_args.kwargs
        self.assertEqual(
            call_kwargs["headers"], {"X-Atlassian-Token": "no-check"}
        )
        self.assertEqual(call_kwargs["files"]["file"][0], "screenshot.png")
        self.assertEqual(request.call_args.args, ("POST", "issue/PROJ-1/attachments"))

    def test_add_attachment_rejects_missing_file(self):
        with self.assertRaises(ValueError):
            main.add_attachment("PROJ-1", "no-such-file.png")

    @patch("main._client")
    @patch("main._request")
    def test_download_attachment_fetches_content_url_and_saves_file(
        self, request, client
    ):
        request.return_value = {
            "filename": "screenshot.png",
            "mimeType": "image/png",
            "size": 4,
            "content": "http://jira.example.com/secure/attachment/15152/screenshot.png",
        }
        client.return_value.get.return_value.status_code = 200
        client.return_value.get.return_value.content = b"fake"

        with tempfile.TemporaryDirectory() as tmp_dir:
            save_path = Path(tmp_dir) / "out.png"

            result = main.download_attachment("15152", str(save_path))

            self.assertEqual(save_path.read_bytes(), b"fake")

        self.assertEqual(request.call_args.args, ("GET", "attachment/15152"))
        client.return_value.get.assert_called_once_with(
            "http://jira.example.com/secure/attachment/15152/screenshot.png",
            timeout=main.JIRA_TIMEOUT,
        )
        self.assertEqual(result["filename"], "screenshot.png")
        self.assertEqual(result["size"], 4)

    @patch("main._request")
    def test_delete_attachment_calls_expected_endpoint(self, request):
        request.return_value = {}

        result = main.delete_attachment("15152")

        self.assertEqual(request.call_args.args, ("DELETE", "attachment/15152"))
        self.assertEqual(request.call_args.kwargs["expected"], (204,))
        self.assertEqual(result, {"deleted_attachment_id": "15152"})

    @patch("main._request")
    def test_delete_link_calls_expected_endpoint(self, request):
        request.return_value = {}

        result = main.delete_link("10050")

        self.assertEqual(request.call_args.args, ("DELETE", "issueLink/10050"))
        self.assertEqual(request.call_args.kwargs["expected"], (204,))
        self.assertEqual(result, {"deleted": True, "link_id": "10050"})

    @patch("main._request")
    def test_get_project_statuses_calls_expected_endpoint(self, request):
        request.return_value = [{"name": "Задача", "statuses": []}]

        result = main.get_project_statuses("PROJ")

        self.assertEqual(request.call_args.args, ("GET", "project/PROJ/statuses"))
        self.assertEqual(result, [{"name": "Задача", "statuses": []}])

    @patch("main._request")
    def test_get_all_statuses_calls_expected_endpoint(self, request):
        request.return_value = [{"id": "10201", "name": "Готово"}]

        result = main.get_all_statuses()

        self.assertEqual(request.call_args.args, ("GET", "status"))
        self.assertEqual(result, [{"id": "10201", "name": "Готово"}])

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
