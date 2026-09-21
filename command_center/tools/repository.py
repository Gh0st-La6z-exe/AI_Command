from dataclasses import dataclass
from pathlib import Path

from command_center.tools.result import ToolResult


@dataclass
class RepositoryResult(ToolResult):
    entries: list[Path]
    count: int

    def describe(self):
        return (
            f"Repository: {self.path}\n"
            f"Entries found: {self.count}"
        )

    def find_file(self, filename):
        for entry in self.entries:
            if entry.name == filename:
                return entry
        
        return None

def inspect_repository(path):
    repository = Path(path)

    # Recursively discover the repository contents so callers can reason
    # about files regardless of which package or subdirectory contains them.
    entries = [
        entry
        for entry in repository.rglob("*")
        if entry.is_file() and "__pycache__" not in entry.parts
    ]

    return RepositoryResult(
        path=str(repository),
        entries=entries,
        count=len(entries),
    )