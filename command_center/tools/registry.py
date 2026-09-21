from command_center.tools.repository import inspect_repository
from command_center.tools.filesystem import read_file


TOOLS = {
    "inspect_repository": inspect_repository,
    "read_file": read_file,
}


def get_tool(action):
    return TOOLS[action]