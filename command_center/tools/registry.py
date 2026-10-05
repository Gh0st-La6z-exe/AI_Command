from dataclasses import dataclass
from typing import Callable

from command_center.tools.repository import inspect_repository
from command_center.tools.filesystem import read_file
from command_center.tools.filesystem import FileResult
from command_center.tools.repository import RepositoryResult
from command_center.tools.result import ToolResult


@dataclass(frozen=True)
class ToolCapability:
    name: str
    description: str
    input_type: type
    input_description: str
    result_type: type[ToolResult]
    risk_level: str
    input_validator: Callable[[object], None]

    def validate_input(self, value):
        if not isinstance(value, self.input_type):
            raise ValueError(
                f"Invalid input for '{self.name}': expected {self.input_description}."
            )

        self.input_validator(value)


def _validate_path(value):
    if not value.strip():
        raise ValueError("Path input must not be empty.")


CAPABILITIES = {
    "inspect_repository": ToolCapability(
        name="inspect_repository",
        description="List source files in a repository, excluding Git metadata and Python caches.",
        input_type=str,
        input_description="a non-empty filesystem path",
        result_type=RepositoryResult,
        risk_level="read_only",
        input_validator=_validate_path,
    ),
    "read_file": ToolCapability(
        name="read_file",
        description="Read a UTF-8 text file from the inspected repository.",
        input_type=str,
        input_description="a non-empty filesystem path",
        result_type=FileResult,
        risk_level="read_only",
        input_validator=_validate_path,
    ),
}


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


def get_capability(action):
    return CAPABILITIES[action]


def list_capabilities():
    return tuple(CAPABILITIES.values())