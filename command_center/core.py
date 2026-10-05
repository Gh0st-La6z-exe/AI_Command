from command_center.agents.agent import Agent
from command_center.context import Context
from command_center.events.bus import EventBus
from command_center.execution.executor import Executor
from command_center.planner.planner import Planner
from command_center.task import Task
from command_center.tools.registry import get_tool


class CommandCenter:
    def __init__(self):
        # CommandCenter is the composition root for the system.
        # It creates the major components and wires their dependencies
        # together. The individual components stay focused on their own
        # responsibilities instead of constructing each other internally.
        self.bus = EventBus()
        self.planner = Planner(get_tool)

        self.agent = Agent(
            "Command Center",
            self.bus,
        )

        self.executor = Executor(
            self.agent,
            get_tool,
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

        # Planner turns the task context into an executable Plan.
        # CommandCenter coordinates this transition but does not perform
        # the planning itself.
        plan = self.planner.plan(context)

        # Executor takes ownership of actually running the Plan.
        # This keeps orchestration here while deterministic execution rules
        # remain inside the execution layer.
        self.executor.execute_plan(plan, context)

        return task
        