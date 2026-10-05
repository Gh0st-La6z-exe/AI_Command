from command_center.agents.agent import Agent
from command_center.context import Context
from command_center.events.bus import EventBus
from command_center.execution.executor import Executor
from command_center.planner.planner import PlanStep, Planner
from command_center.task import Task, TaskStatus
from command_center.tools.registry import get_capability, get_tool


class CommandCenter:
    def __init__(self):
        # CommandCenter is the composition root for the system.
        # It creates the major components and wires their dependencies
        # together. The individual components stay focused on their own
        # responsibilities instead of constructing each other internally.
        self.bus = EventBus()
        self.planner = Planner(get_capability)

        self.agent = Agent(
            "Command Center",
            self.bus,
        )

        self.executor = Executor(
            self.agent,
            get_tool,
            get_capability,
        )

    def run(self, prompt, goal, repository_path):
        # A run creates the Task and Context that carry this specific piece
        # of work through the planning and execution pipeline.
        task = Task(prompt)

        context = Context(
            task,
            goal,
            repository_path
        )

        task.status = TaskStatus.RUNNING

        try:
            repository_result = self.executor.execute_step(
                PlanStep(
                    action="inspect_repository",
                    input=repository_path,
                ),
                context,
            )
            plan = self.planner.plan(context, repository_result)
            if not plan.supported:
                task.message = plan.message
                task.status = TaskStatus.UNSUPPORTED
                return task

            task.message = plan.message
            self.executor.execute_plan(plan, context)
            task.status = TaskStatus.COMPLETED
        except Exception:
            task.status = TaskStatus.FAILED
            raise

        return task
        