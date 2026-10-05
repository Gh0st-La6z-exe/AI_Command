from command_center.tools.repository import inspect_repository
from command_center.tools.filesystem import read_file


# The registry is the controlled mapping between action names used by Plans
# and the actual tool implementations that are allowed to execute them.
# Executor resolves tools through this registry instead of reaching directly
# into individual tool modules.
TOOLS = {
    "inspect_repository": inspect_repository,
    "read_file": read_file,
}


def get_tool(action):
    # Resolve the requested action into its registered callable.
    # If the action is not registered, the KeyError propagates to Executor,
    # which converts it into a deterministic execution error.
    return TOOLS[action]