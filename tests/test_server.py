import asyncio
import unittest

from jira_mcp.server import mcp

EXPECTED_TOOLS = {
    "get_myself",
    "find_users",
    "find_assignable_users",
    "get_my_permissions",
    "get_priorities",
    "get_resolutions",
    "get_issue_types",
    "get_issue_history",
    "get_comments",
    "get_worklogs",
    "list_projects",
    "get_project_issue_types",
    "get_create_fields",
    "get_project_statuses",
    "get_all_statuses",
    "get_fields",
    "get_edit_fields",
    "get_ticket",
    "search_tickets",
    "create_ticket",
    "update_ticket",
    "assign_ticket",
    "add_comment",
    "delete_comment",
    "add_attachment",
    "delete_attachment",
    "download_attachment",
    "list_transitions",
    "change_status",
    "add_worklog",
    "get_link_types",
    "link_tickets",
    "delete_link",
    "get_remote_links",
    "add_remote_link",
    "delete_remote_link",
    "notify_issue",
    "update_worklog",
    "delete_worklog",
    "list_boards",
    "get_board_config",
    "get_board_issues",
    "get_backlog",
    "rank_issues",
    "list_sprints",
    "get_sprint_issues",
    "move_to_sprint",
    "move_to_backlog",
    "create_sprint",
    "start_sprint",
    "close_sprint",
    "list_epics",
    "get_epic_issues",
    "add_to_epic",
    "list_versions",
    "create_version",
    "release_version",
    "list_components",
    "create_component",
    "get_watchers",
    "add_watcher",
    "remove_watcher",
    "list_favourite_filters",
    "run_filter",
}


class ServerTest(unittest.TestCase):
    def test_every_tool_is_registered(self):
        tools = asyncio.run(mcp.list_tools())

        self.assertEqual({tool.name for tool in tools}, EXPECTED_TOOLS)


if __name__ == "__main__":
    unittest.main()
