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

        # Construct the Plan separately from execution. Planner decides WHAT
        # work should happen; Executor is responsible for actually performing it.
        plan = Plan(steps=[])

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