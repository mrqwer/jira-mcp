import unittest
from unittest.mock import MagicMock, patch

import requests

from jira_mcp import client, settings


class ClientTest(unittest.TestCase):
    def tearDown(self):
        client.session.cache_clear()

    @patch.multiple(
        settings,
        JIRA_URL="http://jira.example.com",
        JIRA_USER="user",
        JIRA_PASSWORD="secret",
    )
    def test_session_uses_basic_auth(self):
        client.session.cache_clear()
        http = client.session()

        self.assertEqual(http.auth, ("user", "secret"))
        self.assertNotIn("Authorization", http.headers)

    @patch.multiple(
        settings, JIRA_URL="http://jira.example.com", JIRA_USER="", JIRA_PASSWORD=""
    )
    def test_session_reports_missing_settings(self):
        client.session.cache_clear()

        with self.assertRaisesRegex(RuntimeError, "JIRA_USER, JIRA_PASSWORD"):
            client.session()


def _response(status_code=200, json_data=None, content=b"{}", text="", reason="OK"):
    response = MagicMock()
    response.status_code = status_code
    response.content = content
    response.text = text
    response.reason = reason
    response.json.return_value = json_data if json_data is not None else {}
    return response


@patch.object(settings, "JIRA_URL", "http://jira.example.com")
@patch("jira_mcp.client.session")
class RequestTest(unittest.TestCase):
    def test_uses_core_api_by_default(self, session):
        session.return_value.request.return_value = _response(json_data={"ok": 1})

        result = client.request("GET", "/issue/PROJ-1")

        self.assertEqual(result, {"ok": 1})
        self.assertEqual(
            session.return_value.request.call_args.args,
            ("GET", "http://jira.example.com/rest/api/2/issue/PROJ-1"),
        )

    def test_agile_api_uses_agile_base(self, session):
        session.return_value.request.return_value = _response()

        client.request("GET", "board", api="agile")

        self.assertEqual(
            session.return_value.request.call_args.args,
            ("GET", "http://jira.example.com/rest/agile/1.0/board"),
        )

    def test_rejects_unknown_api(self, session):
        with self.assertRaisesRegex(ValueError, "Unknown Jira API"):
            client.request("GET", "board", api="greenhopper")

        session.return_value.request.assert_not_called()

    def test_unexpected_status_raises_with_detail(self, session):
        session.return_value.request.return_value = _response(
            status_code=400, text='{"errors":{"resolution":"required"}}'
        )

        with self.assertRaisesRegex(RuntimeError, r"HTTP 400 for POST issue.*resolution"):
            client.request("POST", "issue", expected=(201,))

    def test_empty_body_returns_empty_dict(self, session):
        session.return_value.request.return_value = _response(status_code=204, content=b"")

        self.assertEqual(client.request("DELETE", "issueLink/1", expected=(204,)), {})

    def test_non_json_body_raises(self, session):
        response = _response(content=b"<html>")
        response.json.side_effect = requests.JSONDecodeError("bad", "<html>", 0)
        session.return_value.request.return_value = response

        with self.assertRaisesRegex(RuntimeError, "non-JSON"):
            client.request("GET", "myself")

    def test_network_error_raises(self, session):
        session.return_value.request.side_effect = requests.ConnectionError("down")

        with self.assertRaisesRegex(RuntimeError, "Jira request failed: down"):
            client.request("GET", "myself")


@patch("jira_mcp.client.request")
class PageTest(unittest.TestCase):
    def test_core_format_with_more_pages(self, request):
        request.return_value = {
            "startAt": 0,
            "maxResults": 2,
            "total": 5,
            "comments": [{"id": "1"}, {"id": "2"}],
        }

        result = client.page("issue/PROJ-1/comment", "comments", max_results=2)

        self.assertEqual(result["items"], [{"id": "1"}, {"id": "2"}])
        self.assertEqual(result["total"], 5)
        self.assertEqual(result["next_start_at"], 2)
        self.assertEqual(
            request.call_args.kwargs["params"], {"startAt": 0, "maxResults": 2}
        )
        self.assertEqual(request.call_args.kwargs["api"], "api")

    def test_core_format_last_page(self, request):
        request.return_value = {"startAt": 4, "total": 5, "comments": [{"id": "5"}]}

        result = client.page("issue/PROJ-1/comment", "comments", start_at=4)

        self.assertIsNone(result["next_start_at"])

    def test_agile_format_uses_is_last(self, request):
        request.return_value = {"startAt": 0, "isLast": False, "values": [{"id": 7}]}

        result = client.page(
            "board/1/sprint", "values", params={"state": "active"}, api="agile"
        )

        self.assertEqual(result["items"], [{"id": 7}])
        self.assertIsNone(result["total"])
        self.assertEqual(result["next_start_at"], 1)
        self.assertEqual(request.call_args.kwargs["api"], "agile")
        self.assertEqual(request.call_args.kwargs["params"]["state"], "active")

    def test_empty_page_is_last(self, request):
        request.return_value = {"startAt": 0, "isLast": False, "values": []}

        self.assertIsNone(client.page("board", "values", api="agile")["next_start_at"])

    def test_pages_locally_when_server_ignores_paging(self, request):
        everything = [{"id": str(i)} for i in range(5)]
        request.return_value = {"startAt": 0, "maxResults": 5, "total": 5, "worklogs": everything}

        first = client.page("issue/PROJ-1/worklog", "worklogs", max_results=2)
        second = client.page(
            "issue/PROJ-1/worklog", "worklogs", start_at=4, max_results=2
        )

        self.assertEqual([w["id"] for w in first["items"]], ["0", "1"])
        self.assertEqual(first["next_start_at"], 2)
        self.assertEqual([w["id"] for w in second["items"]], ["4"])
        self.assertEqual(second["start_at"], 4)
        self.assertIsNone(second["next_start_at"])

    def test_page_size_is_capped_by_settings(self, request):
        request.return_value = {"values": []}

        with patch.object(settings, "JIRA_MAX_RESULTS", 10):
            result = client.page("board", "values", max_results=500, api="agile")

        self.assertEqual(result["max_results"], 10)
        self.assertEqual(request.call_args.kwargs["params"]["maxResults"], 10)


if __name__ == "__main__":
    unittest.main()
