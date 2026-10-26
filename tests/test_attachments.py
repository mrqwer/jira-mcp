import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests

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

    @patch("jira_mcp.client.request", return_value={"filename": "a.png"})
    def test_download_attachment_without_content_url(self, request):
        with self.assertRaisesRegex(RuntimeError, "has no content URL"):
            download_attachment("15152")

    @patch("jira_mcp.client.session")
    @patch("jira_mcp.client.request")
    def test_download_attachment_http_error(self, request, session):
        request.return_value = {"filename": "a.png", "content": "http://jira/a.png"}
        response = session.return_value.get.return_value
        response.status_code = 403
        response.text = "Forbidden"

        with self.assertRaisesRegex(RuntimeError, "HTTP 403 downloading attachment 15152: Forbidden"):
            download_attachment("15152", "unused.png")

    @patch("jira_mcp.client.session")
    @patch("jira_mcp.client.request")
    def test_download_attachment_network_error(self, request, session):
        request.return_value = {"filename": "a.png", "content": "http://jira/a.png"}
        session.return_value.get.side_effect = requests.ConnectionError("down")

        with self.assertRaisesRegex(RuntimeError, "download failed: down"):
            download_attachment("15152", "unused.png")

    @patch("jira_mcp.client.session")
    @patch("jira_mcp.client.request")
    def test_download_attachment_defaults_to_original_filename(self, request, session):
        request.return_value = {"filename": "report.pdf", "content": "http://jira/report.pdf"}
        session.return_value.get.return_value.status_code = 200
        session.return_value.get.return_value.content = b"pdf"

        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                result = download_attachment("15152")
                self.assertEqual(Path("report.pdf").read_bytes(), b"pdf")
            finally:
                os.chdir(cwd)

        self.assertTrue(result["saved_to"].endswith("report.pdf"))

    @patch("jira_mcp.client.request")
    def test_delete_attachment_calls_expected_endpoint(self, request):
        request.return_value = {}

        result = delete_attachment("15152")

        self.assertEqual(request.call_args.args, ("DELETE", "attachment/15152"))
        self.assertEqual(request.call_args.kwargs["expected"], (204,))
        self.assertEqual(result, {"deleted_attachment_id": "15152"})


if __name__ == "__main__":
    unittest.main()
