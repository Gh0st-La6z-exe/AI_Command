from command_center.events.bus import EventBus
from command_center.agents.agent import Agent
from command_center.task import Task
from command_center.context import Context
from command_center.planner.planner import Planner
from command_center.tools.registry import get_tool
from command_center.execution.executor import Executor


class CommandCenter:
    def __init__(self):
        
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
        task = Task(prompt)
        context = Context(
            task,
            goal,
            r"C:\Dev\AI_Command"
        )

        plan = self.planner.plan(context)

        self.executor.execute_plan(plan, context)

        return task

        