from dataclasses import dataclass

@dataclass
class ToolResult:
    path: str

    def describe(self):
        return f"Result path: {self.path}"