from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class PlanStep:
    action: str
    input: str
    id: str = field(default_factory=lambda: str(uuid4()))
    depends_on: list[str] = field(default_factory=list)


@dataclass
class Plan:
    steps: list[PlanStep]

    def add_step(self, step):
        self.steps.append(step)


class Planner:
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry

    def plan(self, context):
        prompt = context.task.prompt
        repository_path = context.repository_path

        # Map natural-language keywords in the task prompt
        # to the concrete files they represent.
        targets = {
            "core": "core.py",
            "filesystem": "filesystem.py",
            "planner": "planner.py",
            "executor": "executor.py",
            "agent": "agent.py",
        }

        # The Planner uses the repository inspection tool first
        # so later steps can locate files without knowing the
        # repository's internal directory structure in advance.
        inspect_tool = self.tool_registry("inspect_repository")
        repository_result = inspect_tool(repository_path)

        # Every plan begins by inspecting the repository.
        plan = Plan(steps=[])

        plan.add_step(
            PlanStep(
                action="inspect_repository",
                input=repository_path,
            )
        )

        # Translate keywords found in the user's prompt into
        # concrete file-reading steps.
        for keyword, filename in targets.items():
            if keyword in prompt.lower():
                entry = repository_result.find_file(filename)

                if entry is not None:
                    plan.add_step(
                        PlanStep(
                            action="read_file",
                            input=str(entry),
                        )
                    )

        return plan