from dataclasses import dataclass
from pathlib import Path

from command_center.tools.result import ToolResult


@dataclass
class FileResult(ToolResult):
    # FileResult extends the common ToolResult contract with information
    # specific to a filesystem read. The Executor can still treat it as a
    # ToolResult while filesystem-aware code can access the actual contents.
    content: str
    size: int

    def describe(self):
        # Files need a more useful report than the generic ToolResult.
        # Overriding describe() keeps presentation specific to the result
        # type instead of forcing the base class to understand every tool.
        return (
            f"File: {self.path}\n"
            f"Size: {self.size}"
        )


def read_file(path):
    # Convert the incoming path into a Path object so the tool operates
    # through Python's filesystem abstraction rather than raw string paths.
    file = Path(path)

    # Read the file as UTF-8 text and keep the complete contents in the
    # returned result so later components can inspect what was actually read.
    content = file.read_text(encoding="utf-8")

    # Return a structured FileResult instead of a raw string. This gives
    # the execution pipeline both the data and metadata associated with
    # the filesystem operation.
    return FileResult(
        path=str(file),
        content=content,
        size=len(content),
    )