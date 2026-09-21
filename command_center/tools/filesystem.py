from dataclasses import dataclass
from pathlib import Path

from command_center.tools.result import ToolResult


@dataclass
class FileResult(ToolResult):
    content: str
    size: int

    def describe(self):
        return (
            f"File: {self.path}\n"
            f"Size: {self.size}"
        )


def read_file(path):
    file = Path(path)

    content = file.read_text(encoding="utf-8")

    return FileResult(
        path=str(file),
        content=content,
        size=len(content),
    )