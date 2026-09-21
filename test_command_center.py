from pathlib import Path

from command_center.task import Task, TaskStatus
from command_center.context import Context
from command_center.agents.agent import Agent
from command_center.events.bus import EventBus
from command_center.planner.planner import Planner, Plan, PlanStep
from command_center.tools.registry import get_tool
from command_center.execution.executor import Executor


# --------------------------------------------------
# CORE TARGET TEST
# --------------------------------------------------

task = Task("Analyze the core")

goal = "Verify task and context wiring."

context = Context(
    task,
    goal,
    r"C:\Dev\AI_Command"
)

assert context.task is task
assert context.goal == goal

planner = Planner(get_tool)

plan = planner.plan(context)

assert isinstance(plan, Plan)
assert len(plan.steps) == 2

assert isinstance(plan.steps[0], PlanStep)
assert plan.steps[0].action == "inspect_repository"
assert plan.steps[0].input == r"C:\Dev\AI_Command"

assert isinstance(plan.steps[1], PlanStep)
assert plan.steps[1].action == "read_file"
assert plan.steps[1].input == r"C:\Dev\AI_Command\command_center\core.py"

assert Path(plan.steps[1].input).name == "core.py"


# --------------------------------------------------
# EXECUTION TEST
# --------------------------------------------------

bus = EventBus()
agent = Agent("Test Agent", bus)

executor = Executor(
    agent,
    get_tool,
)

results = executor.execute_plan(plan, context)

assert len(results) == 2
assert task.status == TaskStatus.COMPLETED
assert len(task.results) == 2

# EXECUTOR VALIDATION TEST
invalid_step = PlanStep(
    action="",
    input=r"C:\Dev\AI_Command"
)

try:
    executor.execute_step(invalid_step, context)
    raise AssertionError("Executor accepted an invalid plan step.")
except ValueError as error:
    assert str(error) == "Plan step is missing an action."

#Unknown action test
unknown_step = PlanStep(
    action="Does not exist.",
    input=r"C:\Dev\AI_Command"
)

try:
    executor.execute_step(unknown_step, context)
    raise AssertionError("Executor accepted an unknown action.")
except ValueError as error:
    assert str(error) == "Unknown Action: Does not exist."

# --------------------------------------------------
# RESULT TEST
# --------------------------------------------------

repository_result = task.results[0]
file_result = task.results[1]

core_file = repository_result.find_file("core.py")

assert core_file is not None
assert core_file.name == "core.py"
assert core_file == Path(
    r"C:\Dev\AI_Command\command_center\core.py"
)

missing_file = repository_result.find_file("does_not_exist.py")

assert missing_file is None

assert Path(repository_result.path).resolve() == Path(
    r"C:\Dev\AI_Command"
).resolve()

assert Path(file_result.path).resolve() == Path(
    r"C:\Dev\AI_Command\command_center\core.py"
).resolve()

assert isinstance(repository_result.entries, list)
assert repository_result.count == len(repository_result.entries)

assert isinstance(file_result.content, str)
assert file_result.size == len(file_result.content)
assert "CommandCenter" in file_result.content


# --------------------------------------------------
# FILESYSTEM TARGET TEST
# --------------------------------------------------

filesystem_task = Task("Analyze the filesystem tool")

filesystem_context = Context(
    filesystem_task,
    "Understand the filesystem tool.",
    r"C:\Dev\AI_Command"
)

filesystem_plan = planner.plan(filesystem_context)

assert isinstance(filesystem_plan, Plan)
assert len(filesystem_plan.steps) == 2

assert isinstance(filesystem_plan.steps[0], PlanStep)
assert filesystem_plan.steps[0].action == "inspect_repository"

assert isinstance(filesystem_plan.steps[1], PlanStep)
assert filesystem_plan.steps[1].action == "read_file"
assert Path(filesystem_plan.steps[1].input).name == "filesystem.py"

print("TEST PASSED")