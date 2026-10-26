import unittest
from datetime import date
from unittest.mock import patch

from jira_mcp.tools.versions.create_version import create_version
from jira_mcp.tools.versions.list_versions import list_versions
from jira_mcp.tools.versions.release_version import release_version

VERSIONS = [
    {"id": "1", "name": "1.0", "released": True, "archived": False, "releaseDate": "2026-01-01"},
    {"id": "2", "name": "1.1", "released": False, "archived": False},
    {"id": "3", "name": "0.9", "released": True, "archived": True},
]


class VersionsTest(unittest.TestCase):
    @patch("jira_mcp.client.request", return_value=VERSIONS)
    def test_list_versions_filters(self, request):
        self.assertEqual([v["name"] for v in list_versions("PROJ")], ["1.0", "1.1"])
        self.assertEqual(request.call_args.args, ("GET", "project/PROJ/versions"))
        self.assertEqual([v["name"] for v in list_versions("PROJ", released=False)], ["1.1"])
        self.assertEqual(
            [v["name"] for v in list_versions("PROJ", released=True, include_archived=True)],
            ["1.0", "0.9"],
        )

    @patch("jira_mcp.client.request")
    def test_create_version(self, request):
        request.return_value = {"id": "4", "name": "2.0", "released": False}

        result = create_version("proj", "2.0", release_date="2026-12-01")

        self.assertEqual(request.call_args.args, ("POST", "version"))
        self.assertEqual(request.call_args.kwargs["expected"], (201,))
        self.assertEqual(
            request.call_args.kwargs["json"],
            {"project": "PROJ", "name": "2.0", "releaseDate": "2026-12-01"},
        )
        self.assertEqual(result["id"], "4")

    @patch("jira_mcp.client.request", return_value={"id": "5", "name": "3.0"})
    def test_create_version_all_fields(self, request):
        create_version(
            "PROJ", "3.0", description="Big", start_date="2026-11-01", release_date="2026-12-01"
        )

        self.assertEqual(
            request.call_args.kwargs["json"],
            {
                "project": "PROJ",
                "name": "3.0",
                "description": "Big",
                "startDate": "2026-11-01",
                "releaseDate": "2026-12-01",
            },
        )

    @patch("jira_mcp.client.request", return_value={"id": "2", "released": True})
    def test_release_version_with_explicit_date(self, request):
        release_version("2", release_date="2026-10-01")

        self.assertEqual(request.call_args.kwargs["json"]["releaseDate"], "2026-10-01")

    @patch("jira_mcp.client.request")
    def test_release_version_defaults_to_today(self, request):
        request.return_value = {"id": "2", "name": "1.1", "released": True}

        result = release_version("2")

        self.assertEqual(request.call_args.args, ("PUT", "version/2"))
        self.assertEqual(
            request.call_args.kwargs["json"],
            {"released": True, "releaseDate": date.today().isoformat()},
        )
        self.assertTrue(result["released"])


if __name__ == "__main__":
    unittest.main()
