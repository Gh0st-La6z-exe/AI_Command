from dataclasses import dataclass


@dataclass
class ToolResult:
    # ToolResult defines the common result contract returned by tools.
    # The Executor can validate against this base type without needing to
    # know which specific tool produced the result.
    path: str

    def describe(self):
        # Every ToolResult can provide a human-readable representation.
        # Specialized result types can override this when they have more
        # useful information to report.
        return f"Result path: {self.path}"
