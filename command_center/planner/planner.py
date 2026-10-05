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
    supported: bool = True
    message: str | None = None

    def add_step(self, step):
        # Keep plan construction inside Plan rather than exposing the list
        # manipulation throughout the rest of the Command Center.
        self.steps.append(step)


class Planner:
    def __init__(self, capability_registry):
        self.capability_registry = capability_registry

    def plan(self, context, repository_result):
        # Planning consumes observed repository state; it never invokes tools.
        prompt = context.task.prompt

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

        matched_targets = [
            (keyword, filename)
            for keyword, filename in targets.items()
            if keyword in prompt.lower()
        ]

        if not matched_targets:
            return Plan(
                steps=[],
                supported=False,
                message="No supported source-file target was identified in the request.",
            )

        try:
            capability = self.capability_registry("read_file")
        except KeyError:
            return Plan(
                steps=[],
                supported=False,
                message="This request needs the unavailable 'read_file' capability.",
            )

        if capability.risk_level != "read_only":
            return Plan(
                steps=[],
                supported=False,
                message="The requested capability is outside the planner's read-only policy.",
            )

        steps = []
        unavailable_targets = []

        # Match request keywords against known targets and create read_file
        # steps only when the corresponding file exists in the repository.
        for keyword, filename in matched_targets:
            entry = repository_result.find_file(filename)

            if entry is None:
                unavailable_targets.append(filename)
                continue

            file_path = str(entry)
            try:
                capability.validate_input(file_path)
            except (TypeError, ValueError):
                unavailable_targets.append(filename)
                continue

            steps.append(
                PlanStep(
                    action=capability.name,
                    input=file_path,
                )
            )

        if not steps:
            missing_files = ", ".join(unavailable_targets)
            return Plan(
                steps=[],
                supported=False,
                message=f"No readable requested target was found: {missing_files}.",
            )

        message = None
        if unavailable_targets:
            message = "Some requested targets were unavailable: " + ", ".join(
                unavailable_targets
            ) + "."

        return Plan(steps=steps, message=message)