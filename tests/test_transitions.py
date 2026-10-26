import unittest
from unittest.mock import patch

from jira_mcp.tools.transitions.change_status import change_status

TRANSITIONS = {
    "transitions": [
        {"id": "31", "name": "Start progress", "to": {"name": "In Progress"}},
        {
            "id": "41",
            "name": "Close",
            "to": {"name": "Done"},
            "fields": {
                "resolution": {"required": True},
                "fixVersions": {"required": False},
            },
        },
    ]
}


@patch("jira_mcp.client.request")
class TransitionsTest(unittest.TestCase):
    def test_change_status_uses_target_status_name(self, request):
        request.side_effect = [TRANSITIONS, {}]

        result = change_status("PROJ-1", "in progress")

        self.assertEqual(result["transition_id"], "31")
        self.assertEqual(request.call_args.kwargs["json"], {"transition": {"id": "31"}})
        self.assertFalse(result["commented"])

    def test_change_status_sends_fields_and_comment(self, request):
        request.side_effect = [TRANSITIONS, {}]

        result = change_status(
            "PROJ-1",
            "Done",
            fields={"resolution": {"name": "Fixed"}},
            comment="Fixed in 1.2",
        )

        self.assertEqual(request.call_args.args, ("POST", "issue/PROJ-1/transitions"))
        self.assertEqual(
            request.call_args.kwargs["json"],
            {
                "transition": {"id": "41"},
                "fields": {"resolution": {"name": "Fixed"}},
                "update": {"comment": [{"add": {"body": "Fixed in 1.2"}}]},
            },
        )
        self.assertEqual(result["status"], "Done")
        self.assertEqual(result["updated_fields"], ["resolution"])
        self.assertTrue(result["commented"])

    def test_screenless_transition_posts_comment_separately(self, request):
        request.side_effect = [TRANSITIONS, {}, {"id": "900"}]

        result = change_status("PROJ-1", "In Progress", comment="Started")

        transition_call, comment_call = request.call_args_list[1:]
        self.assertEqual(transition_call.args, ("POST", "issue/PROJ-1/transitions"))
        self.assertEqual(transition_call.kwargs["json"], {"transition": {"id": "31"}})
        self.assertEqual(comment_call.args, ("POST", "issue/PROJ-1/comment"))
        self.assertEqual(comment_call.kwargs["json"], {"body": "Started"})
        self.assertEqual(comment_call.kwargs["expected"], (201,))
        self.assertTrue(result["commented"])

    def test_screen_transition_keeps_comment_in_same_request(self, request):
        request.side_effect = [TRANSITIONS, {}]

        change_status("PROJ-1", "Done", comment="Closing")

        self.assertEqual(request.call_count, 2)
        self.assertEqual(
            request.call_args.kwargs["json"]["update"],
            {"comment": [{"add": {"body": "Closing"}}]},
        )

    def test_unavailable_transition_lists_required_fields(self, request):
        request.side_effect = [TRANSITIONS]

        with self.assertRaises(ValueError) as ctx:
            change_status("PROJ-1", "Reopen")

        message = str(ctx.exception)
        self.assertIn("'to_status': 'Done'", message)
        self.assertIn("'required_fields': ['resolution']", message)
        self.assertEqual(request.call_count, 1)


if __name__ == "__main__":
    unittest.main()
