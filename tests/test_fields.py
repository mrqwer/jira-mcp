import unittest
from unittest.mock import patch

from jira_mcp.tools.fields.get_fields import get_fields

FIELDS = [
    {
        "id": "summary",
        "name": "Summary",
        "custom": False,
        "clauseNames": ["summary"],
        "schema": {"type": "string", "system": "summary"},
    },
    {
        "id": "customfield_10010",
        "name": "Story Points",
        "custom": True,
        "clauseNames": ["cf[10010]", "Story Points"],
        "schema": {
            "type": "number",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:float",
        },
    },
    {"id": "customfield_10020", "name": "Sprint", "custom": True},
]


@patch("jira_mcp.client.request", return_value=FIELDS)
class FieldsTest(unittest.TestCase):
    def test_get_fields_normalizes_all_fields(self, request):
        result = get_fields()

        self.assertEqual(request.call_args.args, ("GET", "field"))
        self.assertEqual(len(result), 3)
        self.assertEqual(
            result[1],
            {
                "id": "customfield_10010",
                "name": "Story Points",
                "custom": True,
                "jql_names": ["cf[10010]", "Story Points"],
                "type": "number",
                "items": None,
                "custom_type": "com.atlassian.jira.plugin.system.customfieldtypes:float",
            },
        )
        self.assertIsNone(result[2]["type"])

    def test_get_fields_filters_by_name_or_id(self, request):
        self.assertEqual([f["id"] for f in get_fields("story")], ["customfield_10010"])
        self.assertEqual([f["name"] for f in get_fields("10020")], ["Sprint"])

    def test_get_fields_custom_only(self, request):
        self.assertEqual(
            [f["id"] for f in get_fields(custom_only=True)],
            ["customfield_10010", "customfield_10020"],
        )


if __name__ == "__main__":
    unittest.main()
