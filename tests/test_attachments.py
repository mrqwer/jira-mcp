import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jira_mcp import settings
from jira_mcp.tools.attachments.add_attachment import add_attachment
from jira_mcp.tools.attachments.delete_attachment import delete_attachment
from jira_mcp.tools.attachments.download_attachment import download_attachment


class AttachmentsTest(unittest.TestCase):
    @patch("jira_mcp.client.request")
    def test_add_attachment_sends_multipart_with_no_check_token(self, request):
        request.return_value = [{"id": "10001", "filename": "screenshot.png"}]

        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "screenshot.png"
            file_path.write_bytes(b"fake-png-bytes")

            result = add_attachment("PROJ-1", str(file_path))

        self.assertEqual(result, {"id": "10001", "filename": "screenshot.png"})
        call_kwargs = request.call_args.kwargs
        self.assertEqual(
            call_kwargs["headers"], {"X-Atlassian-Token": "no-check"}
        )
        self.assertEqual(call_kwargs["files"]["file"][0], "screenshot.png")
        self.assertEqual(request.call_args.args, ("POST", "issue/PROJ-1/attachments"))

    def test_add_attachment_rejects_missing_file(self):
        with self.assertRaises(ValueError):
            add_attachment("PROJ-1", "no-such-file.png")

    @patch("jira_mcp.client.session")
    @patch("jira_mcp.client.request")
    def test_download_attachment_fetches_content_url_and_saves_file(
        self, request, session
    ):
        request.return_value = {
            "filename": "screenshot.png",
            "mimeType": "image/png",
            "size": 4,
            "content": "http://jira.example.com/secure/attachment/15152/screenshot.png",
        }
        session.return_value.get.return_value.status_code = 200
        session.return_value.get.return_value.content = b"fake"

        with tempfile.TemporaryDirectory() as tmp_dir:
            save_path = Path(tmp_dir) / "out.png"

            result = download_attachment("15152", str(save_path))

            self.assertEqual(save_path.read_bytes(), b"fake")

        self.assertEqual(request.call_args.args, ("GET", "attachment/15152"))
        session.return_value.get.assert_called_once_with(
            "http://jira.example.com/secure/attachment/15152/screenshot.png",
            timeout=settings.JIRA_TIMEOUT,
        )
        self.assertEqual(result["filename"], "screenshot.png")
        self.assertEqual(result["size"], 4)

    @patch("jira_mcp.client.request")
    def test_delete_attachment_calls_expected_endpoint(self, request):
        request.return_value = {}

        result = delete_attachment("15152")

        self.assertEqual(request.call_args.args, ("DELETE", "attachment/15152"))
        self.assertEqual(request.call_args.kwargs["expected"], (204,))
        self.assertEqual(result, {"deleted_attachment_id": "15152"})


if __name__ == "__main__":
    unittest.main()
