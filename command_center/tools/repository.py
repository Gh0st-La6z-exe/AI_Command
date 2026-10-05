from dataclasses import dataclass
from pathlib import Path

from command_center.tools.result import ToolResult


@dataclass
class RepositoryResult(ToolResult):
    # RepositoryResult captures the repository state discovered by the
    # inspection tool. It gives higher layers a structured view of what
    # actually exists instead of making them walk the filesystem themselves.
    entries: list[Path]
    count: int

    def describe(self):
        # Provide a repository-specific summary while preserving the common
        # ToolResult interface used by the execution pipeline.
        return (
            f"Repository: {self.path}\n"
            f"Entries found: {self.count}"
        )

    def find_file(self, filename):
        # RepositoryResult owns file lookup against the snapshot produced
        # by inspect_repository. Callers don't need to know how the paths
        # were discovered or where the files live in the directory tree.
        for entry in self.entries:
            if entry.name == filename:
                return entry

        return None


def inspect_repository(path):
    repository = Path(path)

    # Recursively discover the repository contents so callers can reason
    # about files regardless of which package or subdirectory contains them.
    # Generated Python cache directories are excluded because they are not
    # meaningful source artifacts for repository analysis.
    entries = [
        entry
        for entry in repository.rglob("*")
        if entry.is_file() and "__pycache__" not in entry.parts
    ]

    # Return a structured snapshot of the repository rather than exposing
    # the raw filesystem traversal to the rest of the Command Center.
    return RepositoryResult(
        path=str(repository),
        entries=entries,
        count=len(entries),
    )