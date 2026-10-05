from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class PlanStep:
    # PlanStep represents one concrete operation the Executor can perform.
    # It carries the action to execute, the input for that action, and an
    # identifier that later allows steps to reference dependencies.
    action: str
    input: str

    # Each step gets its own identifier automatically. This becomes
    # important when the Planner eventually creates dependent task graphs.
    id: str = field(default_factory=lambda: str(uuid4()))

    # Stores the IDs of steps that must be completed before this step can run.
    # The current Executor does not use dependencies yet, but the data model
    # already supports them.
    depends_on: list[str] = field(default_factory=list)


@dataclass
class Plan:
    # Plan owns the ordered collection of work produced by the Planner.
    # The Executor consumes this structure without needing to know how it
    # was constructed.
    steps: list[PlanStep]

    def add_step(self, step):
        # Keep plan construction inside Plan rather than exposing the list
        # manipulation throughout the rest of the Command Center.
        self.steps.append(step)


class Planner:
    def __init__(self, tool_registry):
        # Planner receives the tool registry as a dependency so it can resolve
        # tools without importing individual implementations directly.
        self.tool_registry = tool_registry

    def plan(self, context):
        # Planner extracts the information it needs from Context. The Task
        # contains the user's request, while Context provides the repository
        # location needed to turn that request into concrete steps.
        prompt = context.task.prompt
        repository_path = context.repository_path

        # Translate keywords from the user's request into known repository
        # targets. This is intentionally simple rule-based planning for now;
        # a future planner can replace this with model-driven reasoning.
        targets = {
            "core": "core.py",
            "filesystem": "filesystem.py",
            "planner": "planner.py",
            "executor": "executor.py",
            "agent": "agent.py",
        }

        # Planner needs a snapshot of the repository before it can determine
        # whether requested files actually exist and resolve their paths.
        inspect_tool = self.tool_registry("inspect_repository")
        repository_result = inspect_tool(repository_path)

        # Construct the Plan separately from execution. Planner decides WHAT
        # work should happen; Executor is responsible for actually performing it.
        plan = Plan(steps=[])

        # Repository inspection is always the first planned operation because
        # file-targeted steps depend on knowing what exists in the repository.
        plan.add_step(
            PlanStep(
                action="inspect_repository",
                input=repository_path,
            )
        )

        # Match request keywords against known targets and create read_file
        # steps only when the corresponding file exists in the repository.
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